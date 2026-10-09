import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Workspaces from './pages/Workspaces'
import WorkspaceDetail from './pages/WorkspaceDetail'
import WorkspaceMembers from './pages/WorkspaceMembers'
import ProjectDetail from './pages/ProjectDetail'
import Projects from './pages/Projects'

import Tasks from './pages/Tasks'
import AuditLogs from './pages/AuditLogs'


function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/workspaces" element={<Workspaces />} />
        <Route path="/workspaces/:id" element={<WorkspaceDetail />} />
        <Route path="/workspaces/:id/members" element={<WorkspaceMembers />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/activities" element={<AuditLogs />} />
        <Route path="*" element={<Navigate to="/" replace />} />


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
          path="/workspaces/:id/members"
          element={<WorkspaceMembers />}
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
