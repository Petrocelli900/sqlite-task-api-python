# sqlite-task-api-python

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Verification](https://github.com/Petrocelli900/sqlite-task-api-python/actions/workflows/verify.yml/badge.svg)

API HTTP local de tarefas com persistência SQLite, paginação, validação e testes de integração.

Projeto de portfólio com biblioteca padrão, execução local e testes automatizados. Não exige chave de API nem instalação de dependências.

## Executar

```bash
git clone https://github.com/Petrocelli900/sqlite-task-api-python.git
cd sqlite-task-api-python
python -m unittest discover -s tests -v
python task_api.py --db tasks.db --port 8080
```

Use python3 se esse for o comando do seu ambiente. Requer Python 3.11 ou superior.

## Estrutura

- task_api.py: implementação e interface de linha de comando.
- tests/test_app.py: testes de comportamento e falhas.
- docs/decisions.md: escopo, decisões e limitações.
- .github/workflows/verify.yml: verificação em Python 3.11.

## Escopo

Consulte [as decisões técnicas](docs/decisions.md) antes de adaptar para outros usos. Demonstração de portfólio com limitações explícitas.

Implementação inicial criada com assistência de IA. Exemplos utilizam dados fictícios.

[Perfil do autor](https://github.com/Petrocelli900)
