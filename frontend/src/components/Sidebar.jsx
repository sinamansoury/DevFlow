import { Link, useLocation } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()

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


      <div className="nav-title">
        Workspace
      </div>


      <div className="nav-item">
        <span className="nav-icon">
          👥
        </span>
        اعضا
      </div>


      <div className="nav-item">
        <span className="nav-icon">
          ◌
        </span>
        فعالیت‌ها
      </div>


      <div className="sidebar-bottom">

        <button
          className="nav-item logout-button"
          onClick={() => {
            localStorage.removeItem(
              'access_token'
            )

            localStorage.removeItem(
              'refresh_token'
            )

            window.location.href =
              '/login'
          }}
        >
          <span className="nav-icon">
            ↪
          </span>
          خروج
        </button>

      </div>

    </aside>
  )
}

export default Sidebar