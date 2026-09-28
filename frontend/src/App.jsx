import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Workspaces from './pages/Workspaces'
import WorkspaceDetail from './pages/WorkspaceDetail'
import ProjectDetail from './pages/ProjectDetail'
import Projects from './pages/Projects'

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/workspaces"
          element={<Workspaces />}
        />
        <Route
          path="/workspaces/:id"
          element={<WorkspaceDetail />}
        />
        <Route
          path="/projects/:id"
          element={<ProjectDetail />}
        />
        <Route
          path="/projects"
          element={<Projects />}
        />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />

      </Routes>
    </BrowserRouter>
  )
}

export default App