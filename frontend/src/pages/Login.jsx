import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { getApiErrorMessage } from '../services/errors'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login/', {
        email,
        password,
      })

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)

      navigate('/')
    } catch (error) {
      setError(getApiErrorMessage(error, 'ایمیل یا رمز عبور اشتباه است.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page" dir="rtl">
      <div className="auth-wrapper">

        <div className="auth-brand">
          <div className="logo">D</div>

          <h1>DevFlow</h1>

          <p>
            مدیریت پروژه، تیم و وظایف در یک محیط ساده،
            سریع و حرفه‌ای.
          </p>

          <div className="auth-features">
            <div className="auth-feature">
              <span>✓</span>
              مدیریت Workspace و اعضای تیم
            </div>

            <div className="auth-feature">
              <span>✓</span>
              مدیریت پروژه و Taskها
            </div>

            <div className="auth-feature">
              <span>✓</span>
              ثبت تاریخچه تمام فعالیت‌ها
            </div>
          </div>
        </div>

        <div className="auth-form-wrapper">
          <form className="auth-form" onSubmit={handleSubmit}>

            <h2>خوش برگشتی 👋</h2>

            <p className="auth-form-subtitle">
              برای ورود به DevFlow اطلاعاتت رو وارد کن.
            </p>
            {location.state?.message && <div className="success-message" role="status">{location.state.message}</div>}

            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}

            <div className="form-group">
              <label>ایمیل</label>

              <input
                className="form-input"
                type="email"
                placeholder="example@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>رمز عبور</label>

              <input
                className="form-input"
                type="password"
                placeholder="رمز عبور خود را وارد کنید"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={loading}
            >
              {loading ? 'در حال ورود...' : 'ورود به حساب'}
            </button>

            <div className="auth-link">
              حساب کاربری نداری؟
              {' '}
              <Link to="/register">
                ثبت‌نام کن
              </Link>
            </div>

          </form>
        </div>

      </div>
    </div>
  )
}

export default Login