import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

function Register() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: '',
  })

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    setError('')

    if (form.password !== form.password2) {
      setError('رمز عبور و تکرار آن یکسان نیستند.')
      return
    }

    setLoading(true)

    try {
      await api.post('/auth/register/', {
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
        password: form.password,
        password2: form.password2,
      })

      navigate('/login')
    } catch (error) {
      const data = error.response?.data

      if (typeof data === 'object') {
        setError(
          Object.values(data)
            .flat()
            .join(' ')
        )
      } else {
        setError('ثبت‌نام انجام نشد.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page" dir="rtl">
      <div className="auth-wrapper">

        <div className="auth-brand">
          <div className="logo">D</div>

          <h1>شروع کن 🚀</h1>

          <p>
            فضای کاری خودت رو بساز، تیمت رو اضافه کن
            و پروژه‌ها رو از یک جا مدیریت کن.
          </p>

          <div className="auth-features">
            <div className="auth-feature">
              <span>✓</span>
              ساخت Workspace
            </div>

            <div className="auth-feature">
              <span>✓</span>
              مدیریت اعضای تیم
            </div>

            <div className="auth-feature">
              <span>✓</span>
              مدیریت پروژه‌ها و Taskها
            </div>
          </div>
        </div>

        <div className="auth-form-wrapper">
          <form className="auth-form" onSubmit={handleSubmit}>

            <h2>ساخت حساب</h2>

            <p className="auth-form-subtitle">
              اطلاعاتت رو وارد کن تا شروع کنیم.
            </p>

            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}

            <div className="form-group">
              <label>نام</label>

              <input
                className="form-input"
                name="first_name"
                placeholder="نام"
                value={form.first_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>نام خانوادگی</label>

              <input
                className="form-input"
                name="last_name"
                placeholder="نام خانوادگی"
                value={form.last_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>ایمیل</label>

              <input
                className="form-input"
                type="email"
                name="email"
                placeholder="example@email.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>رمز عبور</label>

              <input
                className="form-input"
                type="password"
                name="password"
                placeholder="رمز عبور"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>تکرار رمز عبور</label>

              <input
                className="form-input"
                type="password"
                name="password2"
                placeholder="تکرار رمز عبور"
                value={form.password2}
                onChange={handleChange}
                required
              />
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={loading}
            >
              {loading ? 'در حال ساخت حساب...' : 'ساخت حساب'}
            </button>

            <div className="auth-link">
              قبلاً حساب ساختی؟
              {' '}
              <Link to="/login">
                وارد شو
              </Link>
            </div>

          </form>
        </div>

      </div>
    </div>
  )
}

export default Register