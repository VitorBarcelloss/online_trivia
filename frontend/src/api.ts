export interface Player {
  id: string
  nickname: string
}

export interface Session {
  player: Player
  accessToken: string
  refreshToken: string
}

export interface Room {
  id: string
  code: string
  host_id: string
  package_id: number
  question_count: number
  max_players: number
  time_per_question: number
  is_private: boolean
  show_ranking: boolean
  status: 'WAITING' | 'IN_PROGRESS' | 'FINISHED'
  players: string[]
  game_id: string | null
}

export interface QuestionPackage {
  id: number
  name: string
  description: string | null
  is_public: boolean
}

export interface Question {
  id: string | number
  order: number
  statement: string
  options: string[]
}

export interface RankingEntry {
  user_id: string
  nickname: string
  score: number
}

const SERVICE = {
  user: '/api/user',
  trivia: '/api/trivia',
  room: '/api/room',
  game: '/api/game',
} as const

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...init?.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null) as
      | { detail?: string | { message?: string }; message?: string }
      | null
    const detail = typeof body?.detail === 'string'
      ? body.detail
      : body?.detail?.message ?? body?.message
    throw new Error(detail || `Falha na requisição (${response.status}).`)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

function query(values: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value))
  })
  return params.toString()
}

export const api = {
  async loginAsGuest(nickname: string): Promise<Session> {
    const tokens = await request<{ access_token: string; refresh_token: string }>(
      `${SERVICE.user}/auth/login`,
      {
        method: 'POST',
        body: JSON.stringify({
          is_guest: true,
          nickname,
          email: null,
          password: null,
        }),
      },
    )
    return {
      player: { id: crypto.randomUUID(), nickname },
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
    }
  },

  listRooms(): Promise<Room[]> {
    return request(`${SERVICE.room}/rooms`)
  },

  getRoom(code: string): Promise<Room> {
    return request(`${SERVICE.room}/rooms/${encodeURIComponent(code)}`)
  },

  listPackages(playerId: string): Promise<QuestionPackage[]> {
    return request(
      `${SERVICE.trivia}/question-packages?${query({ player_id: playerId })}`,
    )
  },

  listGameQuestions(packageId: number, playerId: string): Promise<unknown[]> {
    return request(
      `${SERVICE.trivia}/question-packages/${packageId}/game-questions?${query({ player_id: playerId })}`,
    )
  },

  createRoom(
    playerId: string,
    values: {
      package_id: number
      question_count: number
      max_players: number
      time_per_question: number
      is_private: boolean
      password: string | null
      show_ranking: boolean
    },
  ): Promise<Room> {
    const idempotencyKey = crypto.randomUUID()
    return request(
      `${SERVICE.room}/rooms?${query({ host_id: playerId })}`,
      {
        method: 'POST',
        headers: { 'Idempotency-Key': idempotencyKey },
        body: JSON.stringify(values),
      },
    )
  },

  joinRoom(code: string, playerId: string, password?: string): Promise<Room> {
    return request(
      `${SERVICE.room}/rooms/${encodeURIComponent(code)}/players?${query({ player_id: playerId })}`,
      {
        method: 'POST',
        body: JSON.stringify({ password: password || null }),
      },
    )
  },

  startGame(code: string, playerId: string): Promise<Room> {
    return request(
      `${SERVICE.room}/rooms/${encodeURIComponent(code)}/start?${query({ player_id: playerId })}`,
      { method: 'POST' },
    )
  },

  leaveRoom(code: string, playerId: string): Promise<void> {
    return request(
      `${SERVICE.room}/rooms/${encodeURIComponent(code)}/players/${encodeURIComponent(playerId)}`,
      { method: 'DELETE' },
    )
  },

  getGame(gameId: string): Promise<{
    id: string
    status: string
    question: Question | null
    ranking: RankingEntry[]
    question_time: number
  }> {
    return request(`${SERVICE.game}/games/${encodeURIComponent(gameId)}`)
  },
}

export function gameSocketUrl(roomCode: string, playerId: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const params = new URLSearchParams({ player_id: playerId })
  return `${protocol}//${window.location.host}/ws/${encodeURIComponent(roomCode)}?${params}`
}
