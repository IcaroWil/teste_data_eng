# Teste Técnico Delfos - Pipeline de Dados com Python

Este projeto implementa um pipeline ETL completo conforme especificado no teste técnico da Delfos. O sistema processa dados de energia eólica, agregando informações de 1 minuto em janelas de 10 minutos para análise.

## O que foi implementado

### Core (Obrigatório)
- **Banco Fonte**: PostgreSQL com dados simulados de energia eólica (1-min por 10 dias)
- **Banco Alvo**: PostgreSQL para armazenar agregações processadas
- **API FastAPI**: Endpoint para consultar dados do banco fonte com filtros
- **Script ETL**: Processamento de dados com pandas e SQLAlchemy

### Bônus 
- **Orquestração Dagster**: Job e schedule para execução automática do ETL

## Como executar

### Pré-requisitos
- Python 3.8+
- Docker e Docker Compose
- Git

### 1. Preparar ambiente
```bash
git clone https://github.com/IcaroWil/teste_data_eng.git
cd teste_data_eng

# Criar ambiente virtual
python -m venv .venv
# ou
python3 -m venv .venv

# Entrar no ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar bancos de dados
```bash
docker compose up -d

# Verificar se estão rodando
docker ps
```

### 3. Configurar variáveis de ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# As URLs já estão corretas para o docker-compose
```

### 4. Popular banco fonte
```bash
# Gerar dados simulados (10 dias, 1-min)
python -m src.db.source_seed
```

### 5. Subir API
```bash
# Em um terminal
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Testar API
```bash
# Em outro terminal
curl "http://localhost:8000/data?start=xxxx-xx-xxT00:00:00Z&end=xxxx-xx-xxT23:59:59Z"
# Alterar o valor de x para a data que populou EX: 2025-08-31
```

### 7. Executar ETL
```bash
# Processar dados
python -m src.etl.run_etl
```

## Bônus: Dagster 

### Instalar Dagster
```bash
pip install dagster dagster-postgres
```

### Executar orquestração
```bash
# Em um terminal separado
dagster dev -m src.dagster.definitions
```

### Acessar interface
- Abrir: http://127.0.0.1:3000
- Ver assets, jobs e schedules
- Executar ETL via interface web

## Estrutura do projeto

```
src/
├── api/                    # API FastAPI
│   ├── main.py            # App principal
│   ├── dependencies.py     # Dependências da API
│   └── routers/           # Rotas da API
│       └── data.py        # Endpoint de dados
├── db/                     # Camada de dados
│   ├── source_models.py   # Modelos banco fonte
│   ├── target_models.py   # Modelos banco alvo
│   ├── session.py         # Conexões SQLAlchemy
│   └── source_seed.py     # População de dados
├── etl/                    # Processamento ETL
│   ├── client.py          # Cliente HTTP para API
│   ├── transform.py       # Agregações 10-min
│   └── run_etl.py         # Script principal
├── dagster/                # Orquestração (bônus)
│   ├── assets.py          # Assets particionados
│   ├── jobs.py            # Jobs e schedules
│   ├── definitions.py     # Definições e configurações
│   └── resources.py       # Recursos de banco
└── settings.py             # Configurações globais
```

## Tecnologias utilizadas

- **Python 3.8+**: Linguagem principal
- **FastAPI**: API web moderna e rápida
- **PostgreSQL**: Bancos de dados
- **SQLAlchemy**: ORM e conexões
- **Pandas**: Processamento de dados
- **Dagster**: Orquestração (bônus)
- **Docker**: Containerização dos bancos

## Decisões técnicas

### Arquitetura
- **Monolito simples**: Tudo em um repositório para facilitar deploy
- **Separação clara**: API, ETL e dados em módulos distintos
- **Configuração via .env**: Fácil adaptação para diferentes ambientes

### Banco de dados
- **Fonte**: Dados brutos de 1 em 1 minuto
- **Alvo**: Agregações de 10 minutos em formato longo (normalizado)
- **Relacionamentos**: Tabelas `signal` e `data` com chaves estrangeiras

### ETL
- **Input**: Data específica (execução por dia)
- **Processamento**: Agregações mean, min, max, stddev
- **Output**: Dados normalizados no banco alvo

## Testando o sistema

### Verificar dados fonte
```bash
# Conectar ao banco fonte
psql -h localhost -p 5432 -U user -d source_db
# SELECT COUNT(*) FROM data;  # Deve retornar ~14400 (10 dias)
```

### Verificar dados alvo
```bash
# Conectar ao banco alvo
psql -h localhost -p 5433 -U user -d target_db
# SELECT COUNT(*) FROM data;  # Deve retornar agregações processadas
```

### Testar API
```bash
# Dados de um dia específico
curl "http://localhost:8000/data?start=xxxx-xx-xxT00:00:00Z&end=xxxx-xx-xxT23:59:59Z"
# Alterar o valor de x para o dia específico

# Apenas wind_speed
curl "http://localhost:8000/data?start=xxxx-xx-xxT00:00:00Z&end=xxxx-xx-xxT23:59:59Z&variables=wind_speed"
# Alterar o valor de x para a data específica
```

## Troubleshooting

### Erro de conexão com banco
- Verificar se Docker está rodando
- Confirmar URLs no .env
- Testar conectividade: `telnet localhost 5432`

### API não responde
- Verificar se uvicorn está rodando
- Confirmar porta 8000 livre
- Ver logs do terminal

### ETL falha
- Verificar se API está rodando
- Confirmar dados no banco fonte
- Ver logs de erro no terminal

### Aprendizados
- ETL com Python e pandas
- APIs com FastAPI
- Orquestração com Dagster
- Bancos PostgreSQL
- Docker para desenvolvimento

## Contribuição

Este é um projeto de teste técnico. Para dúvidas ou melhorias, abra uma issue ou pull request.

---

**Desenvolvido com ❤️ para o teste técnico da Delfos**

*Energia em máxima performance* ⚡


