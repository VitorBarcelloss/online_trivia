# Online Trivia

Projeto de trivia multiplayer composto por quatro microsserviços (usuários,
perguntas, salas e partidas) e uma aplicação web em React, TypeScript e Vite.
PostgreSQL, Redis e RabbitMQ são usados como infraestrutura.

## Requisitos

- Docker com Docker Compose
- Node.js 20.19+ ou 22.12+ e npm
- Para executar o teste de integração: Node.js 22.12+ (o teste usa o cliente
  WebSocket nativo do Node)

## Configurar os serviços

O Docker Compose lê um arquivo `.env` de cada microsserviço. Crie-os a partir
dos exemplos:

```bash
cp user_service/.env.sample user_service/.env
cp trivia_service/.env.sample trivia_service/.env
cp room_service/.env.sample room_service/.env
cp games_service/.env.sample games_service/.env
```

Edite os quatro arquivos `.env` e preencha as configurações necessárias
indicadas nos respectivos exemplos. Dentro do Compose, os serviços de
infraestrutura podem ser acessados pelos nomes `postgres`, `redis` e
`rabbitmq`; o PostgreSQL usa o banco `trivia` e as credenciais definidas em
`docker-compose.yml`. Não compartilhe nem versione os arquivos `.env`.

## Subir o projeto

Na raiz do repositório, inicie a infraestrutura e os microsserviços:

```bash
docker compose up --build -d
```

O Compose não aplica as migrações do banco automaticamente. Para preparar um
banco novo, aplique as migrações dos serviços User e Trivia:

```bash
docker compose run --rm \
  -v "$(pwd)/user_service/migrations:/app/migrations:ro" \
  -v "$(pwd)/user_service/alembic.ini:/app/alembic.ini:ro" \
  user-service alembic upgrade head

docker compose exec trivia-service alembic upgrade head
```

Se já houver dados no banco, confira o estado do schema antes de aplicar
migrações.

Confira se os containers estão ativos e acompanhe os logs:

```bash
docker compose ps
docker compose logs -f
```

Em outro terminal, instale as dependências e inicie o front-end:

```bash
cd frontend
npm install
npm run dev
```

Abra [http://localhost:5173](http://localhost:5173). O Vite encaminha as
requisições HTTP e WebSocket aos microsserviços; não é necessário configurar
CORS para o desenvolvimento local.

Os serviços disponibilizam a documentação interativa da API em:

- User Service: [http://localhost:8000/docs](http://localhost:8000/docs)
- Trivia Service: [http://localhost:8001/docs](http://localhost:8001/docs)
- Room Service: [http://localhost:8002/docs](http://localhost:8002/docs)
- Game Service: [http://localhost:8003/docs](http://localhost:8003/docs)

Para parar os containers sem remover os dados persistidos:

```bash
docker compose down
```

## Testar

### Build do front-end

Na pasta `frontend`, execute:

```bash
npm run build
```

Esse comando verifica os tipos TypeScript e gera a versão de produção.

### Teste de integração multiplayer

Com os quatro microsserviços ativos, abra outro terminal e execute:

```bash
cd frontend
npm run test:integration
```

Mantenha também o front-end rodando com `npm run dev` em outro terminal. O
teste usa o proxy do Vite em `http://127.0.0.1:5173`, cria uma sala, conecta
três jogadores por WebSocket, envia respostas e verifica o ranking e a
revisão da partida. Ele espera encontrar o pacote de perguntas de ID `1`
com pelo menos dez perguntas cadastradas.

O teste tenta criar duas contas de usuário e também usa um convidado. Contas
criadas com sucesso permanecem no banco, pois o User Service não oferece
exclusão de usuários. Se o cadastro de usuários falhar, o teste pode
continuar com convidados, mas termina com código de saída `2` para sinalizar
o bloqueio de autenticação. A sala de teste é removida ao final.

Para verificar a aplicação de produção localmente depois do build:

```bash
npm run preview
```

## Estrutura

- `frontend/`: aplicação web React/TypeScript e teste de integração
- `user_service/`: autenticação e usuários
- `trivia_service/`: pacotes de perguntas, perguntas e alternativas
- `room_service/`: criação e gerenciamento de salas
- `games_service/`: partidas e comunicação em tempo real
- `docker-compose.yml`: infraestrutura e microsserviços
