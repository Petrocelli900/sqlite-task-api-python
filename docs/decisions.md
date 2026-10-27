# Decisões técnicas

GET /health retorna status. POST /tasks aceita {"title":"Revisar código"}. GET /tasks aceita limit (1..100) e offset não negativo. PATCH /tasks/1 aceita {"done":true}. Respostas JSON; entradas inválidas 400, ausentes 404 e armazenamento indisponível 503. Métodos não implementados recebem 501 do servidor padrão.

Cada operação abre e fecha conexão SQLite. Escritas usam parâmetros SQL e transação com commit ou rollback. Dados sobrevivem à reinicialização quando o mesmo arquivo é usado. Criação do esquema é idempotente, sem migrações versionadas.

O servidor escuta apenas em 127.0.0.1. Sem autenticação, TLS, exclusão de tarefas ou operação multiusuário. http.server é apenas demonstração local e não deve ser exposto como servidor de produção. JSON limitado a 8 KiB; Transfer-Encoding é rejeitado.

Testes usam arquivo temporário, porta efêmera e requisições HTTP reais. Não dependem de serviços externos.
