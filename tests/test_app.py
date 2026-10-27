import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory
from pathlib import Path
from task_api import Store,handler

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(); self.store=Store(Path(self.temp.name)/'tasks.db')
    def tearDown(self): self.temp.cleanup()
    def test_persistence_sql(self):
        task=self.store.create("'); DROP TABLE tasks; --")
        self.assertEqual(Store(self.store.path).list()[0],task)
        self.assertTrue(self.store.complete(task['id'],True)['done'])
    def test_validation_pagination(self):
        for title in ['', ' '*3,'x'*201,None]:
            with self.assertRaises(ValueError): self.store.create(title)
        for i in range(3): self.store.create(str(i))
        self.assertEqual(self.store.list(1,1)[0]['title'],'1')
        with self.assertRaises(ValueError): self.store.list(101)
        with self.assertRaises(KeyError): self.store.complete(999,True)
        with self.assertRaises(ValueError): self.store.complete(1,1)
    def test_http(self):
        with ThreadingHTTPServer(('127.0.0.1',0),handler(self.store)) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            connection=HTTPConnection('127.0.0.1',server.server_port,timeout=5)
            def request(method,path,data=None):
                connection.request(method,path,json.dumps(data) if data is not None else None,{'Content-Type':'application/json'})
                response=connection.getresponse(); return response.status,json.loads(response.read())
            try:
                self.assertEqual(request('GET','/health'),(200,{'status':'ok'}))
                status,task=request('POST','/tasks',{'title':'Review code'}); self.assertEqual(status,201)
                self.assertEqual(request('GET','/tasks')[1],[task])
                self.assertTrue(request('PATCH',f"/tasks/{task['id']}",{'done':True})[1]['done'])
                self.assertEqual(request('PATCH','/tasks/999',{'done':True})[0],404)
                self.assertEqual(request('POST','/tasks',{'title':''})[0],400)
                self.assertEqual(request('GET','/tasks?limit=100000000000000000000000')[0],400)
                self.assertEqual(request('GET','/missing')[0],404)
            finally: connection.close(); server.shutdown(); thread.join(timeout=5)
