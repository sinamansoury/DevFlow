import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
function Workspaces() {
  const [workspaces, setWorkspaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)

  const [form, setForm] = useState({
    name: '',
    description: '',
  })

  const loadWorkspaces = async () => {
    try {
      setLoading(true)

      const response = await api.get(`/workspaces/?page=${page}`)

      setWorkspaces(response.data.results || response.data)
      setTotalPages(response.data.count ? Math.ceil(response.data.count / 9) : 1)
    } catch (error) {
      setError('دریافت Workspaceها انجام نشد.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadWorkspaces()
  }, [page])

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  const handleCreate = async (e) => {
    e.preventDefault()

    try {
      await api.post('/workspaces/', form)

      setForm({
        name: '',
        description: '',
      })

      setShowModal(false)
      setPage(1)
      await loadWorkspaces()
    } catch (error) {
      const data = error.response?.data

      if (data && typeof data === 'object') {
        setError(
          Object.values(data)
            .flat()
            .join(' ')
        )
      } else {
        setError('ساخت Workspace انجام نشد.')
      }
    }
  }

  return (
    <div className="dashboard" dir="rtl">

      {/* Sidebar */}

      <Sidebar />

      {/* Main */}

      <main className="main-content">

        <div className="topbar">

          <div>
            <h1>
              Workspaceها
            </h1>

            <p>
              فضاهای کاری خودت رو مدیریت کن.
            </p>
          </div>

          <button
            className="primary-button"
            style={{
              width: 'auto',
              padding: '0 22px',
            }}
            onClick={() => {
              setError('')
              setShowModal(true)
            }}
          >
            + ساخت Workspace
          </button>

        </div>

        {error && (
          <div
            className="auth-error"
            style={{ marginBottom: '20px' }}
          >
            {error}
          </div>
        )}

        {loading ? (

          <div className="dashboard-card">
            <div className="empty-state">
              <div className="empty-icon">
                ⏳
              </div>

              <p>
                در حال دریافت Workspaceها...
              </p>
            </div>
          </div>

        ) : workspaces.length === 0 ? (

          <div className="dashboard-card">
            <div className="empty-state">

              <div className="empty-icon">
                ▣
              </div>

              <strong>
                هنوز Workspaceای نداری
              </strong>

              <p>
                اولین Workspace خودت رو بساز و شروع کن.
              </p>

              <button
                className="primary-button"
                style={{
                  width: 'auto',
                  padding: '0 25px',
                  marginTop: '18px',
                }}
                onClick={() => setShowModal(true)}
              >
                ساخت اولین Workspace
              </button>

            </div>
          </div>

        ) : (

          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fill, minmax(280px, 1fr))',
              gap: '18px',
            }}
          >

            {workspaces.map((workspace) => (

              <div
                key={workspace.id}
                className="dashboard-card"
                style={{
                  transition: '0.2s',
                }}
              >

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '20px',
                  }}
                >

                  <div
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background:
                        'rgba(99, 102, 241, 0.12)',
                      color: '#818cf8',
                      fontSize: '20px',
                    }}
                  >
                    ▣
                  </div>

                  <span
                    style={{
                      fontSize: '12px',
                      color: '#64748b',
                    }}
                  >
                    #{workspace.id}
                  </span>

                </div>

                <h3
                  style={{
                    marginBottom: '8px',
                  }}
                >
                  {workspace.name}
                </h3>

                <p
                  style={{
                    color: '#64748b',
                    fontSize: '13px',
                    minHeight: '42px',
                    lineHeight: '1.8',
                  }}
                >
                  {workspace.description ||
                    'بدون توضیحات'}
                </p>

                <div
                  style={{
                    marginTop: '20px',
                    paddingTop: '15px',
                    borderTop:
                      '1px solid #1e293b',
                  }}
                >

                  <Link
                    to={`/workspaces/${workspace.id}`}
                    style={{
                      color: '#818cf8',
                      fontSize: '13px',
                      fontWeight: '600',
                    }}
                  >
                    ورود به Workspace ←
                  </Link>

                </div>

              </div>

            ))}

          </div>
          {totalPages > 1 && <div className="pagination">
            <button type="button" className="secondary-button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>قبلی</button>
            <span>صفحه {page} از {totalPages}</span>
            <button type="button" className="secondary-button" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>بعدی</button>
          </div>}

        )}

      </main>

      {/* Create Modal */}

      {showModal && (

        <div
          onClick={() => setShowModal(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            zIndex: 1000,
          }}
        >

          <div
            onClick={(e) => e.stopPropagation()}
            className="dashboard-card"
            style={{
              width: '100%',
              maxWidth: '480px',
              background: '#0f172a',
            }}
          >

            <div className="card-header">
              <h3>
                ساخت Workspace جدید
              </h3>

              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#64748b',
                  fontSize: '22px',
                }}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreate}>

              <div className="form-group">
                <label>
                  نام Workspace
                </label>

                <input
                  className="form-input"
                  name="name"
                  placeholder="مثلاً تیم توسعه"
                  value={form.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  توضیحات
                </label>

                <textarea
                  className="form-input"
                  name="description"
                  placeholder="توضیح کوتاهی درباره Workspace..."
                  value={form.description}
                  onChange={handleChange}
                  rows="4"
                  style={{
                    height: 'auto',
                    paddingTop: '14px',
                    resize: 'vertical',
                  }}
                />
              </div>

              <button
                className="primary-button"
                type="submit"
              >
                ساخت Workspace
              </button>

            </form>

          </div>

        </div>

      )}

    </div>
  )
}

export default Workspaces