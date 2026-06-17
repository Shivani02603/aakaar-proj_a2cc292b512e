export interface JwtPayload {
  sub: string
  email: string
  exp: number
  iat: number
}

export const getToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null
  }
  return localStorage.getItem('token')
}

export const setToken = (token: string): void => {
  if (typeof window === 'undefined') {
    return
  }
  localStorage.setItem('token', token)
}

export const removeToken = (): void => {
  if (typeof window === 'undefined') {
    return
  }
  localStorage.removeItem('token')
}

export const isAuthenticated = (): boolean => {
  const token = getToken()
  if (!token) return false

  try {
    const payload = parseJwt(token)
    const currentTime = Math.floor(Date.now() / 1000)
    return payload.exp > currentTime
  } catch {
    return false
  }
}

export const getUser = (): JwtPayload | null => {
  const token = getToken()
  if (!token) return null

  try {
    return parseJwt(token)
  } catch {
    return null
  }
}

export const parseJwt = (token: string): JwtPayload => {
  const base64Url = token.split('.')[1]
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  )
  return JSON.parse(jsonPayload)
}