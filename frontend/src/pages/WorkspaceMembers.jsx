import { useEffect, useState } from 'react'
<<<<<<< Updated upstream
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

  const loadMembers = async () => {
    setLoading(true)
    setError('')
    try {
      const [workspaceResponse, membersResponse] = await Promise.all([
        api.get(`/workspaces/${id}/`),
        api.get(`/workspaces/${id}/members/`),
      ])
      setWorkspace(workspaceResponse.data)
      setMembers(membersResponse.data.results || membersResponse.data)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'دریافت اعضای Workspace انجام نشد.'))
=======
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'

function WorkspaceMembers() {
  const { id } = useParams()

  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [workspace, setWorkspace] = useState(null)

  useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true)
      setError('')

      const [workspaceResponse, membersResponse] =
        await Promise.all([
          api.get(`/workspaces/${id}/`),
          api.get(`/workspaces/${id}/members/`),
        ])

      setWorkspace(workspaceResponse.data)

      const data = membersResponse.data

      setMembers(
        Array.isArray(data)
          ? data
          : Array.isArray(data.results)
            ? data.results
            : []
      )

    } catch (error) {
      console.error(error)

      setError(
        error.response?.data?.detail ||
        'دریافت اطلاعات Workspace انجام نشد.'
      )

>>>>>>> Stashed changes
    } finally {
      setLoading(false)
    }
  }

<<<<<<< Updated upstream
  useEffect(() => { loadMembers() }, [id])

  const addMember = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setNotice('')
    try {
      await api.post(`/workspaces/${id}/members/add/`, { email: email.trim() })
      setEmail('')
      setNotice('عضو جدید با موفقیت اضافه شد.')
      await loadMembers()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'افزودن عضو انجام نشد.'))
    } finally {
      setSaving(false)
    }
  }

  const removeMember = async (member) => {
    if (!window.confirm(`عضویت ${member.email} از این Workspace حذف شود؟`)) return
    setRemovingId(member.id)
    setError('')
    setNotice('')
    try {
      await api.delete(`/workspaces/${id}/members/delete/${member.id}/`)
      setMembers((current) => current.filter((item) => item.id !== member.id))
      setNotice('عضو از Workspace حذف شد.')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'حذف عضو انجام نشد.'))
    } finally {
      setRemovingId(null)
    }
