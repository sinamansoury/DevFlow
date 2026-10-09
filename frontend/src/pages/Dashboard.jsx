import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'

function Dashboard() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [workspaces, setWorkspaces] = useState([])
  const [projects, setProjects] = useState([])
  const [tasks, setTasks] = useState([])
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const loadDashboard = async () => {
      try {
        const [userResponse, workspaceResponse, projectResponse, taskResponse] = await Promise.all([
          api.get('/auth/me/'),
          api.get('/workspaces/'),
          api.get('/projects/'),
          api.get('/tasks/'),
        ])
        const activityResponse = await api.get('/audits/').catch(() => ({ data: { results: [] } }))
        if (!active) return
        setUser(userResponse.data)
        setWorkspaces(workspaceResponse.data.results || workspaceResponse.data)
        setProjects(projectResponse.data.results || projectResponse.data)
        setTasks(taskResponse.data.results || taskResponse.data)
        setActivities(activityResponse.data.results || activityResponse.data || [])
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/login', { replace: true })
      } finally {
        if (active) setLoading(false)
      }
    }
    loadDashboard()
    return () => { active = false }
  }, [navigate])

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login', { replace: true })
  }

  const actionLabels = { CREATE: 'ایجاد', UPDATE: 'ویرایش', DELETE: 'حذف', ADD_MEMBER: 'افزودن عضو', REMOVE_MEMBER: 'حذف عضو', UPDATE_STATUS: 'تغییر وضعیت' }

  return (
    <div className="dashboard" dir="rtl">
      <Sidebar />
      <main className="main-content">
        <div className="topbar">
          <div>
            <h1>سلام {user?.first_name || 'دوست من'} 👋</h1>
            <p>به داشبورد DevFlow خوش اومدی.</p>
          </div>
          {user && <div className="user-box">
            <div className="user-info"><strong>{[user.first_name, user.last_name].filter(Boolean).join(' ') || user.email}</strong><span>{user.email}</span></div>
            <div className="avatar">{user.first_name?.charAt(0) || user.email?.charAt(0) || 'U'}</div>
            <button type="button" className="secondary-button" onClick={logout}>خروج</button>
          </div>}
        </div>

        <div className="stats-grid">
          <div className="stat-card"><div className="stat-card-header">Workspaceها <span className="stat-icon">▣</span></div><div className="stat-value">{loading ? '—' : workspaces.length}</div><Link className="text-link" to="/workspaces">مدیریت Workspaceها ←</Link></div>
          <div className="stat-card"><div className="stat-card-header">پروژه‌ها <span className="stat-icon">◫</span></div><div className="stat-value">{loading ? '—' : projects.length}</div><Link className="text-link" to="/projects">مشاهده پروژه‌ها ←</Link></div>
          <div className="stat-card"><div className="stat-card-header">وظایف <span className="stat-icon">✓</span></div><div className="stat-value">{loading ? '—' : tasks.length}</div><Link className="text-link" to="/tasks">پیگیری وظایف ←</Link></div>
          <div className="stat-card"><div className="stat-card-header">فعالیت‌های اخیر <span className="stat-icon">◌</span></div><div className="stat-value">{loading ? '—' : activities.length}</div><Link className="text-link" to="/activities">مشاهده تاریخچه ←</Link></div>
        </div>

        <div className="dashboard-grid">
          <section className="dashboard-card">
            <div className="card-header"><h3>Workspaceهای من</h3><Link className="text-link" to="/workspaces">مشاهده همه</Link></div>
            {loading ? <div className="empty-state"><p>در حال دریافت اطلاعات...</p></div> :
              workspaces.length === 0 ? <div className="empty-state"><div className="empty-icon">▣</div><strong>هنوز Workspace نداری</strong><p>اولین فضای کاری خودت رو ایجاد کن.</p><Link className="primary-button dashboard-cta" to="/workspaces">ساخت Workspace</Link></div> :
              <div>{workspaces.slice(0, 5).map((workspace) => <Link className="workspace-list-item" to={`/workspaces/${workspace.id}`} key={workspace.id}><span className="workspace-list-icon">▣</span><span className="workspace-list-copy"><strong>{workspace.name}</strong><small>{workspace.description || 'بدون توضیحات'}</small></span><span className="text-link">مشاهده ←</span></Link>)}</div>}
          </section>

          <section className="dashboard-card">
            <div className="card-header"><h3>فعالیت اخیر</h3><Link className="text-link" to="/activities">همه فعالیت‌ها</Link></div>
            {loading ? <div className="empty-state"><p>در حال دریافت فعالیت‌ها...</p></div> :
              activities.length === 0 ? <div className="empty-state"><div className="empty-icon">◌</div><strong>فعالیتی وجود ندارد</strong><p>فعالیت‌های ثبت‌شده اینجا نمایش داده می‌شوند.</p></div> :
              <div className="activity-list">{activities.slice(0, 5).map((activity) => <article className="activity-row" key={activity.id}><div className="activity-mark">◌</div><div className="activity-content"><strong>{actionLabels[activity.action] || activity.action} · {activity.entity_name}</strong><p>{activity.entity_type} · {new Date(activity.created_at).toLocaleString('fa-IR')}</p></div></article>)}</div>}
          </section>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
