
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import Notifications from './Notifications'
function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { id } = useParams()

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

  const isActive = (item) =>
    item.exact
      ? location.pathname === item.to
      : location.pathname.startsWith(item.to)

  return (
    <aside className="sidebar">
      <Link to="/" className="sidebar-logo">
        <span className="logo">D</span>
        <span>DevFlow</span>
      </Link>
        <Notifications />
      <div className="nav-title">منوی اصلی</div>

      <nav aria-label="منوی اصلی">
        {links.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={isActive(item) ? 'nav-item active' : 'nav-item'}
          >
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>
            {item.label}
          </Link>
        ))}
      </nav>

      {id && location.pathname.startsWith('/workspaces/') && (
        <>
          <div className="nav-title">Workspace</div>

          <Link
            to={`/workspaces/${id}/members`}
            className={
              location.pathname.includes('/members')
                ? 'nav-item active'
                : 'nav-item'
            }
          >
            <span className="nav-icon" aria-hidden="true">
              👥
            </span>
            اعضا
          </Link>
        </>
      )}

      <div className="sidebar-bottom">
        <button
          type="button"
          className="nav-item logout-button"
          onClick={logout}
        >
          <span className="nav-icon" aria-hidden="true">
            ↪
          </span>
          خروج
        </button>
      </div>
    </aside>
  )
}

export default Sidebar

