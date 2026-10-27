"""Local-only SQLite task API. Run with --help."""
import argparse
import json
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs

class Store:
    def __init__(self,path):
        self.path=str(path)
        with closing(self.connect()) as db,db:
            db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)))')
    def connect(self):
        db=sqlite3.connect(self.path,timeout=5); db.row_factory=sqlite3.Row; return db
    @staticmethod
    def task(row): return {'id':row['id'],'title':row['title'],'done':bool(row['done'])}
    def create(self,title):
        if not isinstance(title,str) or not title.strip() or len(title.strip())>200: raise ValueError('invalid title')
        with closing(self.connect()) as db,db:
            cursor=db.execute('INSERT INTO tasks(title) VALUES (?)',(title.strip(),))
            return self.task(db.execute('SELECT * FROM tasks WHERE id=?',(cursor.lastrowid,)).fetchone())
    def list(self,limit=50,offset=0):
        if not 1<=limit<=100 or not 0<=offset<=9223372036854775807: raise ValueError('invalid pagination')
        with closing(self.connect()) as db:
            return [self.task(row) for row in db.execute('SELECT * FROM tasks ORDER BY id LIMIT ? OFFSET ?',(limit,offset))]
    def complete(self,task_id,done):
        if type(done) is not bool: raise ValueError('done must be boolean')
        if not 1<=task_id<=9223372036854775807: raise ValueError('invalid id')
        with closing(self.connect()) as db,db:
            cursor=db.execute('UPDATE tasks SET done=? WHERE id=?',(int(done),task_id))
            if cursor.rowcount==0: raise KeyError(task_id)
            return self.task(db.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone())

def handler(store):
    class Handler(BaseHTTPRequestHandler):
        server_version='TaskPortfolio/0.1'
        def log_message(self,*args): pass
        def reply(self,status,data):
            body=json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        def body(self):
            if self.headers.get('Transfer-Encoding'): raise ValueError('unsupported encoding')
            if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json': raise ValueError('JSON required')
            length=int(self.headers.get('Content-Length','0'))
            if not 1<=length<=8192: raise ValueError('body too large or empty')
            self.connection.settimeout(5)
            value=json.loads(self.rfile.read(length))
            if not isinstance(value,dict): raise ValueError('object required')
            return value
        def dispatch(self,method):
            try:
                path=urlsplit(self.path).path
                if method=='GET' and path=='/health': return self.reply(200,{'status':'ok'})
                if method=='GET' and path=='/tasks':
                    query=parse_qs(urlsplit(self.path).query)
                    return self.reply(200,store.list(int(query.get('limit',['50'])[0]),int(query.get('offset',['0'])[0])))
                if method=='POST' and path=='/tasks':
                    data=self.body()
                    if set(data)!={'title'}: raise ValueError('title required')
                    return self.reply(201,store.create(data['title']))
                if method=='PATCH' and path.startswith('/tasks/') and path[7:].isdigit():
                    data=self.body()
                    if set(data)!={'done'}: raise ValueError('done required')
                    return self.reply(200,store.complete(int(path[7:]),data['done']))
                self.reply(404,{'error':'route not found'})
            except (ValueError,UnicodeError,OverflowError,TimeoutError): self.reply(400,{'error':'invalid request'})
            except KeyError: self.reply(404,{'error':'task not found'})
            except sqlite3.Error: self.reply(503,{'error':'storage unavailable'})
        def do_GET(self): self.dispatch('GET')
        def do_POST(self): self.dispatch('POST')
        def do_PATCH(self): self.dispatch('PATCH')
    return Handler

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',default='tasks.db'); parser.add_argument('--port',type=int,default=8080)
    args=parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler(Store(args.db))) as server:
        print(f'Local task API: http://127.0.0.1:{server.server_port}',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass

if __name__=='__main__': main()
