# Relatório de teste de integração multiplayer

**Data:** 5 de outubro de 2026  
**Resultado geral:** execução parcial, com uma falha de concorrência confirmada e o teste de dois usuários autenticados bloqueado pela configuração atual do User Service.

## Escopo executado

O teste automatizado `npm run test:integration` usou HTTP e WebSocket encaminhados pelo Vite (`http://127.0.0.1:5173`). Foram criados três clientes simultâneos, uma sala pública com dez perguntas e limite de cinco segundos por pergunta. Como o cadastro normal não funcionou no ambiente, a execução prosseguiu com três convidados. Um deles deixou de responder à primeira pergunta; os outros enviaram respostas, e todos responderam às nove seguintes.

Esta execução automatiza os protocolos HTTP/WebSocket através do proxy do front-end. Ela **não** automatiza os componentes React em três navegadores. O fluxo visual de um cliente já havia sido exercitado separadamente; a distribuição de jogadores deste relatório foi validada no Game Service.

## Resultados

| Verificação | Resultado | Observação |
|---|---|---|
| Pacote de perguntas | Passou | Pacote público com 10 perguntas, gabaritos e explicações. |
| Lobby e conexão simultânea | Passou | 3 clientes conectados antes do início. |
| Entrega de perguntas | Passou | Os 3 clientes receberam a mesma pergunta; diferença observada entre eventos foi de até 0,2 ms. |
| Timeout | Passou | Após 5 s sem resposta de um jogador, os três receberam a resolução e a próxima pergunta. |
| Continuação e término natural | Passou | A partida avançou pelas 10 perguntas e os três clientes receberam `game_finished`. |
| Ranking | Passou parcialmente | Cada cliente recebeu 10 eventos `ranking_updated` e o ranking final; a pontuação foi afetada pela falha de persistência descrita abaixo. |
| Revisão pela API | Passou parcialmente | A API retornou 10 perguntas, gabaritos, explicações e respostas; faltou uma resposta concorrente na persistência. |
| Limpeza | Passou | A sala temporária foi removida e não restaram salas públicas. |

**Execução mais recente:** run `e832a4aa`, sala `RN9NZB`, jogo `43198987-29c6-42ec-b147-2f013b6c0430`, três clientes convidados. A pergunta expirada recebeu duas submissões concorrentes. A revisão retornou 28 respostas, em vez das 29 esperadas (duas respostas na questão expirada e três em cada uma das outras nove). A falha de persistência ocorreu novamente na execução anterior.

## Achados

### Alta — submissões concorrentes podem sobrescrever respostas

Dois jogadores enviaram resposta para a mesma pergunta quase ao mesmo tempo e ambos receberam `answer_submitted`. Porém, a revisão final persistiu somente uma das duas respostas. A pontuação somada foi 9.500, coerente com o estado incompleto salvo, mas menor do que a esperada quando ambas as respostas são gravadas.

O caso ocorre no fluxo que lê o jogo, acrescenta a resposta e atualiza o documento Redis sem serializar/mesclar as atualizações concorrentes: [submit_answer.py](../games_service/app/application/use_cases/submit_answer.py) e [game_websocket.py](../games_service/app/presentation/websocket/game_websocket.py). A confirmação atual é enviada após a tentativa de atualização, mas não detecta se outra resposta sobrescreveu essa gravação.

### Bloqueio — não foi possível criar os dois usuários autenticados

O cadastro no User Service retorna HTTP 500 com `database "online_trivia" does not exist`. A configuração de Compose declara o banco `trivia` para o Postgres em [docker-compose.yml](../docker-compose.yml); o serviço de usuário ativo, por sua vez, tenta conectar a `online_trivia`. Portanto, **não foi possível executar a distribuição solicitada de dois usuários logados e um convidado**. O teste marcou essa etapa como bloqueada e usou três convidados para continuar a validação do jogo.

### Revisão de questões não aparece na tela de resultado

A revisão com respostas, alternativas corretas e explicações está disponível em `GET /games/{game_id}/review`. A interface, porém, mostra somente a classificação em [App.tsx](./src/App.tsx). Assim, ao terminar pelo front, o ranking fica visível, mas as perguntas e explicações não são apresentadas.

### Apelidos de outros jogadores

O Game Service cria jogadores usando o próprio UUID como `nickname` em [start_game.py](../games_service/app/application/use_cases/start_game.py). Como resultado, entradas de outros participantes na classificação e na revisão aparecem com o identificador, não com o apelido escolhido.

## Validação final

- `node --check scripts/game-integration-test.mjs`: passou.
- `npm run build`: passou, incluindo a checagem TypeScript.
- A sala usada no cenário foi removida.

## Como repetir

Com os serviços ativos e Node.js 22.12+:

```bash
npm run test:integration
```

O teste retorna código de saída 2 quando precisa recorrer ao modo de três convidados; isso indica que a rodada multiplayer foi exercitada, mas que o cenário exato de autenticação não foi validado.
