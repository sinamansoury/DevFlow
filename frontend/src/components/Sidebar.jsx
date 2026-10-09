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
          خروج
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
