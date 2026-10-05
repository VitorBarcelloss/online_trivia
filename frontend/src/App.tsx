import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  BookOpen,
  Check,
  CircleHelp,
  Clock3,
  Crown,
  DoorOpen,
  Gamepad2,
  KeyRound,
  LoaderCircle,
  LockKeyhole,
  LogOut,
  Medal,
  Plus,
  Radio,
  RefreshCw,
  Sparkles,
  Trophy,
  Users,
  Wifi,
  WifiOff,
  X,
} from 'lucide-react'
import {
  api,
  gameSocketUrl,
  type Player,
  type Question,
  type QuestionPackage,
  type RankingEntry,
  type Room,
  type Session,
} from './api'

type Screen = 'login' | 'home' | 'lobby' | 'game' | 'results'
type Notice = { kind: 'error' | 'success'; text: string } | null

const SESSION_KEY = 'online-trivia-session'

function readSession(): Session | null {
  try {
    const value = localStorage.getItem(SESSION_KEY)
    return value ? JSON.parse(value) as Session : null
  } catch {
    return null
  }
}

function shortId(id: string): string {
  return id.replace(/-/g, '').slice(0, 6).toUpperCase()
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Ocorreu um erro inesperado.'
}

function App() {
  const [session, setSession] = useState<Session | null>(readSession)
  const [screen, setScreen] = useState<Screen>(readSession() ? 'home' : 'login')
  const [rooms, setRooms] = useState<Room[]>([])
  const [packages, setPackages] = useState<QuestionPackage[]>([])
  const [room, setRoom] = useState<Room | null>(null)
  const [question, setQuestion] = useState<Question | null>(null)
  const [questionNumber, setQuestionNumber] = useState(0)
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [notice, setNotice] = useState<Notice>(null)
  const [loading, setLoading] = useState(false)
  const [socketConnected, setSocketConnected] = useState(false)
  const [answerSent, setAnswerSent] = useState(false)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null)
  const [explanation, setExplanation] = useState('')
  const [remaining, setRemaining] = useState(0)
  const [modal, setModal] = useState<'create' | 'join' | null>(null)
  const [joinCode, setJoinCode] = useState('')
  const [joinPassword, setJoinPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const socketRef = useRef<WebSocket | null>(null)
  const currentQuestionIdRef = useRef<string | null>(null)
  const player = session?.player

  const updateRoom = useCallback(async (code: string) => {
    const updated = await api.getRoom(code)
    setRoom(updated)
    return updated
  }, [])

  const refreshRooms = useCallback(async () => {
    setLoading(true)
    try {
      const [publicRooms, availablePackages] = await Promise.all([
        api.listRooms(),
        player ? api.listPackages(player.id) : Promise.resolve([]),
      ])
      setRooms(publicRooms.filter((item) => item.status === 'WAITING'))
      setPackages(availablePackages)
      setNotice(null)
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }, [player])

  useEffect(() => {
    if (session) void refreshRooms()
  }, [session, refreshRooms])

  useEffect(() => {
    if (screen !== 'lobby' || !room) return
    const interval = window.setInterval(() => {
      void updateRoom(room.code).catch((error: unknown) => {
        setNotice({ kind: 'error', text: errorMessage(error) })
      })
    }, 3500)
    return () => window.clearInterval(interval)
  }, [screen, room?.code, updateRoom])

  useEffect(() => {
    if (!room || !player || !['lobby', 'game'].includes(screen)) return
    let reconnectTimer = 0
    let disposed = false

    const connect = () => {
      if (disposed) return
      const socket = new WebSocket(gameSocketUrl(room.code, player.id))
      socketRef.current = socket
      socket.onopen = () => {
        setSocketConnected(true)
        if (room.game_id) {
          void api.getGame(room.game_id).then((game) => {
            if (disposed || game.status !== 'IN_PROGRESS') return
            if (game.question) {
              if (currentQuestionIdRef.current !== String(game.question.id)) {
                currentQuestionIdRef.current = String(game.question.id)
                setQuestionNumber((current) => current === 0 ? 1 : current + 1)
              }
              setQuestion(game.question)
              setRemaining(game.question_time)
              setScreen('game')
            }
            setRanking(game.ranking)
          }).catch((error: unknown) => {
            setNotice({ kind: 'error', text: errorMessage(error) })
          })
        }
      }
      socket.onmessage = (event: MessageEvent<string>) => {
        let message: Record<string, unknown>
        try {
          message = JSON.parse(event.data) as Record<string, unknown>
        } catch {
          setNotice({ kind: 'error', text: 'O Game Service enviou uma mensagem inválida.' })
          return
        }

        switch (message.type) {
          case 'game_started':
            currentQuestionIdRef.current = null
            setQuestionNumber(0)
            setScreen('game')
            setAnswerSent(false)
            setSelectedAnswer(null)
            setCorrectAnswer(null)
            break
          case 'question_started':
          case 'next_question':
            {
              const incomingQuestion = message.question as Question
              if (currentQuestionIdRef.current !== String(incomingQuestion.id)) {
                currentQuestionIdRef.current = String(incomingQuestion.id)
                setQuestionNumber((current) => current === 0 ? 1 : current + 1)
              }
              setQuestion(incomingQuestion)
            }
            setRemaining(room.time_per_question)
            setAnswerSent(false)
            setSelectedAnswer(null)
            setCorrectAnswer(null)
            setExplanation('')
            setScreen('game')
            break
          case 'answer_submitted':
            setAnswerSent(true)
            break
          case 'question_resolved':
            setCorrectAnswer(String(message.correct_answer ?? ''))
            setExplanation(String(message.explanation ?? ''))
            break
          case 'ranking_updated':
            setRanking(message.ranking as RankingEntry[])
            break
          case 'game_finished':
            setRanking(message.ranking as RankingEntry[])
            setScreen('results')
            setQuestion(null)
            break
          case 'error':
            setNotice({ kind: 'error', text: String(message.message ?? 'Erro no jogo.') })
            break
          default:
            break
        }
      }
      socket.onerror = () => {
        setNotice({ kind: 'error', text: 'Não foi possível conectar ao Game Service.' })
      }
      socket.onclose = () => {
        setSocketConnected(false)
        if (!disposed) reconnectTimer = window.setTimeout(connect, 2500)
      }
    }

    connect()
    return () => {
      disposed = true
      window.clearTimeout(reconnectTimer)
      socketRef.current?.close()
      socketRef.current = null
      setSocketConnected(false)
    }
  }, [room?.code, room?.game_id, room?.time_per_question, player?.id, screen === 'results'])

  useEffect(() => {
    if (screen !== 'game' || !question || correctAnswer !== null) return
    const interval = window.setInterval(() => {
      setRemaining((current) => Math.max(0, current - 1))
    }, 1000)
    return () => window.clearInterval(interval)
  }, [screen, question?.id, correctAnswer])

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const cleanedNickname = nickname.trim()
    if (!cleanedNickname) {
      setNotice({ kind: 'error', text: 'Digite um apelido para continuar.' })
      return
    }
    setLoading(true)
    try {
      const loggedIn = await api.loginAsGuest(cleanedNickname)
      localStorage.setItem(SESSION_KEY, JSON.stringify(loggedIn))
      setSession(loggedIn)
      setScreen('home')
      setNotice(null)
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  const enterRoom = async (code: string, password?: string) => {
    if (!player) return
    setLoading(true)
    try {
      const found = await api.getRoom(code.trim().toUpperCase())
      const joined = found.players.includes(player.id)
        ? found
        : await api.joinRoom(found.code, player.id, password)
      setRoom(joined)
      setQuestion(null)
      setQuestionNumber(0)
      currentQuestionIdRef.current = null
      setRanking([])
      setModal(null)
      setJoinPassword('')
      setScreen(joined.status === 'IN_PROGRESS' ? 'game' : 'lobby')
      setNotice(null)
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  const createRoom = async (values: {
    package_id: number
    question_count: number
    max_players: number
    time_per_question: number
    is_private: boolean
    password: string | null
    show_ranking: boolean
  }) => {
    if (!player) return
    setLoading(true)
    try {
      const created = await api.createRoom(player.id, values)
      setRoom(created)
      setQuestionNumber(0)
      currentQuestionIdRef.current = null
      setModal(null)
      setScreen('lobby')
      setNotice(null)
      void refreshRooms()
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  const startGame = async () => {
    if (!room || !player) return
    setLoading(true)
    try {
      const started = await api.startGame(room.code, player.id)
      setRoom(started)
      setScreen('game')
      setNotice(null)
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = () => {
    if (!selectedAnswer || answerSent || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      if (!socketConnected) setNotice({ kind: 'error', text: 'A conexão com a partida foi interrompida.' })
      return
    }
    socketRef.current.send(JSON.stringify({ type: 'submit_answer', answer: selectedAnswer }))
  }

  const finishGame = () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setNotice({ kind: 'error', text: 'Sem conexão com o Game Service. Tente novamente.' })
      return
    }
    socketRef.current.send(JSON.stringify({ type: 'finish_game' }))
  }

  const leaveRoom = async () => {
    if (!room || !player) return
    setLoading(true)
    try {
      await api.leaveRoom(room.code, player.id)
      socketRef.current?.close()
      setRoom(null)
      setQuestion(null)
      setQuestionNumber(0)
      currentQuestionIdRef.current = null
      setRanking([])
      setScreen('home')
      setNotice(null)
      void refreshRooms()
    } catch (error) {
      setNotice({ kind: 'error', text: errorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  const leaveSession = () => {
    socketRef.current?.close()
    localStorage.removeItem(SESSION_KEY)
    setSession(null)
    setRoom(null)
    setQuestion(null)
    setScreen('login')
    setNotice(null)
  }

  const players: Player[] = useMemo(
    () => room?.players.map((id) => ({
      id,
      nickname: id === player?.id ? player.nickname : `Jogador ${shortId(id)}`,
    })) ?? [],
    [room?.players, player],
  )

  const openRoom = (selected: Room) => void enterRoom(selected.code)

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => session && setScreen('home')} aria-label="Ir para início">
          <span className="brand-mark"><Sparkles size={19} /></span>
          <span>trivia<span className="brand-dot">.</span></span>
        </button>
        <div className="topbar-right">
          {session && <span className="player-chip"><span className="avatar">{session.player.nickname.slice(0, 1).toUpperCase()}</span>{session.player.nickname}</span>}
          {session && <button className="icon-button" onClick={leaveSession} aria-label="Sair da conta" title="Sair"><LogOut size={18} /></button>}
        </div>
      </header>

      {notice && (
        <div className={`notice ${notice.kind}`} role="alert">
          <span>{notice.text}</span>
          <button onClick={() => setNotice(null)} aria-label="Fechar aviso"><X size={16} /></button>
        </div>
      )}

      <main>
        {screen === 'login' && (
          <section className="login-layout">
            <div className="login-copy">
              <span className="eyebrow"><span className="eyebrow-dot" /> DESAFIE SEUS AMIGOS</span>
              <h1>Conhecimento<br />também é <span className="highlight">diversão.</span></h1>
              <p>Entre em uma sala, responda em tempo real e descubra quem sabe mais.</p>
              <div className="login-stat-row">
                <div><strong>01</strong><span>Escolha uma sala</span></div>
                <div><strong>02</strong><span>Responda rápido</span></div>
                <div><strong>03</strong><span>Suba no ranking</span></div>
              </div>
              <div className="decor-card" aria-hidden="true">
                <div className="decor-spark">✳</div><div className="decor-orbit orbit-one" /><div className="decor-orbit orbit-two" />
                <div className="decor-note"><Trophy size={19} /><span>Seu próximo<br /><b>grande momento</b></span></div>
              </div>
            </div>
            <form className="login-card" onSubmit={handleLogin}>
              <div className="card-icon"><Gamepad2 size={21} /></div>
              <span className="eyebrow">COMECE AGORA</span>
              <h2>Jogue como convidado</h2>
              <p>Sem cadastro. Escolha como quer aparecer na partida.</p>
              <label htmlFor="nickname">Seu apelido</label>
              <input id="nickname" value={nickname} onChange={(event) => setNickname(event.target.value)} maxLength={32} placeholder="Ex.: Ana" autoComplete="nickname" autoFocus />
              <button className="button primary full" type="submit" disabled={loading}>
                {loading ? <LoaderCircle className="spin" size={18} /> : <>Entrar no jogo <ArrowRight size={17} /></>}
              </button>
              <div className="privacy-note"><LockKeyhole size={14} /> Seus dados não são compartilhados.</div>
            </form>
          </section>
        )}

        {screen === 'home' && (
          <section className="home-page">
            <div className="welcome-banner">
              <div className="welcome-copy">
                <span className="eyebrow light"><span className="eyebrow-dot" /> SUA PRÓXIMA PARTIDA COMEÇA AQUI</span>
                <h1>Oi, {player?.nickname}!<br /><span>Vamos jogar?</span></h1>
                <p>Crie um desafio ou encontre uma sala aberta para entrar.</p>
                <div className="welcome-actions">
                  <button className="button lime" onClick={() => setModal('create')}><Plus size={18} /> Criar sala</button>
                  <button className="button glass" onClick={() => setModal('join')}><KeyRound size={17} /> Usar código</button>
                </div>
              </div>
              <div className="welcome-art" aria-hidden="true">
                <div className="art-circle"><span>?</span></div><div className="art-pill pill-a">A</div><div className="art-pill pill-b">B</div><div className="art-pill pill-c">C</div>
                <div className="art-caption"><span className="live-dot" /> TRIVIA NIGHT</div>
              </div>
            </div>

            <div className="section-heading">
              <div><span className="eyebrow">AO VIVO AGORA</span><h2>Salas públicas</h2></div>
              <button className="button subtle" onClick={() => void refreshRooms()} disabled={loading}><RefreshCw size={15} className={loading ? 'spin' : ''} /> Atualizar</button>
            </div>

            {loading && rooms.length === 0 ? (
              <div className="empty-state"><LoaderCircle className="spin" size={25} /><span>Buscando salas...</span></div>
            ) : rooms.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon"><DoorOpen size={22} /></div>
                <h3>Nenhuma sala aberta por enquanto</h3>
                <p>Seja o primeiro a criar uma e chamar a galera.</p>
                <button className="button primary" onClick={() => setModal('create')}><Plus size={17} /> Criar sala</button>
              </div>
            ) : (
              <div className="room-grid">
                {rooms.map((item) => {
                  const packageName = packages.find((itemPackage) => itemPackage.id === item.package_id)?.name
                  return (
                    <article className="room-card" key={item.code}>
                      <div className="room-card-top">
                        <span className="room-category"><BookOpen size={14} /> {packageName ?? `Pacote #${item.package_id}`}</span>
                        <span className="status-pill"><span /> Aberta</span>
                      </div>
                      <h3>Sala de {item.players.includes(item.host_id) ? ` ${shortId(item.host_id)}` : 'Trivia'}</h3>
                      <div className="room-meta">
                        <span><Users size={15} /> {item.players.length}/{item.max_players}</span>
                        <span><CircleHelp size={15} /> {item.question_count} perguntas</span>
                        <span><Clock3 size={15} /> {item.time_per_question}s</span>
                      </div>
                      <div className="room-card-bottom">
                        <span className="room-code">#{item.code}</span>
                        <button className="button dark small" onClick={() => openRoom(item)} disabled={loading}>Entrar <ArrowRight size={15} /></button>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        )}

        {screen === 'lobby' && room && (
          <section className="lobby-page">
            <button className="back-link" onClick={() => { setRoom(null); setScreen('home'); void refreshRooms() }}><ArrowLeft size={16} /> Voltar às salas</button>
            <div className="lobby-header">
              <div>
                <span className="eyebrow"><span className="eyebrow-dot" /> SALA DE ESPERA</span>
                <h1>Está quase na hora<span className="highlight">.</span></h1>
                <p>Compartilhe o código e espere todo mundo chegar.</p>
              </div>
              <div className="room-code-panel"><span>CÓDIGO DA SALA</span><strong>{room.code}</strong><small><Radio size={13} /> Convide seus amigos</small></div>
            </div>
            <div className="lobby-columns">
              <div className="panel players-panel">
                <div className="panel-heading"><div><Users size={18} /><h2>Jogadores</h2></div><span className="count-pill">{players.length} / {room.max_players}</span></div>
                <div className="player-list">
                  {players.map((item, index) => (
                    <div className="player-row" key={item.id}>
                      <span className={`player-avatar avatar-${index % 5}`}>{item.nickname.slice(0, 1).toUpperCase()}</span>
                      <span className="player-name">{item.nickname}{item.id === player?.id && <small>VOCÊ</small>}</span>
                      {item.id === room.host_id && <span className="host-badge"><Crown size={13} /> HOST</span>}
                    </div>
                  ))}
                  {Array.from({ length: Math.max(0, Math.min(room.max_players - players.length, 3)) }).map((_, index) => (
                    <div className="player-row waiting-row" key={`waiting-${index}`}><span className="player-avatar"><Plus size={17} /></span><span>Aguardando jogador...</span></div>
                  ))}
                </div>
                <div className={`connection-status ${socketConnected ? 'connected' : ''}`}>
                  {socketConnected ? <Wifi size={15} /> : <WifiOff size={15} />}
                  {socketConnected ? 'Conectado ao jogo em tempo real' : 'Conectando ao jogo em tempo real...'}
                </div>
              </div>
              <aside className="panel details-panel">
                <span className="eyebrow">DETALHES DA PARTIDA</span>
                <h2>{packages.find((item) => item.id === room.package_id)?.name ?? `Pacote #${room.package_id}`}</h2>
                <div className="detail-list">
                  <div><CircleHelp size={16} /><span>Perguntas</span><strong>{room.question_count}</strong></div>
                  <div><Clock3 size={16} /><span>Tempo por pergunta</span><strong>{room.time_per_question}s</strong></div>
                  <div><Users size={16} /><span>Máximo de jogadores</span><strong>{room.max_players}</strong></div>
                  <div><Trophy size={16} /><span>Ranking ao vivo</span><strong>{room.show_ranking ? 'Sim' : 'Não'}</strong></div>
                </div>
                {player?.id === room.host_id ? (
                  <button className="button primary full" onClick={() => void startGame()} disabled={loading || room.players.length === 0}>
                    {loading ? <LoaderCircle className="spin" size={18} /> : <>Começar partida <ArrowRight size={17} /></>}
                  </button>
                ) : (
                  <div className="host-wait"><LoaderCircle size={17} className="spin" /> Aguardando o host começar...</div>
                )}
                <button className="button subtle full leave-button" onClick={() => void leaveRoom()} disabled={loading}>Sair da sala</button>
              </aside>
            </div>
          </section>
        )}

        {screen === 'game' && room && (
          <section className="game-page">
            <div className="game-topline">
              <button className="back-link" onClick={() => setNotice({ kind: 'error', text: 'Você está em uma partida. Use “Encerrar partida” se for o host.' })}><ArrowLeft size={16} /> Sala {room.code}</button>
              <div className={`connection-status compact ${socketConnected ? 'connected' : ''}`}>{socketConnected ? <Wifi size={14} /> : <WifiOff size={14} />}{socketConnected ? 'Ao vivo' : 'Reconectando'}</div>
              {player?.id === room.host_id && <button className="button end-button" onClick={finishGame}>Encerrar partida <X size={15} /></button>}
            </div>
            <div className="game-layout">
              <div className="question-area">
                <div className="question-progress">
                  <span>PERGUNTA <b>{question ? questionNumber : '—'}</b><span className="muted"> / {room.question_count}</span></span>
                  <div className="progress-track"><span style={{ width: `${Math.min(100, (questionNumber / room.question_count) * 100)}%` }} /></div>
                </div>
                <div className={`timer ${remaining <= 5 ? 'urgent' : ''}`}><Clock3 size={17} /><strong>{remaining}</strong><span>seg</span></div>
                <div className="question-card">
                  {question ? (
                    <>
                      <span className="eyebrow">PENSE RÁPIDO</span>
                      <h1>{question.statement}</h1>
                      <div className="answer-grid">
                        {question.options.map((option, index) => {
                          const isCorrect = correctAnswer !== null && option === correctAnswer
                          const isWrong = correctAnswer !== null && option === selectedAnswer && !isCorrect
                          return (
                            <button
                              className={`answer-option ${selectedAnswer === option ? 'selected' : ''} ${isCorrect ? 'correct' : ''} ${isWrong ? 'wrong' : ''}`}
                              key={`${question.id}-${option}`}
                              onClick={() => !answerSent && correctAnswer === null && setSelectedAnswer(option)}
                              disabled={answerSent || correctAnswer !== null}
                            >
                              <span className="answer-letter">{String.fromCharCode(65 + index)}</span>
                              <span>{option}</span>
                              {isCorrect && <Check size={18} />}
                            </button>
                          )
                        })}
                      </div>
                      {correctAnswer !== null && (
                        <div className="answer-feedback">
                          <BadgeCheck size={18} />
                          <div><strong>Resposta correta: {correctAnswer}</strong>{explanation && <p>{explanation}</p>}</div>
                        </div>
                      )}
                      <div className="answer-actions">
                        {answerSent && correctAnswer === null ? <span className="submitted-label"><Check size={16} /> Resposta enviada — aguardando os outros jogadores</span> : (
                          <button className="button primary" onClick={submitAnswer} disabled={!selectedAnswer || answerSent || correctAnswer !== null || remaining === 0}>
                            Enviar resposta <ArrowRight size={17} />
                          </button>
                        )}
                        {remaining === 0 && correctAnswer === null && <span className="muted">Tempo encerrado, aguardando a próxima pergunta.</span>}
                      </div>
                    </>
                  ) : (
                    <div className="question-loading"><LoaderCircle className="spin" size={27} /><h2>Preparando a pergunta...</h2><p>A partida vai começar em instantes.</p></div>
                  )}
                </div>
              </div>
              <aside className="panel ranking-panel">
                <div className="panel-heading"><div><Trophy size={18} /><h2>Ranking</h2></div><span className="live-label"><span /> AO VIVO</span></div>
                {!room.show_ranking ? (
                  <div className="ranking-empty"><LockKeyhole size={21} /><p>O host ocultou o ranking durante a partida.</p></div>
                ) : ranking.length ? (
                  <div className="ranking-list">
                    {ranking.map((entry, index) => (
                      <div className={`ranking-row ${entry.user_id === player?.id ? 'me' : ''}`} key={entry.user_id}>
                        <span className={`rank-number rank-${index + 1}`}>{index === 0 ? <Medal size={17} /> : `0${index + 1}`}</span>
                        <span className="ranking-avatar">{entry.user_id === player?.id ? player.nickname.slice(0, 1).toUpperCase() : '•'}</span>
                        <span className="ranking-name">{entry.user_id === player?.id ? player.nickname : entry.nickname}</span>
                        <strong>{entry.score}</strong>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="ranking-empty"><Trophy size={23} /><p>O ranking aparece assim que a primeira pergunta for respondida.</p></div>
                )}
                <div className="ranking-footer"><Users size={15} /> {room.players.length} jogadores na partida</div>
              </aside>
            </div>
          </section>
        )}

        {screen === 'results' && room && (
          <section className="results-page">
            <div className="results-confetti" aria-hidden="true">✦　✧　✳　✦　✧</div>
            <span className="eyebrow"><span className="eyebrow-dot" /> PARTIDA ENCERRADA</span>
            <div className="results-trophy"><Trophy size={34} /></div>
            <h1>Mandaram <span className="highlight">bem!</span></h1>
            <p className="results-subtitle">A sala {room.code} chegou ao fim. Confira o resultado.</p>
            <div className="results-board">
              <div className="panel-heading"><div><Medal size={18} /><h2>Classificação final</h2></div></div>
              {ranking.length ? ranking.map((entry, index) => (
                <div className={`result-row ${index === 0 ? 'winner' : ''}`} key={entry.user_id}>
                  <span className={`result-place place-${index + 1}`}>{index === 0 ? <Crown size={17} /> : `${index + 1}º`}</span>
                  <span className="ranking-avatar">{entry.user_id === player?.id ? player.nickname.slice(0, 1).toUpperCase() : '•'}</span>
                  <span className="ranking-name">{entry.user_id === player?.id ? `${player.nickname} (você)` : entry.nickname}</span>
                  <strong>{entry.score}<small> pts</small></strong>
                </div>
              )) : <p className="no-results">O serviço não retornou pontuações para esta partida.</p>}
            </div>
            <button className="button primary" onClick={() => { setRoom(null); setQuestion(null); setQuestionNumber(0); currentQuestionIdRef.current = null; setRanking([]); setScreen('home'); void refreshRooms() }}>Voltar para salas <ArrowRight size={17} /></button>
          </section>
        )}
      </main>

      {modal === 'create' && (
        <CreateRoomModal
          packages={packages}
          playerId={player?.id ?? ''}
          loading={loading}
          onClose={() => setModal(null)}
          onCreate={(values) => void createRoom(values)}
          onRefreshPackages={() => player ? api.listPackages(player.id).then(setPackages).catch((error: unknown) => setNotice({ kind: 'error', text: errorMessage(error) })) : undefined}
        />
      )}
      {modal === 'join' && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && setModal(null)}>
          <form className="modal-card compact-modal" onSubmit={(event) => { event.preventDefault(); void enterRoom(joinCode, joinPassword) }}>
            <button className="modal-close" type="button" onClick={() => setModal(null)} aria-label="Fechar"><X size={19} /></button>
            <div className="card-icon"><KeyRound size={20} /></div><span className="eyebrow">ENTRAR EM UMA PARTIDA</span>
            <h2>Tem um código?</h2><p>Digite o código da sala para entrar direto no lobby.</p>
            <label htmlFor="room-code">Código da sala</label>
            <input id="room-code" value={joinCode} onChange={(event) => setJoinCode(event.target.value.toUpperCase())} placeholder="Ex.: A2B3CD" maxLength={12} required autoFocus />
            <label htmlFor="room-password">Senha <span className="optional">(se necessário)</span></label>
            <input id="room-password" type="password" value={joinPassword} onChange={(event) => setJoinPassword(event.target.value)} placeholder="Sala privada" />
            <button className="button primary full" type="submit" disabled={loading}>{loading ? <LoaderCircle className="spin" size={18} /> : <>Entrar na sala <ArrowRight size={17} /></>}</button>
          </form>
        </div>
      )}
    </div>
  )
}

function CreateRoomModal({
  packages,
  playerId,
  loading,
  onClose,
  onCreate,
  onRefreshPackages,
}: {
  packages: QuestionPackage[]
  playerId: string
  loading: boolean
  onClose: () => void
  onCreate: (values: {
    package_id: number
    question_count: number
    max_players: number
    time_per_question: number
    is_private: boolean
    password: string | null
    show_ranking: boolean
  }) => void
  onRefreshPackages: () => void
}) {
  const [packageId, setPackageId] = useState('')
  const [questionCount, setQuestionCount] = useState(10)
  const [maxPlayers, setMaxPlayers] = useState(8)
  const [timePerQuestion, setTimePerQuestion] = useState(20)
  const [isPrivate, setIsPrivate] = useState(false)
  const [password, setPassword] = useState('')
  const [showRanking, setShowRanking] = useState(true)
  const [availableQuestions, setAvailableQuestions] = useState<number | null>(null)
  const [checkingQuestions, setCheckingQuestions] = useState(false)
  const [questionLoadError, setQuestionLoadError] = useState('')
  const [questionRetry, setQuestionRetry] = useState(0)

  useEffect(() => {
    if (packages.length && !packageId) setPackageId(String(packages[0].id))
  }, [packages, packageId])

  useEffect(() => {
    if (!packageId || !playerId) return
    let active = true
    setCheckingQuestions(true)
    setAvailableQuestions(null)
    setQuestionLoadError('')
    api.listGameQuestions(Number(packageId), playerId)
      .then((questions) => {
        if (!active) return
        setAvailableQuestions(questions.length)
        if (questions.length > 0) {
          setQuestionCount((count) => Math.min(count, questions.length))
        }
      })
      .catch((error: unknown) => {
        if (active) setQuestionLoadError(errorMessage(error))
      })
      .finally(() => {
        if (active) setCheckingQuestions(false)
      })
    return () => { active = false }
  }, [packageId, playerId, questionRetry])

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <form className="modal-card create-modal" onSubmit={(event) => {
        event.preventDefault()
        onCreate({
          package_id: Number(packageId),
          question_count: questionCount,
          max_players: maxPlayers,
          time_per_question: timePerQuestion,
          is_private: isPrivate,
          password: isPrivate ? password : null,
          show_ranking: showRanking,
        })
      }}>
        <button className="modal-close" type="button" onClick={onClose} aria-label="Fechar"><X size={19} /></button>
        <div className="card-icon"><Plus size={20} /></div><span className="eyebrow">SEU JOGO, SUAS REGRAS</span>
        <h2>Criar uma sala</h2><p>Configure a partida e convide seus amigos.</p>
        {packages.length === 0 ? (
          <div className="package-empty"><BookOpen size={20} /><span>Nenhum pacote de perguntas disponível.</span><small>Crie ou publique pacotes no Trivia Service e atualize a lista.</small><button type="button" className="button subtle" onClick={onRefreshPackages}><RefreshCw size={14} /> Atualizar pacotes</button></div>
        ) : (
          <>
            <label htmlFor="question-package">Pacote de perguntas</label>
            <select id="question-package" value={packageId} onChange={(event) => setPackageId(event.target.value)} required>
              {packages.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
            </select>
            {checkingQuestions && <small className="field-note">Verificando perguntas disponíveis...</small>}
            {!checkingQuestions && availableQuestions !== null && availableQuestions > 0 && <small className="field-note">{availableQuestions} perguntas disponíveis neste pacote.</small>}
            {!checkingQuestions && availableQuestions === 0 && <small className="field-error">Este pacote ainda não tem perguntas disponíveis.</small>}
            {questionLoadError && <div className="field-error">{questionLoadError} <button type="button" onClick={() => setQuestionRetry((count) => count + 1)}>Tentar novamente</button></div>}
            <div className="form-grid">
              <div><label htmlFor="question-count">Perguntas</label><input id="question-count" type="number" min={1} max={availableQuestions ?? 100} value={questionCount} onChange={(event) => setQuestionCount(Number(event.target.value))} disabled={checkingQuestions || availableQuestions === 0 || Boolean(questionLoadError)} required /></div>
              <div><label htmlFor="max-players">Jogadores</label><input id="max-players" type="number" min={1} max={100} value={maxPlayers} onChange={(event) => setMaxPlayers(Number(event.target.value))} required /></div>
              <div className="wide-field"><label htmlFor="question-time">Tempo por pergunta (segundos)</label><input id="question-time" type="number" min={5} max={300} value={timePerQuestion} onChange={(event) => setTimePerQuestion(Number(event.target.value))} required /></div>
            </div>
            <label className="check-line"><input type="checkbox" checked={showRanking} onChange={(event) => setShowRanking(event.target.checked)} /><span>Mostrar ranking durante a partida</span></label>
            <label className="check-line"><input type="checkbox" checked={isPrivate} onChange={(event) => setIsPrivate(event.target.checked)} /><span>Sala privada com senha</span></label>
            {isPrivate && <input aria-label="Senha da sala" type="password" minLength={1} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Defina uma senha" required />}
          </>
        )}
        <div className="modal-actions">
          <button className="button subtle" type="button" onClick={onClose}>Cancelar</button>
          {packages.length > 0 && <button className="button primary" type="submit" disabled={loading || checkingQuestions || availableQuestions === 0 || Boolean(questionLoadError) || !packageId}>{loading ? <LoaderCircle className="spin" size={18} /> : <>Criar sala <ArrowRight size={17} /></>}</button>}
        </div>
      </form>
    </div>
  )
}

export default App
