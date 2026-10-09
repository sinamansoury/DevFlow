<<<<<<< Updated upstream
import { Link, useLocation, useNavigate } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const links = [
    { to: '/', label: 'داشبورد', icon: '⌂', exact: true },
    { to: '/workspaces', label: 'Workspaceها', icon: '▣' },
    { to: '/projects', label: 'پروژه‌ها', icon: '◫' },
    { to: '/tasks', label: 'وظایف', icon: '✓' },
    { to: '/activities', label: 'فعالیت‌ها', icon: '◌' },
  ]

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login', { replace: true })
  }

  return (
    <aside className="sidebar">
      <Link to="/" className="sidebar-logo">
        <span className="logo">D</span>
        <span>DevFlow</span>
      </Link>
      <div className="nav-title">منوی اصلی</div>
      <nav aria-label="منوی اصلی">
        {links.map((item) => {
          const active = item.exact
            ? location.pathname === item.to
            : location.pathname.startsWith(item.to)
          return (
            <Link key={item.to} to={item.to} className={active ? 'nav-item active' : 'nav-item'}>
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>
      <div className="sidebar-bottom">
        <button type="button" className="nav-item logout-button" onClick={logout}>
          <span className="nav-icon" aria-hidden="true">↪</span>
=======
import { Link, useLocation, useParams } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()
  const { id } = useParams()

  const workspaceId = id

  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="logo">
          D
        </div>

        <span>
          DevFlow
        </span>
      </div>


      <div className="nav-title">
        منوی اصلی
      </div>


      <Link
        to="/"
        className={
          location.pathname === '/'
            ? 'nav-item active'
            : 'nav-item'
        }
      >
        <span className="nav-icon">
          ⌂
        </span>

        داشبورد
      </Link>


      <Link
        to="/workspaces"
        className={
          location.pathname.startsWith('/workspaces')
            ? 'nav-item active'
            : 'nav-item'
        }
      >
        <span className="nav-icon">
          ▣
        </span>

        Workspaceها
      </Link>


      <Link
        to="/projects"
        className={
          location.pathname.startsWith('/projects')
            ? 'nav-item active'
            : 'nav-item'
        }
      >
        <span className="nav-icon">
          ◫
        </span>

        پروژه‌ها
      </Link>


      <Link
        to="/tasks"
        className={
          location.pathname.startsWith('/tasks')
            ? 'nav-item active'
            : 'nav-item'
        }
      >
        <span className="nav-icon">
          ✓
        </span>

        وظایف
      </Link>


      {workspaceId && (
        <>
          <div className="nav-title">
            Workspace
          </div>


          <Link
            to={`/workspaces/${workspaceId}/members`}
            className={
              location.pathname.includes('/members')
                ? 'nav-item active'
                : 'nav-item'
            }
          >
            <span className="nav-icon">
              👥
            </span>

            اعضا
          </Link>


          <div className="nav-item">
            <span className="nav-icon">
              ◌
            </span>

            فعالیت‌ها
          </div>
        </>
      )}


      <div className="sidebar-bottom">

        <button
          className="nav-item logout-button"
          onClick={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')

            window.location.href = '/login'
          }}
        >
          <span className="nav-icon">
            ↪
          </span>

>>>>>>> Stashed changes
          خروج
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
