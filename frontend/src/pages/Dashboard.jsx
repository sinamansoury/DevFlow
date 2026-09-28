import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
function Dashboard() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [user, setUser] = useState(null)
  const [workspaces, setWorkspaces] = useState([])

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [userResponse, workspaceResponse] = await Promise.all([
          api.get('/auth/me/'),
          api.get('/workspaces/'),
        ])

        setUser(userResponse.data)
        setWorkspaces(workspaceResponse.data.results || workspaceResponse.data)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/login')
      }
    }

    loadDashboard()
  }, [navigate])

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="dashboard" dir="rtl">

      <Sidebar />

      <main className="main-content">

        <div className="topbar">

          <div>
            <h1>
              سلام {user?.first_name || 'دوست من'} 👋
            </h1>

            <p>
              به داشبورد DevFlow خوش اومدی.
            </p>
          </div>

          {user && (
            <div className="user-box">

              <div className="user-info">
                <strong>
                  {user.first_name} {user.last_name}
                </strong>

                <span>
                  {user.email}
                </span>
              </div>

              <div className="avatar">
                {user.first_name?.charAt(0) || 'U'}
              </div>

            </div>
          )}

        </div>

        <div className="stats-grid">

          <div className="stat-card">
            <div className="stat-card-header">
              Workspace
              <div className="stat-icon">▣</div>
            </div>

            <div className="stat-value">
              {workspaces.length}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              پروژه‌ها
              <div className="stat-icon">◫</div>
            </div>

            <div className="stat-value">
              —
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
              فعالیت‌ها
              <div className="stat-icon">◌</div>
            </div>

            <div className="stat-value">
              —
            </div>
          </div>

        </div>

        <div className="dashboard-grid">

          <div className="dashboard-card">

            <div className="card-header">
              <h3>
                Workspaceهای من
              </h3>

              <a href="#">
                مشاهده همه
              </a>
            </div>

            {workspaces.length === 0 ? (

              <div className="empty-state">
                <div className="empty-icon">
                  ▣
                </div>

                <strong>
                  هنوز Workspace نداری
                </strong>

                <p>
                  اولین فضای کاری خودت رو ایجاد کن.
                </p>
              </div>

            ) : (

              <div>
                {workspaces.map((workspace) => (
                  <div
                    key={workspace.id}
                    style={{
                      padding: '15px',
                      borderBottom: '1px solid #1e293b',
                    }}
                  >
                    <strong>
                      {workspace.name}
                    </strong>

                    <p
                      style={{
                        color: '#64748b',
                        fontSize: '13px',
                        marginTop: '5px',
                      }}
                    >
                      {workspace.description || 'بدون توضیحات'}
                    </p>
                  </div>
                ))}
              </div>

            )}

          </div>

          <div className="dashboard-card">

            <div className="card-header">
              <h3>
                فعالیت اخیر
              </h3>
            </div>

            <div className="empty-state">
              <div className="empty-icon">
                ◌
              </div>

              <strong>
                فعالیتی وجود ندارد
              </strong>

              <p>
                فعالیت‌های اخیر اینجا نمایش داده می‌شوند.
              </p>
            </div>

          </div>

        </div>

      </main>

    </div>
  )
}

export default Dashboard