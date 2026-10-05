# Online Trivia — Front-end

Aplicação web em React, TypeScript e Vite para testar o Online Trivia pelos microsserviços existentes.

## Requisitos

- Node.js 20.19+ ou 22.12+
- npm
- Os serviços do projeto disponíveis nas portas `8000` a `8003`
- Redis e RabbitMQ conforme a configuração dos serviços
- Pacotes públicos com perguntas cadastrados no Trivia Service

## Iniciar

Na raiz do repositório, inicie os serviços da aplicação:

```bash
docker compose up --build
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Abra o endereço exibido pelo Vite (por padrão, `http://localhost:5173`). Para gerar e validar a versão de produção:

```bash
npm run build
npm run preview
```

## Teste de integração multiplayer

Com o Vite e os quatro microsserviços já ativos, execute em outro terminal:

```bash
npm run test:integration
```

O cenário usa o proxy do Vite para HTTP e WebSocket, cria uma sala de dez perguntas, conecta três clientes, deixa um cliente sem responder à primeira pergunta, responde às seguintes, verifica o ranking e consulta a revisão final. O Node.js precisa ser 22.12 ou mais recente para fornecer o cliente WebSocket nativo. A sala de teste é removida ao terminar.

Quando o User Service está funcional, o teste provisiona dois usuários autenticados e um convidado. Se o cadastro falhar, continua com três convidados, indica `PASS_WITH_AUTH_BLOCKER` ou `PASS_WITH_FINDINGS_AND_AUTH_BLOCKER` no relatório e termina com código de saída 2. O User Service não oferece exclusão de usuários; portanto, contas descartáveis criadas em um teste bem-sucedido permanecem no banco.

O script dirige HTTP/WebSocket pelo proxy, não automatiza os controles React em três navegadores. A tela final do front-end pode ser conferida manualmente; a API de revisão é consultada separadamente pelo teste.

## Funcionalidades

- Login como convidado pelo endpoint `/auth/login` do User Service.
- Lista de salas públicas, criação de sala e entrada por código.
- Lobby com atualização periódica dos jogadores e conexão WebSocket antecipada.
- Perguntas e envio de respostas em tempo real, ranking e encerramento pelo host.
- Tela de classificação final após o evento `game_finished`.

## Proxy de desenvolvimento

O Vite encaminha chamadas do navegador diretamente aos serviços locais; não é necessário habilitar CORS nos microsserviços:

| Prefixo no front-end | Serviço | Destino |
| --- | --- | --- |
| `/api/user` | User | `http://localhost:8000` |
| `/api/trivia` | Trivia | `http://localhost:8001` |
| `/api/room` | Room | `http://localhost:8002` |
| `/api/game` | Game | `http://localhost:8003` |
| `/ws` | Game WebSocket | `ws://localhost:8003/games` |

Os prefixos `/api/...` são removidos pelo proxy antes de encaminhar cada requisição. O front-end mantém um UUID de jogador por sessão de navegador e envia esse identificador nos parâmetros `host_id`/`player_id` exigidos pelo Room Service e pelo WebSocket. O token de convidado devolvido pelo User Service é guardado na sessão, mas os endpoints de salas e jogo existentes não exigem esse token.

O Game Service atual identifica os jogadores pelo UUID ao iniciar uma partida. Assim, nos rankings a aplicação mostra o apelido local do próprio jogador e mantém o identificador retornado pelo serviço para os demais participantes.

## Configurações

- `package.json`: scripts de desenvolvimento, build e preview, dependências React e Vite.
- `tsconfig.json`, `tsconfig.app.json` e `tsconfig.node.json`: referências TypeScript e checagem estrita.
- `vite.config.ts`: plugin React, servidor acessível na rede local e proxies HTTP/WebSocket.
