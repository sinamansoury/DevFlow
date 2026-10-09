import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
function WorkspaceDetail() {
  const { id } = useParams()

  const [workspace, setWorkspace] = useState(null)
  const [projects, setProjects] = useState([])

  const [loading, setLoading] = useState(true)
  const [projectLoading, setProjectLoading] = useState(true)

  const [projectPage, setProjectPage] = useState(1)
  const [projectTotalPages, setProjectTotalPages] = useState(1)

  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)

  const [form, setForm] = useState({
    name: '',
    description: '',
  })

  const loadData = async () => {
    try {
      setLoading(true)

      const workspaceResponse = await api.get(
        `/workspaces/${id}/`
      )

      setWorkspace(workspaceResponse.data)
    } catch (error) {
      setError(
        error.response?.data?.detail ||
        'دریافت Workspace انجام نشد.'
      )
    } finally {
      setLoading(false)
    }

    try {
      setProjectLoading(true)

      const projectResponse = await api.get(
        `/projects/?workspace=${id}&page=${projectPage}`
      )

      setProjects(
        projectResponse.data.results ||
        projectResponse.data
      )

      if (projectResponse.data.count) {
        setProjectTotalPages(
          Math.ceil(
            projectResponse.data.count / 9
          )
        )
      } else {
        setProjectTotalPages(1)
      }
    } catch (error) {
      console.error(error)
    } finally {
      setProjectLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [id, projectPage])

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()

    try {
      await api.post(`/projects/workspace/${id}/`, {
        name: form.name,
        description: form.description,
      })

      setForm({
        name: '',
        description: '',
      })

      setShowModal(false)

      setProjectPage(1)

      loadData()
    } catch (error) {
      const data = error.response?.data

      if (data && typeof data === 'object') {
        setError(
          Object.values(data)
            .flat()
            .join(' ')
        )
      } else {
        setError('ساخت پروژه انجام نشد.')
      }
    }
  }

  if (loading) {
    return (
      <div className="dashboard" dir="rtl">
        <main className="main-content">
          <div className="dashboard-card">
            <div className="empty-state">
              <div className="empty-icon">⏳</div>
              <p>در حال دریافت اطلاعات...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error && !workspace) {
    return (
      <div className="dashboard" dir="rtl">
        <main className="main-content">
          <div className="dashboard-card">
            <div className="empty-state">
              <div className="empty-icon">⚠️</div>
              <strong>{error}</strong>

              <Link
                to="/workspaces"
                style={{
                  color: '#818cf8',
                  marginTop: '15px',
                }}
              >
                بازگشت به Workspaceها
              </Link>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="dashboard" dir="rtl">

      <Sidebar />

      <main className="main-content">

        <div className="topbar">

          <div>
            <div
              style={{
                color: '#64748b',
                fontSize: '13px',
                marginBottom: '8px',
              }}
            >
              Workspace / {workspace.name}
            </div>

            <h1>
              {workspace.name}
            </h1>

            <p>
              {workspace.description ||
                'بدون توضیحات'}
            </p>
          </div>

          <div className="topbar-actions">
            <Link to={`/workspaces/${id}/members`} className="secondary-button">مدیریت اعضا</Link>
            <Link to="/workspaces" className="text-link">← همه Workspaceها</Link>
          </div>

        </div>

        {error && (
          <div
            className="auth-error"
            style={{ marginBottom: '20px' }}
          >
            {error}
          </div>
        )}

        <div className="stats-grid">

          <div className="stat-card">
            <div className="stat-card-header">
              پروژه‌ها
              <div className="stat-icon">◫</div>
            </div>

            <div className="stat-value">
              {projects.length}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              وظایف
              <div className="stat-icon">✓</div>
            </div>

            <div className="stat-value">
              —
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              اعضا
              <div className="stat-icon">👥</div>
            </div>

            <div className="stat-value">
              {workspace.members?.length || 0}
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

        <div className="dashboard-card">

          <div className="card-header">

            <div>
              <h3>
                پروژه‌های Workspace
              </h3>

              <p
                style={{
                  color: '#64748b',
                  fontSize: '12px',
                  marginTop: '5px',
                }}
              >
                پروژه‌های این Workspace را مدیریت کن.
              </p>
            </div>

            <button
              className="primary-button"
              style={{
                width: 'auto',
                height: '40px',
                padding: '0 18px',
                fontSize: '13px',
              }}
              onClick={() => {
                setError('')
                setShowModal(true)
              }}
            >
              + پروژه جدید
            </button>

          </div>

          {projectLoading ? (

            <div className="empty-state">
              <div className="empty-icon">
                ⏳
              </div>

              <p>
                در حال دریافت پروژه‌ها...
              </p>
            </div>

          ) : projects.length === 0 ? (

            <div className="empty-state">
              <div className="empty-icon">
                ◫
              </div>

              <strong>
                هنوز پروژه‌ای ساخته نشده
              </strong>

              <p>
                اولین پروژه این Workspace را بساز.
              </p>
            </div>

          ) : (

            <>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '16px',
                }}
              >

                {projects.map((project) => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    className="stat-card"
                    style={{
                      transition: '0.2s',
                      textDecoration: 'none',
                      color: 'inherit',
                      display: 'block',
                      cursor: 'pointer',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '15px',
                      }}
                    >
                      <div
                        style={{
                          width: '42px',
                          height: '42px',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background:
                            'rgba(99, 102, 241, 0.12)',
                          color: '#818cf8',
                        }}
                      >
                        ◫
                      </div>

                      <div>
                        <strong>
                          {project.name}
                        </strong>

                        <div
                          style={{
                            color: '#475569',
                            fontSize: '11px',
                            marginTop: '3px',
                          }}
                        >
                          Project #{project.id}
                        </div>
                      </div>
                    </div>

                    <p
                      style={{
                        color: '#64748b',
                        fontSize: '13px',
                        lineHeight: '1.8',
                        minHeight: '46px',
                      }}
                    >
                      {project.description ||
                        'بدون توضیحات'}
                    </p>

                    <div
                      style={{
                        marginTop: '16px',
                        paddingTop: '13px',
                        borderTop:
                          '1px solid #1e293b',
                      }}
                    >
                      <span
                        style={{
                          color: '#818cf8',
                          fontSize: '12px',
                        }}
                      >
                        مشاهده پروژه ←
                      </span>
                    </div>
                  </Link>
                ))}

              </div>

              {projectTotalPages > 1 && (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '7px',
      marginTop: '28px',
      paddingTop: '22px',
      borderTop: '1px solid #1e293b',
    }}
  >

    {/* قبلی */}
    <button
      type="button"
      disabled={projectPage === 1}
      onClick={() =>
        setProjectPage((page) => page - 1)
      }
      style={{
        height: '36px',
        minWidth: '68px',
        padding: '0 12px',
        border: '1px solid #263247',
        borderRadius: '9px',
        background: '#111827',
        color:
          projectPage === 1
            ? '#475569'
            : '#94a3b8',
        fontFamily: 'inherit',
        fontSize: '12px',
        cursor:
          projectPage === 1
            ? 'not-allowed'
            : 'pointer',
        opacity: projectPage === 1 ? 0.5 : 1,
      }}
    >
      ← قبلی
    </button>

    {/* شماره صفحات */}
    {Array.from(
      {
        length: projectTotalPages,
      },
      (_, index) => index + 1
    ).map((page) => {
      const active = page === projectPage

      return (
        <button
          type="button"
          key={page}
          onClick={() =>
            setProjectPage(page)
          }
          style={{
            width: '36px',
            height: '36px',
            padding: 0,
            border: active
              ? '1px solid #6366f1'
              : '1px solid #263247',
            borderRadius: '9px',
            background: active
              ? '#6366f1'
              : '#111827',
            color: active
              ? '#ffffff'
              : '#94a3b8',
            fontFamily: 'inherit',
            fontSize: '12px',
            fontWeight: active
              ? '600'
              : '400',
            cursor: 'pointer',
            boxShadow: active
              ? '0 4px 12px rgba(99, 102, 241, 0.2)'
              : 'none',
            transition: 'all 0.2s ease',
          }}
        >
          {page}
        </button>
      )
    })}

    {/* بعدی */}
    <button
      type="button"
      disabled={
        projectPage === projectTotalPages
      }
      onClick={() =>
        setProjectPage((page) => page + 1)
      }
      style={{
        height: '36px',
        minWidth: '68px',
        padding: '0 12px',
        border: '1px solid #263247',
        borderRadius: '9px',
        background: '#111827',
        color:
          projectPage === projectTotalPages
            ? '#475569'
            : '#94a3b8',
        fontFamily: 'inherit',
        fontSize: '12px',
        cursor:
          projectPage === projectTotalPages
            ? 'not-allowed'
            : 'pointer',
        opacity:
          projectPage === projectTotalPages
            ? 0.5
            : 1,
      }}
    >
      بعدی →
    </button>

  </div>
)}

            </>

          )}

        </div>

      </main>

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
                ساخت پروژه جدید
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

            <form onSubmit={handleCreateProject}>

              <div className="form-group">

                <label>
                  نام پروژه
                </label>

                <input
                  className="form-input"
                  name="name"
                  placeholder="مثلاً پنل مدیریت"
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
                  placeholder="توضیح کوتاهی درباره پروژه..."
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
                ساخت پروژه
              </button>

            </form>

          </div>

        </div>

      )}

    </div>
  )
}

export default WorkspaceDetail