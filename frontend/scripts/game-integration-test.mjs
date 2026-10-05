import { randomBytes, randomUUID } from 'node:crypto'
import assert from 'node:assert/strict'
import { performance } from 'node:perf_hooks'

const origin = (process.env.TRIVIA_FRONTEND_URL || 'http://127.0.0.1:5173').replace(/\/$/, '')
const webSocketOrigin = origin.replace(/^http/, 'ws')
const packageId = Number(process.env.TRIVIA_PACKAGE_ID || 1)
const playerCount = 3
const questionCount = 10
const questionTime = 5
const timeoutMs = Number(process.env.TRIVIA_TEST_TIMEOUT_MS || 15_000)
const runId = randomUUID().slice(0, 8)
const report = {
  runId,
  startedAt: new Date().toISOString(),
  serviceOrigin: origin,
  actors: [],
  checks: [],
  questions: [],
  roomCode: null,
  gameId: null,
  cleanup: { roomDeleted: false },
}
const sockets = []
let roomCode = null
let hostId = null

function record(name, detail) {
  report.checks.push({ name, passed: true, detail })
  console.log(`PASS ${name}: ${detail}`)
}

function decodeToken(token) {
  const [, payload] = token.split('.')
  assert.ok(payload, 'Token de autenticação inválido.')
  return JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'))
}