=======
  fetchData()
}, [id])

  const getInitial = (member) => {
    if (member.first_name) {
      return member.first_name.charAt(0).toUpperCase()
    }

    if (member.email) {
      return member.email.charAt(0).toUpperCase()
    }

    return 'U'
  }

  const getFullName = (member) => {
    const fullName = `${member.first_name || ''} ${
      member.last_name || ''
    }`.trim()

    return fullName || 'بدون نام'
>>>>>>> Stashed changes
  }

  return (
    <div className="dashboard" dir="rtl">
<<<<<<< Updated upstream
      <Sidebar />
      <main className="main-content">
        <div className="topbar">
          <div>
            <Link className="text-link" to={`/workspaces/${id}`}>← بازگشت به Workspace</Link>
            <h1>اعضای Workspace</h1>
            <p>{workspace?.name || 'مدیریت اعضای فضای کاری'}</p>
          </div>
        </div>
        {error && <div className="auth-error" role="alert">{error}</div>}
        {notice && <div className="success-message" role="status">{notice}</div>}

        <section className="dashboard-card member-add-card">
          <div className="card-header"><h3>افزودن عضو</h3></div>
          <p className="muted-cell">فقط مالک Workspace می‌تواند عضو اضافه یا حذف کند. ایمیل باید متعلق به یک حساب ثبت‌شده باشد.</p>
          <form className="inline-form" onSubmit={addMember}>
            <div className="form-group">
              <label htmlFor="member-email">ایمیل کاربر</label>
              <input id="member-email" className="form-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="user@example.com" required />
            </div>
            <button className="primary-button" type="submit" disabled={saving}>{saving ? 'در حال افزودن...' : 'افزودن عضو'}</button>
          </form>
        </section>

        <section className="dashboard-card">
          <div className="card-header"><h3>اعضا</h3><span>{members.length} نفر</span></div>
          {loading ? <div className="empty-state"><p>در حال دریافت اعضا...</p></div> :
            members.length === 0 ? <div className="empty-state"><strong>عضوی وجود ندارد</strong></div> :
            <div className="member-list">{members.map((member) => {
              const isOwner = Number(workspace?.owner) === Number(member.id)
              const name = [member.first_name, member.last_name].filter(Boolean).join(' ') || member.email
              return <div className="member-row" key={member.id}>
                <div className="avatar">{name.charAt(0).toUpperCase()}</div>
                <div className="member-details"><strong>{name}</strong><span>{member.email}</span></div>
                {isOwner ? <span className="role-pill">مالک</span> : <button type="button" className="danger-button" disabled={removingId === member.id} onClick={() => removeMember(member)}>{removingId === member.id ? 'در حال حذف...' : 'حذف عضو'}</button>}
              </div>
            })}</div>}
        </section>
      </main>
=======

      <Sidebar workspaceId={id} />

      <main className="main-content">

        {/* Header */}

        <div className="topbar">

          <div>
            <div
                style={{
                  color: '#64748b',
                  fontSize: '13px',
                  marginBottom: '8px',
                }}
            >
              Workspace / {workspace?.name || 'در حال دریافت...'}
            </div>

            <h1>
              اعضای {workspace?.name}
            </h1>

            <p>
              اعضای Workspace «{workspace?.name || '...'}» را مشاهده و مدیریت کن.
            </p>
          </div>

          <Link
              to={`/workspaces/${id}`}
              style={{
                color: '#818cf8',
                fontSize: '13px',
                textDecoration: 'none',
              }}
          >
            ← بازگشت به Workspace
          </Link>

        </div>


        {/* Stats */}

        {!loading && !error && (
          <div className="stats-grid">

            <div className="stat-card">

              <div className="stat-card-header">
                تعداد اعضا

                <div className="stat-icon">
                  👥
                </div>
              </div>

              <div className="stat-value">
                {members.length}
              </div>

            </div>


            <div className="stat-card">

              <div className="stat-card-header">
                وضعیت

                <div className="stat-icon">
                  ●
                </div>
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


        {/* Members Card */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <h3>
                لیست اعضا
              </h3>



            </div>

            {!loading && !error && (
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


          {/* Loading */}

          {loading && (

            <div className="empty-state">

              <div className="empty-icon">
                ⏳
              </div>

              <strong>
                در حال دریافت اعضا...
              </strong>

              <p>
                لطفاً کمی صبر کنید.
              </p>

            </div>

          )}


          {/* Error */}

          {!loading && error && (

            <div className="empty-state">

              <div className="empty-icon">
                ⚠️
              </div>

              <strong>
                خطا در دریافت اعضا
              </strong>

              <p>
                {error}
              </p>

              <Link
                to={`/workspaces/${id}`}
                style={{
                  color: '#818cf8',
                  marginTop: '12px',
                  textDecoration: 'none',
                  fontSize: '13px',
                }}
              >
                بازگشت به Workspace
              </Link>

            </div>

          )}


          {/* Empty */}

          {!loading &&
            !error &&
            members.length === 0 && (

              <div className="empty-state">

                <div className="empty-icon">
                  👥
                </div>

                <strong>
                  هنوز عضوی وجود ندارد
                </strong>



              </div>

            )}


          {/* Members */}

          {!loading &&
            !error &&
            members.length > 0 && (

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '14px',
                }}
              >

                {members.map((member) => (

                  <div
                    key={member.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '14px',
                      padding: '16px',
                      background: '#111827',
                      border: '1px solid #1e293b',
                      borderRadius: '14px',
                      transition: 'all 0.2s ease',
                    }}
                  >

                    {/* Avatar */}

                    <div
                      style={{
                        width: '48px',
                        height: '48px',
                        minWidth: '48px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background:
                          'rgba(99, 102, 241, 0.14)',
                        border:
                          '1px solid rgba(99, 102, 241, 0.25)',
                        color: '#818cf8',
                        fontSize: '17px',
                        fontWeight: '600',
                      }}
                    >
                      {getInitial(member)}
                    </div>


                    {/* Info */}

                    <div
                      style={{
                        minWidth: 0,
                        flex: 1,
                      }}
                    >

                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          marginBottom: '5px',
                        }}
                      >

                        <strong
                          style={{
                            color: '#f8fafc',
                            fontSize: '14px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {getFullName(member)}
                        </strong>

                      </div>


                      <div
                        style={{
                          color: '#64748b',
                          fontSize: '12px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          direction: 'ltr',
                          textAlign: 'right',
                        }}
                      >
                        {member.email}
                      </div>

                    </div>

                  </div>

                ))}

              </div>

            )}

        </div>

      </main>

>>>>>>> Stashed changes
    </div>
  )
}

<<<<<<< Updated upstream
export default WorkspaceMembers
=======
export default WorkspaceMembers
>>>>>>> Stashed changes
