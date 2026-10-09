import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import { getApiErrorMessage } from '../services/errors'

const statusLabels = { TODO: 'برای انجام', IN_PROGRESS: 'در حال انجام', DONE: 'انجام‌شده' }

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)
  const [error, setError] = useState('')

  const loadTasks = async () => {
    setLoading(true)
    setError('')
    try {
      const query = status ? `?status=${encodeURIComponent(status)}` : ''
      const response = await api.get(`/tasks/${query}`)
      setTasks(response.data.results || response.data)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'دریافت وظایف انجام نشد.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTasks() }, [status])

  const updateStatus = async (task, nextStatus) => {
    if (task.status === nextStatus) return
    setUpdatingId(task.id)
    setError('')
    try {
      await api.patch(`/tasks/${task.id}/`, { status: nextStatus })
      await loadTasks()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'تغییر وضعیت وظیفه انجام نشد.'))
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <div className="dashboard" dir="rtl">
      <Sidebar />
      <main className="main-content">
        <div className="topbar">
          <div><h1>همه وظایف</h1><p>وظایف Workspaceهایی که به آن‌ها دسترسی داری.</p></div>
          <label className="filter-control">
            <span>وضعیت</span>
            <select className="form-input" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">همه وضعیت‌ها</option>
              <option value="TODO">برای انجام</option>
              <option value="IN_PROGRESS">در حال انجام</option>
              <option value="DONE">انجام‌شده</option>
            </select>
          </label>
        </div>

        {error && <div className="auth-error" role="alert">{error}</div>}
        <section className="dashboard-card">
          <div className="card-header"><h3>فهرست وظایف</h3><span>{tasks.length} مورد</span></div>
          {loading ? <div className="empty-state"><p>در حال دریافت وظایف...</p></div> :
            tasks.length === 0 ? <div className="empty-state"><div className="empty-icon">✓</div><strong>وظیفه‌ای پیدا نشد</strong><p>با تغییر فیلتر یا ساخت Task در یک پروژه، وظایف اینجا نمایش داده می‌شوند.</p><Link className="text-link" to="/projects">رفتن به پروژه‌ها</Link></div> :
            <div className="table-wrap"><table className="data-table">
              <thead><tr><th>وظیفه</th><th>مسئول</th><th>شروع</th><th>مهلت</th><th>وضعیت</th><th>پروژه</th></tr></thead>
              <tbody>{tasks.map((task) => <tr key={task.id}>
                <td><strong>{task.title}</strong><div className="muted-cell">{task.description || 'بدون توضیحات'}</div></td>
                <td>{task.assigned_to_name || 'تعیین نشده'}</td>
                <td>{task.started_date ? new Date(task.started_date).toLocaleDateString('fa-IR') : '—'}</td>
                <td>{task.deadline ? new Date(task.deadline).toLocaleDateString('fa-IR') : '—'}</td>
                <td><select aria-label={`وضعیت ${task.title}`} className={`status-select status-${task.status.toLowerCase()}`} value={task.status} disabled={updatingId === task.id} onChange={(event) => updateStatus(task, event.target.value)}>
                  {Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select></td>
                <td><Link className="text-link" to={`/projects/${task.project}`}>مشاهده پروژه</Link></td>
              </tr>)}</tbody>
            </table></div>}
        </section>
      </main>
    </div>
  )
}

export default Tasks
