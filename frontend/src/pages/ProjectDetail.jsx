import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
function ProjectDetail() {
  const { id } = useParams()

  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [members, setMembers] = useState([])
  const [isWorkspaceOwner, setIsWorkspaceOwner] = useState(false)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [selectedTask, setSelectedTask] = useState(null)
  const [creating, setCreating] = useState(false)
  const openEditModal = (task) => {

  setError('')

  setSelectedTask(task)

  setEditMode(true)

  setForm({
    title: task.title || '',
    description: task.description || '',
    status: task.status || 'TODO',
    assigned_to: task.assigned_to || '',
    started_date: task.started_date
      ? task.started_date.slice(0,16)
      : '',
    deadline: task.deadline
      ? task.deadline.slice(0,16)
      : '',
  })

  setShowModal(true)

}

  const [form, setForm] = useState({
    title: '',
    description: '',
    status: 'TODO',
    assigned_to: '',
    started_date: '',
    deadline: '',
  })

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')

      const [projectResponse, tasksResponse, userResponse] = await Promise.all([
        api.get('/projects/' + id + '/'),
        api.get('/tasks/?project=' + id),
        api.get('/auth/me/'),
      ])

      const workspaceId = projectResponse.data.workspace
      const workspaceResponse = await api.get('/workspaces/' + workspaceId + '/')
      const owner = Number(workspaceResponse.data.owner) === Number(userResponse.data.id)
      const membersResponse = owner
        ? await api.get('/workspaces/' + workspaceId + '/members/')
        : { data: [] }

      setProject(projectResponse.data)
      setIsWorkspaceOwner(owner)
      setTasks(tasksResponse.data.results || tasksResponse.data)
      setMembers(membersResponse.data.results || membersResponse.data)

    } catch (err) {
      console.error(err)
      setError('اطلاعات پروژه دریافت نشد.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [id])

  const getTasks = (status) => {
    return tasks.filter(
      (task) => task.status === status
    )
  }

  const getMemberName = (memberId) => {
  const member = members.find(
    (item) =>
      Number(item.id) === Number(memberId)
  )

  if (!member) {
    return 'کاربر ناشناس'
  }

  const fullName = [
    member.first_name,
    member.last_name,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    fullName ||
    member.email ||
    'کاربر #' + member.id
  )
}

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  const openCreateModal = () => {
    setError('')

    setForm({
      title: '',
      description: '',
      status: 'TODO',
      assigned_to: '',
      started_date: '',
      deadline: '',
    })

    setShowModal(true)
  }

  const createTask = async (e) => {
    e.preventDefault()

    try {
      setCreating(true)
      setError('')

      const data = {
        title: form.title,
        description: form.description,
        project: Number(id),
        status: form.status,
      }

      if (form.assigned_to) {
        data.assigned_to = Number(
          form.assigned_to
        )
      }

      if (form.started_date) {
        data.started_date =
          form.started_date
      }

      if (form.deadline) {
        data.deadline =
          form.deadline
      }

      if (editMode && selectedTask) {
        await api.patch('/tasks/' + selectedTask.id + '/', data)
      } else {
        await api.post('/tasks/projects/' + id + '/', data)
      }

      setShowModal(false)

      await loadData()
    } catch (err) {
      console.error(err)

      const data = err.response?.data

      if (
        data &&
        typeof data === 'object'
      ) {
        setError(
          Object.values(data)
            .flat()
            .join(' ')
        )
      } else {
        setError('ساخت Task انجام نشد.')
      }
    } finally {
      setCreating(false)
    }
  }

  const changeStatus = async (
    task,
    status
  ) => {
    if (task.status === status) {
      return
    }

    try {
      setError('')

      await api.patch(
        '/tasks/' + task.id + '/',
        {
          status,
        }
      )

      await loadData()
    } catch (err) {
      console.error(err)

      const data = err.response?.data

      if (
        data &&
        typeof data === 'object'
      ) {
        setError(
          Object.values(data)
            .flat()
            .join(' ')
        )
      } else {
        setError(
          'تغییر وضعیت Task انجام نشد.'
        )
      }
    }
  }

  if (loading) {
    return (
      <div
        className="project-page-loading"
        dir="rtl"
      >
        <div className="loading-spinner" />

        <span>
          در حال بارگذاری پروژه...
        </span>
      </div>
    )
  }

  if (!project) {
    return (
      <div
        className="project-page-loading"
        dir="rtl"
      >
        <h2>
          پروژه پیدا نشد
        </h2>

        <Link
          to="/workspaces"
          className="primary-button"
        >
          بازگشت
        </Link>
      </div>
    )
  }

  const columns = [
    {
      key: 'TODO',
      title: 'برای انجام',
      icon: '○',
    },
    {
      key: 'IN_PROGRESS',
      title: 'در حال انجام',
      icon: '◐',
    },
    {
      key: 'DONE',
      title: 'انجام شده',
      icon: '✓',
    },
  ]

  return (
    <div
      className="dashboard project-dashboard"
      dir="rtl"
    >
      <Sidebar />

      <main className="main-content project-main">

        <div className="project-topbar">

          <div>

            <Link
              to={
                '/workspaces/' +
                project.workspace
              }
              className="project-back"
            >
              ← بازگشت به Workspace
            </Link>

            <div className="project-heading">

              <div className="project-icon">
                ◈
              </div>

              <div>

                <h1>
                  {project.name}
                </h1>

                <p>
                  {project.description ||
                    'بدون توضیحات برای این پروژه ثبت نشده است.'}
                </p>

              </div>

            </div>

          </div>

          {isWorkspaceOwner && <button type="button" className="primary-button" onClick={openCreateModal}>
            <span>＋</span> Task جدید
          </button>}

        </div>

        {error && (
          <div className="project-error">
            {error}
          </div>
        )}

        <div className="project-stats">

          <div className="project-stat">
            <div className="stat-icon">
              ▣
            </div>

            <div>
              <span>
                کل Taskها
              </span>

              <strong>
                {tasks.length}
              </strong>
            </div>
          </div>

          <div className="project-stat">
            <div className="stat-icon">
              ○
            </div>

            <div>
              <span>
                برای انجام
              </span>

              <strong>
                {getTasks('TODO').length}
              </strong>
            </div>
          </div>

          <div className="project-stat">
            <div className="stat-icon">
              ◐
            </div>

            <div>
              <span>
                در حال انجام
              </span>

              <strong>
                {getTasks(
                  'IN_PROGRESS'
                ).length}
              </strong>
            </div>
          </div>

          <div className="project-stat">
            <div className="stat-icon">
              ✓
            </div>

            <div>
              <span>
                تکمیل شده
              </span>

              <strong>
                {getTasks('DONE').length}
              </strong>
            </div>
          </div>

        </div>

        <div className="board-title">

          <div>

            <h2>
              Task Board
            </h2>

            <span>
              مدیریت و پیگیری وضعیت Taskهای پروژه
            </span>

          </div>

        </div>

        <div className="kanban-board-modern">

          {columns.map((column) => {

            const columnTasks =
              getTasks(column.key)

            return (
              <section
                className={
                  'kanban-column-modern column-' +
                  column.key.toLowerCase()
                }
                key={column.key}
              >

                <div className="kanban-column-header">

                  <div className="column-title">

                    <span className="column-icon">
                      {column.icon}
                    </span>

                    <h3>
                      {column.title}
                    </h3>

                  </div>

                  <span className="column-count">
                    {columnTasks.length}
                  </span>

                </div>

                <div className="kanban-list">

                  {columnTasks.map(
                    (task) => (
                      <article
                        className="task-card-modern"
                        key={task.id}
                      >

                        <div className="task-card-header">

                          <span>
                            TASK-
                            {String(
                              task.id
                            ).padStart(
                              3,
                              '0'
                            )}
                          </span>

                          {task.deadline && (
                            <span className="deadline">
                              📅{' '}
                              {task.deadline}
                            </span>
                          )}

                        </div>

                        <div className="task-card-heading">
                          <h3>{task.title}</h3>
                          {isWorkspaceOwner && <button type="button" className="task-edit-button" onClick={() => openEditModal(task)} aria-label={`ویرایش ${task.title}`}>ویرایش</button>}
                        </div>

                        {task.description && (
                          <p>
                            {
                              task.description
                            }
                          </p>
                        )}

                        <div className="task-divider" />

                        <div className="task-footer">

                          <span className="assignee">
                            👤{' '}
                            {task.assigned_to
                              ? getMemberName(
                                  task.assigned_to
                                )
                              : 'بدون مسئول'}
                          </span>

                          <select
                            value={
                              task.status
                            }
                            onChange={(e) =>
                              changeStatus(
                                task,
                                e.target.value
                              )
                            }
                          >
                            <option value="TODO">
                              برای انجام
                            </option>

                            <option value="IN_PROGRESS">
                              در حال انجام
                            </option>

                            <option value="DONE">
                              انجام شده
                            </option>
                          </select>

                        </div>

                      </article>
                    )
                  )}

                  {columnTasks.length ===
                    0 && (
                    <div className="empty-column">

                      <div>
                        ✦
                      </div>

                      <span>
                        هنوز Taskای در این بخش نیست
                      </span>

                    </div>
                  )}

                </div>

                {isWorkspaceOwner && <button type="button" className="column-add" onClick={openCreateModal}>＋ افزودن Task</button>}

              </section>
            )
          })}

        </div>

      </main>

      {showModal && (
  <div
    className="task-modal-overlay"
    onClick={() =>
      !creating && setShowModal(false)
    }
  >

    <div
      className="task-create-modal"
      onClick={(e) =>
        e.stopPropagation()
      }
    >

      <div className="task-modal-header">

        <div>

          <span className="task-modal-label">
            PROJECT TASK
          </span>

          <h2>
            ساخت Task جدید
          </h2>

          <p>
            یک وظیفه جدید برای این پروژه ایجاد کنید.
          </p>

        </div>


        <button
          className="task-close-button"
          onClick={() =>
            !creating &&
            setShowModal(false)
          }
        >
          ×
        </button>

      </div>



      <form onSubmit={createTask}>


        <div className="form-group">

          <label>
            عنوان Task
          </label>

          <input
            className="form-input"
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="مثلاً طراحی صفحه لاگین"
            required
          />

        </div>



        <div className="form-group">

          <label>
            توضیحات
          </label>

          <textarea
            className="form-input form-textarea"
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="توضیحات Task..."
          />

        </div>



        <div className="form-row">


          <div className="form-group">

            <label>
              وضعیت
            </label>

            <select
              className="form-input"
              name="status"
              value={form.status}
              onChange={handleChange}
            >

              <option value="TODO">
                برای انجام
              </option>

              <option value="IN_PROGRESS">
                در حال انجام
              </option>

              <option value="DONE">
                انجام شده
              </option>

            </select>

          </div>



          <div className="form-group">

            <label>
              مسئول Task
            </label>


            <select
              className="form-input"
              name="assigned_to"
              value={form.assigned_to}
              onChange={handleChange}
            >

              <option value="">
                بدون مسئول
              </option>


              {members.map(
                (member) => (

                  <option
                    key={member.id}
                    value={member.id}
                  >

                    {member.first_name}
                    {' '}
                    {member.last_name ||
                      member.email}

                  </option>

                )
              )}

            </select>


          </div>


        </div>




        <div className="form-row">


          <div className="form-group">

            <label>
              تاریخ شروع
            </label>

            <input
              className="form-input"
              type="datetime-local"
              name="started_date"
              value={form.started_date}
              onChange={handleChange}
            />

          </div>



          <div className="form-group">

            <label>
              Deadline
            </label>

            <input
              className="form-input"
              type="datetime-local"
              name="deadline"
              value={form.deadline}
              onChange={handleChange}
            />

          </div>


        </div>




        <div className="modal-actions">






          <button
            type="submit"
            className="primary-button"
            disabled={creating}
          >

            {creating
              ? 'در حال ساخت...'
              : 'ساخت Task'}

          </button>


        </div>


      </form>


    </div>


  </div>
)}

    </div>
  )
}

export default ProjectDetail