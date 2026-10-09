import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { getApiErrorMessage } from '../services/errors'

function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    password: '',
    password2: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (form.password !== form.password2) {
      setError('رمز عبور و تکرار آن یکسان نیستند.')
      return
    }

    setLoading(true)
    try {
      await api.post('/auth/register/', {
        email: form.email.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        phone: form.phone.trim(),
        password: form.password,
      })
      navigate('/login', {
        replace: true,
        state: { message: 'حساب کاربری ساخته شد؛ حالا وارد شو.' },
      })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'ثبت‌نام انجام نشد.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page" dir="rtl">
      <div className="auth-wrapper">
        <section className="auth-brand">
          <div className="logo">D</div>
          <h1>شروع کن 🚀</h1>
          <p>فضای کاری خودت رو بساز، تیمت رو اضافه کن و پروژه‌ها رو از یک جا مدیریت کن.</p>
          <div className="auth-features">
            <div className="auth-feature"><span>✓</span>ساخت Workspace</div>
            <div className="auth-feature"><span>✓</span>مدیریت اعضای تیم</div>
            <div className="auth-feature"><span>✓</span>مدیریت پروژه‌ها و Taskها</div>
          </div>
        </section>

        <section className="auth-form-wrapper">
          <form className="auth-form" onSubmit={handleSubmit}>
            <h2>ساخت حساب</h2>
            <p className="auth-form-subtitle">اطلاعاتت رو وارد کن تا شروع کنیم.</p>

            {error && <div className="auth-error" role="alert">{error}</div>}

            <div className="form-group">
              <label htmlFor="first_name">نام</label>
              <input id="first_name" className="form-input" name="first_name" autoComplete="given-name" value={form.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">نام خانوادگی</label>
              <input id="last_name" className="form-input" name="last_name" autoComplete="family-name" value={form.last_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="email">ایمیل</label>
              <input id="email" className="form-input" type="email" name="email" autoComplete="email" placeholder="example@email.com" value={form.email} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="phone">شماره موبایل</label>
              <input id="phone" className="form-input" type="tel" name="phone" inputMode="tel" autoComplete="tel" placeholder="09123456789" pattern="09[0-9]{9}" title="شماره موبایل را با 09 و ۱۱ رقم وارد کن." value={form.phone} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="password">رمز عبور</label>
              <input id="password" className="form-input" type="password" name="password" autoComplete="new-password" value={form.password} onChange={handleChange} minLength={8} required />
            </div>
            <div className="form-group">
              <label htmlFor="password2">تکرار رمز عبور</label>
              <input id="password2" className="form-input" type="password" name="password2" autoComplete="new-password" value={form.password2} onChange={handleChange} required />
            </div>

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? 'در حال ساخت حساب...' : 'ساخت حساب'}
            </button>
            <div className="auth-link">قبلاً حساب ساختی؟ <Link to="/login">وارد شو</Link></div>
          </form>
        </section>
      </div>
    </div>
  )
}

export default Register
