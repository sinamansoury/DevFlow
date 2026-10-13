import axios from 'axios'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

const AUTH_PATHS = ['/auth/login/', '/auth/register/', '/auth/refresh/']

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

let refreshPromise = null

function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)

  if (!refresh) {
    return Promise.reject(new Error('No refresh token available'))
  }

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${api.defaults.baseURL}/auth/refresh/`, { refresh })
      .then(({ data }) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, data.access)

        if (data.refresh) {
          localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
        }

        return data.access
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

function redirectToLogin() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)

  const { pathname } = window.location
  if (pathname !== '/login' && pathname !== '/register') {
    window.location.assign('/login')
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const isAuthRequest = AUTH_PATHS.some((path) =>
      originalRequest?.url?.includes(path)
    )

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      isAuthRequest
    ) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const accessToken = await refreshAccessToken()
      originalRequest.headers.Authorization = `Bearer ${accessToken}`
      return api(originalRequest)
    } catch {
      redirectToLogin()
      return Promise.reject(error)
    }
  }
)

export default api
