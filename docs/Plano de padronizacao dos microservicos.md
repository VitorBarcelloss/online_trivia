# Plano de padronização dos microsserviços

Escopo: `trivia_service`, `room_service` e `user_service` permanecem projetos independentes. Não compartilhar código, banco nem adicionar integrações entre eles nesta etapa. Autenticação permanece sob responsabilidade do `user_service`; o fluxo do front-end está fora destas mudanças.

## Padrão-alvo

- **Estrutura:** manter `controllers`, `dtos`, `services`, `repositories`, `models`, `core` e `database` em cada serviço. Cada projeto mantém suas próprias dependências e configuração por ambiente.
- **DTOs:** separar entrada e saída por operação/recurso (`Create...DTO`, `Update...DTO`, `...ResponseDTO`). Não retornar entidade ORM nem reutilizar DTO de saída como corpo de entrada. Campos gerados pelo serviço, como ID, autoria e timestamps, não são aceitos do cliente.
- **Rotas:** usar recursos no plural e verbos HTTP (`POST /resources`, `GET /resources/{id}`, `PUT/PATCH /resources/{id}`, `DELETE /resources/{id}`). Evitar sufixos como `/create`, `/update` e `/delete`.
- **Respostas:** criação retorna DTO e HTTP 201; leituras/atualizações retornam DTO e HTTP 200. Exclusões retornam HTTP 204 sem corpo. Listas vazias retornam `[]` com HTTP 200.
- **Erros:** uma exceção de domínio e handler por serviço, com envelope estável `{status, code, message}` e códigos HTTP adequados. Registrar cada handler uma única vez na criação da aplicação.
- **Responsabilidades:** controller trata HTTP/DI; service aplica regras, autorização e transação; repository consulta/persiste sem regras de negócio. Repositórios SQL usam `Session` tipada e não fazem `commit`; o service confirma ou reverte a operação.
- **Validação e modelos:** validar entradas com Pydantic; manter modelos de persistência distintos de DTOs. Usar timestamps UTC consistentes e valores mutáveis com `default_factory`.
- **Dependências externas:** cada serviço declara e instala suas próprias dependências. Integrações entre microsserviços serão tratadas depois por contratos/clientes explícitos, nunca por imports diretos.
- **Idempotência:** POSTs com chave natural reutilizam o recurso quando o conteúdo é igual e retornam `409` quando a mesma chave identifica dados diferentes. PATCH repetido sem mudança retorna sucesso; DELETE repetido retorna `204`. A criação de sala usa `Idempotency-Key`, pois duas salas com a mesma configuração podem ser intencionais.

## Diferenças e lacunas atuais

- **`trivia_service`:** separa DTOs por criação, atualização e resposta; usa `PATCH`, respostas `204`, listas vazias válidas e migração inicial Alembic. Criar pacote usa autor+nome (sem diferenciar maiúsculas); pergunta usa pacote+enunciado; alternativa usa pergunta+texto. Conteúdo igual retorna o recurso existente; dados diferentes retornam `409`.
- **`room_service`:** mantém Redis; operações Redis são assíncronas, o hash persiste o modelo completo e a criação aceita `Idempotency-Key`. Repetir join, leave, start ou delete mantém o estado e retorna sucesso.
- **`user_service`:** criação repetida com as mesmas credenciais e dados retorna sucesso; email/nickname em conflito com dados diferentes retorna `409`. Atualizações sem mudança retornam sucesso; repetir uma troca para a senha já vigente é um no-op bem-sucedido.
- **Nos três:** erros usam `{status, code, message}` e cada exceção tem um handler registrado uma vez. Não foram adicionados testes nesta etapa.

## Sequência de execução

1. **Contratos e execução:** alinhar rotas, DTOs, respostas, erros e dependências independentes. Concluído nesta rodada.
2. **Idempotência:** proteger criações por chaves naturais ou `Idempotency-Key` e tornar atualizações/exclusões repetíveis. Concluído nesta rodada.
3. **Persistência:** versionar o schema SQL de trivia; preservar Redis em salas e transações locais em usuários. Para banco trivia vazio: `cd trivia_service && alembic upgrade head`. A migração não foi executada; bancos já existentes precisam ser verificados antes de aplicá-la.
4. **Depois:** discutir integrações; testes não fazem parte desta rodada.
