import { useEffect, useState } from 'react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import { getApiErrorMessage } from '../services/errors'

const actionLabels = {
  CREATE: 'ایجاد', UPDATE: 'ویرایش', DELETE: 'حذف',
  ADD_MEMBER: 'افزودن عضو', REMOVE_MEMBER: 'حذف عضو', UPDATE_STATUS: 'تغییر وضعیت',
}
const entityLabels = { WORKSPACE: 'Workspace', PROJECT: 'پروژه', TASK: 'وظیفه' }

function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [entityType, setEntityType] = useState('')
  const [action, setAction] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const params = new URLSearchParams({ page: String(page) })
        if (entityType) params.set('entity_type', entityType)
        if (action) params.set('action', action)
        const response = await api.get(`/audits/?${params.toString()}`)
        if (active) {
          setLogs(response.data.results || response.data)
          setTotalPages(response.data.count ? Math.ceil(response.data.count / 9) : 1)
        }
      } catch (requestError) {
        if (active) setError(getApiErrorMessage(requestError, 'دریافت تاریخچه فعالیت‌ها انجام نشد.'))
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => { active = false }
  }, [entityType, action, page])

  const changeEntityType = (value) => { setEntityType(value); setPage(1) }
  const changeAction = (value) => { setAction(value); setPage(1) }

  return (
    <div className="dashboard" dir="rtl">
      <Sidebar />
      <main className="main-content">
        <div className="topbar">
          <div><h1>تاریخچه فعالیت‌ها</h1><p>رویدادهای ثبت‌شده برای Workspaceهایی که مالک آن‌ها هستی.</p></div>
          <div className="filter-row">
            <select className="form-input" aria-label="نوع موجودیت" value={entityType} onChange={(event) => changeEntityType(event.target.value)}>
              <option value="">همه بخش‌ها</option><option value="WORKSPACE">Workspace</option><option value="PROJECT">پروژه</option><option value="TASK">وظیفه</option>
            </select>
            <select className="form-input" aria-label="نوع فعالیت" value={action} onChange={(event) => changeAction(event.target.value)}>
              <option value="">همه فعالیت‌ها</option>
              {Object.entries(actionLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
        </div>
        {error && <div className="auth-error" role="alert">{error}</div>}
        <section className="dashboard-card">
          <div className="card-header"><h3>رویدادها</h3><span>{logs.length} مورد در این صفحه</span></div>
          {loading ? <div className="empty-state"><p>در حال دریافت تاریخچه...</p></div> :
            logs.length === 0 ? <div className="empty-state"><div className="empty-icon">◌</div><strong>فعالیتی پیدا نشد</strong><p>پس از انجام عملیات، رویدادها اینجا نمایش داده می‌شوند.</p></div> :
            <div className="activity-list">{logs.map((log) => <article className="activity-row" key={log.id}>
              <div className="activity-mark">◌</div>
              <div className="activity-content">
                <strong>{actionLabels[log.action] || log.action} {entityLabels[log.entity_type] || log.entity_type}: {log.entity_name}</strong>
                <p>شناسه: {log.entity_id}{log.user ? ` · کاربر #${log.user}` : ''}</p>
              </div>
              <time>{new Date(log.created_at).toLocaleString('fa-IR')}</time>
            </article>)}</div>}
          {!loading && totalPages > 1 && <div className="pagination">
            <button type="button" className="secondary-button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>قبلی</button>
            <span>صفحه {page} از {totalPages}</span>
            <button type="button" className="secondary-button" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>بعدی</button>
          </div>}
        </section>
      </main>
    </div>
  )
}

export default AuditLogs