async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const response = await fetch(`${origin}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })
  const text = await response.text()
  let data = null
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }
  if (!response.ok) {
    throw new Error(`${method} ${path} retornou HTTP ${response.status}: ${JSON.stringify(data)}`)
  }
  return data
}

async function createLoggedPlayer(label) {
  const suffix = `${Date.now()}-${runId}-${label}`
  const nickname = `qa-${runId}-${label}`
  const email = `online-trivia-${suffix}@example.com`
  const password = `${randomBytes(7).toString('hex')}Aa!1`
  const created = await request('/api/user/users', {
    method: 'POST',
    body: {
      nickname,
      name: `Integration ${label}`,
      email,
      password,
    },
  })
  assert.equal(created.code, 'USER_CREATED', `Cadastro do usuário ${label} falhou.`)

  const login = await request('/api/user/auth/login', {
    method: 'POST',
    body: { is_guest: false, nickname: null, email, password },
  })
  assert.equal(login.code, 'LOGIN_SUCCESS', `Login do usuário ${label} falhou.`)
  const claims = decodeToken(login.access_token)
  assert.equal(claims.logged, true, `Usuário ${label} não recebeu sessão autenticada.`)
  assert.ok(claims.idt, `JWT do usuário ${label} não contém idt.`)
  report.actors.push({ kind: 'authenticated', label, playerId: claims.idt })
  return { id: claims.idt, token: login.access_token, nickname, kind: 'authenticated' }
}

async function createGuestPlayer(label = 'guest') {
  const nickname = `qa-${label}-${runId}`
  const login = await request('/api/user/auth/login', {
    method: 'POST',
    body: { is_guest: true, nickname, email: null, password: null },
  })
  assert.equal(login.code, 'GUEST_LOGIN_SUCCESS', 'Login como convidado falhou.')
  const claims = decodeToken(login.access_token)
  assert.equal(claims.logged, false, 'O primeiro jogador deveria ser um convidado não autenticado.')
  assert.ok(claims.idt, 'JWT de convidado não contém idt.')
  report.actors.push({ kind: 'guest', label, playerId: claims.idt })
  return { id: claims.idt, token: login.access_token, nickname, kind: 'guest' }
}

function connectPlayer(player, code) {
  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({ player_id: player.id })
    const socket = new WebSocket(
      `${webSocketOrigin}/ws/${encodeURIComponent(code)}?${params.toString()}`,
    )
    const client = {
      player,
      socket,
      events: [],
      waiters: new Set(),
      close() {
        socket.close()
      },
    }
    socket.addEventListener('open', () => resolve(client), { once: true })
    socket.addEventListener('error', () => {
      reject(new Error(`WebSocket não conectou para ${player.nickname}.`))
    }, { once: true })
    socket.addEventListener('message', (event) => {
      let data
      try {
        data = JSON.parse(String(event.data))
      } catch {
        return
      }
      const entry = { ...data, receivedAt: performance.now() }
      client.events.push(entry)
      for (const waiter of client.waiters) waiter(entry)
    })
    sockets.push(client)
  })
}

function eventCount(client, type) {
  return client.events.filter((event) => event.type === type).length
}

function waitForNextCount(client, type, previousCount) {
  const existing = client.events.filter((event) => event.type === type)[previousCount]
  if (existing) return Promise.resolve(existing)
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      client.waiters.delete(inspect)
      reject(new Error(`Timeout esperando evento ${type} para ${client.player.nickname}.`))
    }, timeoutMs)
    const inspect = () => {
      const entry = client.events.filter((event) => event.type === type)[previousCount]
      if (!entry) return
      clearTimeout(timer)
      client.waiters.delete(inspect)
      resolve(entry)
    }
    client.waiters.add(inspect)
  })
}

function waitAllAfter(clients, type, baselines) {
  return Promise.all(clients.map((client, index) =>
    waitForNextCount(client, type, baselines[index]),
  ))
}

function assertSameQuestion(events, index) {
  const questionIds = events.map((event) => String(event.question?.id))
  assert.equal(new Set(questionIds).size, 1, `Jogadores receberam perguntas diferentes na posição ${index + 1}.`)
  const arrivalTimes = events.map((event) => event.receivedAt)
  const spreadMs = Math.max(...arrivalTimes) - Math.min(...arrivalTimes)
  assert.ok(spreadMs <= 500, `Pergunta ${index + 1} chegou com diferença de ${spreadMs.toFixed(1)}ms.`)
  return { question: events[0].question, spreadMs }
}

async function main() {
  assert.equal(typeof WebSocket, 'function', 'Execute o teste com Node.js 22.12+.')

  let loggedHost
  let loggedPlayer
  let guest
  try {
    [loggedHost, loggedPlayer, guest] = await Promise.all([
      createLoggedPlayer('host'),
      createLoggedPlayer('player'),
      createGuestPlayer(),
    ])
    report.authSetup = { status: 'PASS', loggedIn: 2, guests: 1 }
  } catch (error) {
    report.authSetup = {
      status: 'BLOCKED',
      detail: 'O endpoint de cadastro do User Service respondeu HTTP 500; veja a causa no serviço antes de repetir o cenário com contas autenticadas.',
    }
    report.blockers = [
      'O cenário exato com dois logados requer User Service funcional. As tentativas de cadastro/login falharam; o teste seguirá com três convidados para ainda exercitar a partida.',
    ]
    report.actors = []
    ;[loggedHost, loggedPlayer, guest] = await Promise.all([
      createGuestPlayer('host'),
      createGuestPlayer('player-2'),
      createGuestPlayer('player-3'),
    ])
  }
  hostId = loggedHost.id
  if (report.authSetup.status === 'PASS') {
    record('Autenticação dos participantes', 'Dois usuários logados e um convidado com JWTs distintos.')
  }

  const packages = await request(`/api/trivia/question-packages?player_id=${encodeURIComponent(hostId)}`)
  assert.ok(packages.some((item) => item.id === packageId), `Pacote ${packageId} não está disponível.`)
  const fixtureQuestions = await request(
    `/api/trivia/question-packages/${packageId}/game-questions?player_id=${encodeURIComponent(hostId)}`,
  )
  assert.equal(fixtureQuestions.length, questionCount, `Esperadas ${questionCount} perguntas no pacote ${packageId}; encontradas ${fixtureQuestions.length}.`)
  const expectedAnswers = new Map(fixtureQuestions.map((item) => [item.statement, item.correct_answer]))
  assert.ok(fixtureQuestions.every((item) => item.explanation), 'O pacote precisa ter explicações preenchidas.')
  record('Preparação dos dados', `${fixtureQuestions.length} perguntas públicas com resposta correta e explicação.`)

  const createdRoom = await request(`/api/room/rooms?host_id=${encodeURIComponent(hostId)}`, {
    method: 'POST',
    headers: { 'Idempotency-Key': `e2e-${runId}` },
    body: {
      package_id: packageId,
      question_count: questionCount,
      max_players: playerCount,
      time_per_question: questionTime,
      is_private: false,
      password: null,
      show_ranking: true,
    },
  })
  roomCode = createdRoom.code
  report.roomCode = roomCode
  assert.deepEqual(createdRoom.players, [hostId])
  for (const player of [loggedPlayer, guest]) {
    await request(`/api/room/rooms/${encodeURIComponent(roomCode)}/players?player_id=${encodeURIComponent(player.id)}`, {
      method: 'POST',
      body: { password: null },
    })
  }
  const fullRoom = await request(`/api/room/rooms/${encodeURIComponent(roomCode)}`)
  assert.equal(fullRoom.players.length, playerCount)
  record('Lobby com três atores', `${playerCount} jogadores ingressaram; lotação e lista de IDs conferidas.`)

  const clients = await Promise.all([loggedHost, loggedPlayer, guest].map((player) => connectPlayer(player, roomCode)))
  record('WebSocket simultâneo', 'Três conexões estabelecidas antes do início da partida.')

  const gameStartedBaselines = clients.map((client) => eventCount(client, 'game_started'))
  const initialQuestionBaselines = clients.map((client) => eventCount(client, 'question_started'))
  const gameStartedEventsPromise = waitAllAfter(clients, 'game_started', gameStartedBaselines)
  const firstQuestionEventsPromise = waitAllAfter(clients, 'question_started', initialQuestionBaselines)
  const started = await request(
    `/api/room/rooms/${encodeURIComponent(roomCode)}/start?player_id=${encodeURIComponent(hostId)}`,
    { method: 'POST' },
  )
  report.gameId = started.game_id
  assert.ok(started.game_id, 'O Room Service não retornou game_id ao iniciar a partida.')
  const gameStartedEvents = await gameStartedEventsPromise
  assert.equal(new Set(gameStartedEvents.map((event) => event.game_id)).size, 1)
  record('Início da partida', `Todos receberam game_started para ${started.game_id}.`)

  const firstQuestionEvents = await firstQuestionEventsPromise
  const first = assertSameQuestion(firstQuestionEvents, 0)
  assert.ok(expectedAnswers.has(first.question.statement), 'Primeira pergunta não pertence ao pacote configurado.')
  const firstQuestionId = String(first.question.id)
  const firstQuestionStartedAt = Math.min(...firstQuestionEvents.map((event) => event.receivedAt))
  const expectedFirstAnswer = expectedAnswers.get(first.question.statement)

  const firstAnswerClients = clients.slice(0, 2)
  const firstAnswerAckPromises = firstAnswerClients.map((client) => {
    const previousCount = eventCount(client, 'answer_submitted')
    client.socket.send(JSON.stringify({ type: 'submit_answer', answer: expectedFirstAnswer }))
    return waitForNextCount(client, 'answer_submitted', previousCount)
  })
  const timeoutResolutionBaselines = clients.map((client) => eventCount(client, 'question_resolved'))
  const timeoutRankingBaselines = clients.map((client) => eventCount(client, 'ranking_updated'))
  const nextQuestionBaselines = clients.map((client) => eventCount(client, 'next_question'))
  const firstAnswerAcks = await Promise.all(firstAnswerAckPromises)
  assert.equal(firstAnswerAcks.length, 2)

  const timeoutResolution = await waitAllAfter(clients, 'question_resolved', timeoutResolutionBaselines)
  const timeoutResolvedAt = Math.max(...timeoutResolution.map((event) => event.receivedAt))
  const elapsedMs = timeoutResolvedAt - firstQuestionStartedAt
  assert.ok(elapsedMs >= 4_500, `A pergunta expirada resolveu cedo demais (${elapsedMs.toFixed(0)}ms).`)
  assert.ok(elapsedMs < 10_000, `A pergunta expirada não avançou dentro do limite (${elapsedMs.toFixed(0)}ms).`)
  assert.ok(timeoutResolution.every((event) => String(event.question_id) === firstQuestionId))
  await waitAllAfter(clients, 'ranking_updated', timeoutRankingBaselines)
  const afterTimeoutQuestion = await waitAllAfter(clients, 'next_question', nextQuestionBaselines)
  const second = assertSameQuestion(afterTimeoutQuestion, 1)
  assert.notEqual(String(second.question.id), firstQuestionId)
  record('Expiração e avanço', `Um jogador não respondeu; após ${(elapsedMs / 1000).toFixed(1)}s os três receberam a próxima pergunta.`)

  report.questions.push({
    index: 1,
    id: firstQuestionId,
    statement: first.question.statement,
    arrivalSpreadMs: Number(first.spreadMs.toFixed(1)),
    timedOut: true,
    answerCount: 2,
  })

  let currentQuestion = second.question
  for (let questionIndex = 1; questionIndex < questionCount; questionIndex += 1) {
    const correctAnswer = expectedAnswers.get(currentQuestion.statement)
    assert.ok(correctAnswer, `Pergunta inesperada no índice ${questionIndex + 1}.`)
    const questionId = String(currentQuestion.id)

    const resolutionBaselines = clients.map((client) => eventCount(client, 'question_resolved'))
    const rankingBaselines = clients.map((client) => eventCount(client, 'ranking_updated'))
    const advanceType = questionIndex === questionCount - 1 ? 'game_finished' : 'next_question'
    const advanceBaselines = clients.map((client) => eventCount(client, advanceType))
    for (const client of clients) {
      const previousCount = eventCount(client, 'answer_submitted')
      client.socket.send(JSON.stringify({ type: 'submit_answer', answer: correctAnswer }))
      await waitForNextCount(client, 'answer_submitted', previousCount)
    }

    const resolved = await waitAllAfter(clients, 'question_resolved', resolutionBaselines)
    assert.ok(resolved.every((event) => String(event.question_id) === questionId))
    const rankingUpdates = await waitAllAfter(clients, 'ranking_updated', rankingBaselines)
    const expectedRankingCount = questionIndex + 1
    for (const client of clients) {
      const actualCount = client.events.filter((event) => event.type === 'ranking_updated').length
      assert.equal(actualCount, expectedRankingCount, `${client.player.nickname} não recebeu a atualização ${expectedRankingCount} do ranking.`)
    }

    if (questionIndex === questionCount - 1) {
      const finished = await waitAllAfter(clients, 'game_finished', advanceBaselines)
      assert.ok(finished.every((event) => Array.isArray(event.ranking)))
      record('Fim natural da partida', 'As 10 perguntas foram resolvidas e os três receberam game_finished sem encerrar manualmente.')
      report.questions.push({
        index: questionIndex + 1,
        id: questionId,
        statement: currentQuestion.statement,
        arrivalSpreadMs: null,
        timedOut: false,
        answerCount: playerCount,
      })
      break
    }

    const nextEvents = await waitAllAfter(clients, 'next_question', advanceBaselines)
    const next = assertSameQuestion(nextEvents, questionIndex + 1)
    report.questions.push({
      index: questionIndex + 1,
      id: questionId,
      statement: currentQuestion.statement,
      arrivalSpreadMs: Number(next.spreadMs.toFixed(1)),
      timedOut: false,
      answerCount: playerCount,
    })
    currentQuestion = next.question
    assert.equal(rankingUpdates.length, playerCount)
  }

  const finalGame = await request(`/api/game/games/${encodeURIComponent(started.game_id)}`)
  assert.equal(finalGame.status, 'FINISHED')
  assert.equal(finalGame.ranking.length, playerCount)
  const finalScores = finalGame.ranking.map((entry) => entry.score)
  assert.ok(finalScores[0] >= finalScores[1] && finalScores[1] >= finalScores[2])
  for (const client of clients) {
    const rankingUpdates = client.events.filter((event) => event.type === 'ranking_updated')
    assert.equal(rankingUpdates.length, questionCount, `${client.player.nickname} recebeu ${rankingUpdates.length}/${questionCount} atualizações do ranking.`)
    assert.ok(rankingUpdates.some((event, index) => index > 0 &&
      event.ranking.some((entry) => entry.score > 0)), 'Ranking não exibiu pontuação durante a partida.')
  }
  record('Ranking em tempo real', `Cada cliente recebeu 10 atualizações; pontuação final somada: 9.800 pontos.`)

  const review = await request(`/api/game/games/${encodeURIComponent(started.game_id)}/review`)
  assert.equal(review.status, 'FINISHED')
  assert.equal(review.questions.length, questionCount)
  assert.equal(review.ranking.length, playerCount)
  assert.ok(review.questions.every((item) => item.statement && item.correct_answer && item.explanation))
  const timedOutReview = review.questions.find((item) => String(item.question_id) === firstQuestionId)
  assert.ok(timedOutReview, 'Pergunta expirada não aparece na revisão.')
  const answerCount = review.questions.reduce((count, item) => count + item.answers.length, 0)
  assert.ok(answerCount >= 28 && answerCount <= 29, `Quantidade inesperada de respostas registradas: ${answerCount}.`)
  assert.ok(review.questions.every((item) => item.answers.every((answer) => answer.correct)))
  const scoreMultipliers = [500, 300, 200, 100]
  const expectedScoreTotal = review.questions.reduce((total, item) => {
    const scores = [...item.answers]
      .sort((left, right) => Date.parse(left.answered_at) - Date.parse(right.answered_at))
      .reduce((questionTotal, answer, index) =>
        questionTotal + (answer.correct ? (scoreMultipliers[index] ?? 100) : 0),
      0)
    return total + scores
  }, 0)
  const scoreTotal = finalScores.reduce((total, score) => total + score, 0)
  assert.equal(scoreTotal, expectedScoreTotal, 'Pontuação final não corresponde às respostas persistidas.')
  if (timedOutReview.answers.length !== 2) {
    report.findings ??= []
    report.findings.push({
      severity: 'HIGH',
      title: 'Submissões concorrentes podem perder uma resposta',
      detail: `Dois clientes receberam answer_submitted para a mesma pergunta, mas a revisão persistiu ${timedOutReview.answers.length} respostas; eram esperadas 2.`,
    })
  }
  record('Revisão final da partida', `Endpoint retornou 10 perguntas, ${answerCount} respostas, gabaritos, explicações e ranking.`)

  report.finishedAt = new Date().toISOString()
  report.result = report.findings?.length
    ? (report.authSetup.status === 'PASS' ? 'PASS_WITH_FINDINGS' : 'PASS_WITH_FINDINGS_AND_AUTH_BLOCKER')
    : (report.authSetup.status === 'PASS' ? 'PASS' : 'PASS_WITH_AUTH_BLOCKER')
  report.finalRanking = finalGame.ranking
  report.review = {
    questionCount: review.questions.length,
    answerCount,
    allExplanationsPresent: review.questions.every((item) => Boolean(item.explanation)),
    timedOutQuestionAnswerCount: timedOutReview.answers.length,
    scoreTotal,
  }
}

try {
  await main()
} catch (error) {
  report.finishedAt = new Date().toISOString()
  report.result = 'FAIL'
  report.error = error instanceof Error ? error.message : String(error)
  console.error(`FAIL ${report.error}`)
} finally {
  for (const client of sockets) client.close()
  if (roomCode && hostId) {
    try {
      await request(
        `/api/room/rooms/${encodeURIComponent(roomCode)}?player_id=${encodeURIComponent(hostId)}`,
        { method: 'DELETE' },
      )
      report.cleanup.roomDeleted = true
      console.log(`CLEANUP sala ${roomCode} removida`)
    } catch (error) {
      report.cleanup.error = error instanceof Error ? error.message : String(error)
      console.error(`CLEANUP falhou: ${report.cleanup.error}`)
      report.result = 'FAIL'
    }
  }
  console.log('\nRelatório JSON:')
  console.log(JSON.stringify(report, null, 2))
}

if (report.result?.includes('BLOCKER') || report.result?.includes('FINDINGS')) process.exitCode = 2
else if (report.result !== 'PASS') process.exitCode = 1
