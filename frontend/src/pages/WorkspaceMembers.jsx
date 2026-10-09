import { useEffect, useState } from 'react'
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
    } finally {
      setLoading(false)
    }
  }

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
  }

  return (
    <div className="dashboard" dir="rtl">
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
    </div>
  )
}

export default WorkspaceMembers
