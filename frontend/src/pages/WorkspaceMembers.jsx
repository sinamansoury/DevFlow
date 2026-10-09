
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import { getApiErrorMessage } from '../services/errors'

function WorkspaceMembers() {
  const { id } = useParams()

  const [workspace, setWorkspace] = useState(null)
  const [members, setMembers] = useState([])
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [removingId, setRemovingId] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadMembers = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [workspaceResponse, membersResponse] = await Promise.all([
        api.get(`/workspaces/${id}/`),
        api.get(`/workspaces/${id}/members/`),
      ])

      setWorkspace(workspaceResponse.data)

      const data = membersResponse.data
      const results = Array.isArray(data)
        ? data
        : Array.isArray(data.results)
          ? data.results
          : []

      setMembers(results)
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          'دریافت اعضای Workspace انجام نشد.'
        )
      )
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    loadMembers()
  }, [loadMembers])

  const addMember = async (event) => {
    event.preventDefault()

    if (saving || !email.trim()) return

    setSaving(true)
    setError('')
    setNotice('')

    try {
      await api.post(`/workspaces/${id}/members/add/`, {
        email: email.trim(),
      })

      setEmail('')
      setNotice('عضو جدید با موفقیت اضافه شد.')

      await loadMembers()
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          'افزودن عضو انجام نشد.'
        )
      )
    } finally {
      setSaving(false)
    }
  }

  const removeMember = async (member) => {
    const confirmed = window.confirm(
      `عضویت ${member.email} از این Workspace حذف شود؟`
    )

    if (!confirmed || removingId !== null) return

    setRemovingId(member.id)
    setError('')
    setNotice('')

    try {
      await api.delete(
        `/workspaces/${id}/members/delete/${member.id}/`
      )

      setMembers((current) =>
        current.filter((item) => item.id !== member.id)
      )

      setNotice('عضو از Workspace حذف شد.')
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          'حذف عضو انجام نشد.'
        )
      )
    } finally {
      setRemovingId(null)
    }
  }

  const getInitial = (member) => {
    const name = member.first_name || member.email || 'U'
    return name.charAt(0).toUpperCase()
  }

  const getFullName = (member) => {
    const fullName = [
      member.first_name,
      member.last_name,
    ]
      .filter(Boolean)
      .join(' ')
      .trim()

    return fullName || member.email || 'بدون نام'
  }

  const isOwner = (member) => {
    const owner = workspace?.owner
    const ownerId =
      owner && typeof owner === 'object' ? owner.id : owner

    return (
      ownerId !== undefined &&
      ownerId !== null &&
      String(ownerId) === String(member.id)
    )
  }

  return (
    <div className="dashboard" dir="rtl">
      <Sidebar />

      <main className="main-content">
        <div className="topbar">
          <div>
            <Link
              className="text-link"
              to={`/workspaces/${id}`}
            >
              ← بازگشت به Workspace
            </Link>

            <h1>
              اعضای {workspace?.name || 'Workspace'}
            </h1>

            <p>
              اعضای این فضای کاری رو مشاهده و مدیریت کن.
            </p>
          </div>
        </div>

        {error && (
          <div className="auth-error" role="alert">
            {error}
          </div>
        )}

        {notice && (
          <div className="success-message" role="status">
            {notice}
          </div>
        )}

        {!loading && !error && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-card-header">
                تعداد اعضا
                <div className="stat-icon">👥</div>
              </div>

              <div className="stat-value">
                {members.length}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-header">
                وضعیت
                <div className="stat-icon">●</div>
              </div>

              <div
                className="stat-value"
                style={{
                  fontSize: '16px',
                  color: '#34d399',
                }}
              >
                فعال
              </div>
            </div>
          </div>
        )}

        <section className="dashboard-card member-add-card">
          <div className="card-header">
            <h3>افزودن عضو</h3>
          </div>

          <p className="muted-cell">
            فقط مالک Workspace می‌تواند اعضا را مدیریت کند.
            ایمیل باید متعلق به یک حساب ثبت‌شده باشد.
          </p>

          <form className="inline-form" onSubmit={addMember}>
            <div className="form-group">
              <label htmlFor="member-email">
                ایمیل کاربر
              </label>

              <input
                id="member-email"
                className="form-input"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="user@example.com"
                required
              />
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={saving || !email.trim()}
            >
              {saving ? 'در حال افزودن...' : 'افزودن عضو'}
            </button>
          </form>
        </section>

        <section className="dashboard-card">
          <div className="card-header">
            <h3>لیست اعضا</h3>

            {!loading && (
              <span
                style={{
                  color: '#94a3b8',
                  fontSize: '12px',
                }}
              >
                {members.length} عضو
              </span>
            )}
          </div>

          {loading ? (
            <div className="empty-state">
              <div className="empty-icon">⏳</div>
              <strong>در حال دریافت اعضا...</strong>
              <p>لطفاً کمی صبر کن.</p>
            </div>
          ) : error && members.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">⚠️</div>
              <strong>دریافت اطلاعات انجام نشد.</strong>
              <button
                type="button"
                className="secondary-button"
                onClick={loadMembers}
                style={{ marginTop: '12px' }}
              >
                تلاش مجدد
              </button>
            </div>
          ) : members.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <strong>هنوز عضوی وجود ندارد</strong>
              <p>می‌تونی اولین عضو رو اضافه کنی.</p>
            </div>
          ) : (
            <div className="member-list">
              {members.map((member) => {
                const ownerMember = isOwner(member)
                const name = getFullName(member)

                return (
                  <div className="member-row" key={member.id}>
                    <div className="avatar">
                      {getInitial(member)}
                    </div>

                    <div className="member-details">
                      <strong>{name}</strong>
                      <span dir="ltr">{member.email}</span>
                    </div>

                    {ownerMember ? (
                      <span className="role-pill">
                        مالک
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="danger-button"
                        disabled={removingId !== null}
                        onClick={() => removeMember(member)}
                      >
                        {removingId === member.id
                          ? 'در حال حذف...'
                          : 'حذف عضو'}
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default WorkspaceMembers

