
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'

function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [error, setError] = useState('')

  const unreadCount = notifications.filter(
    (notification) => !notification.is_read
  ).length

  const fetchNotifications = useCallback(async () => {
  setLoading(true)

  try {
    setError('')

    const response = await api.get('/notifications/')
    const data = response.data

    setNotifications(
      Array.isArray(data) ? data : data.results || []
    )
  } catch (err) {
    setError('دریافت اعلان‌ها ناموفق بود.')
    console.error('Fetch notifications error:', err)
  } finally {
    setLoading(false)
  }
}, [])

  useEffect(() => {
    if (!localStorage.getItem('access_token')) {
      setLoading(false)
      return
    }

    fetchNotifications()
  }, [fetchNotifications])

  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      try {
        const response = await api.post(
          `/notifications/${notification.id}/read/`
        )

        setNotifications((current) =>
          current.map((item) =>
            item.id === notification.id
              ? { ...item, ...response.data }
              : item
          )
        )
      } catch (err) {
        setError('علامت‌گذاری اعلان ناموفق بود.')
        console.error('Mark notification read error:', err)
        return
      }
    }

    if (notification.task) {
      setOpen(false)
      // فعلاً به صفحه وظایف می‌رویم؛
      // مسیر جزئیات تسک را در مرحله بعد متصل می‌کنیم.
      window.location.href = '/tasks'
    }
  }

  return (
    <div className="notifications">
      <button
        type="button"
        className="notifications-trigger"
        aria-label={`اعلان‌ها، ${unreadCount} اعلان خوانده‌نشده`}
        aria-expanded={open}
        onClick={() => {
          setOpen((current) => !current)
          if (!open) fetchNotifications()
        }}
      >
        <span aria-hidden="true">🔔</span>

        {unreadCount > 0 && (
          <span className="notifications-badge">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="notifications-panel" dir="rtl">
          <div className="notifications-header">
            <strong>اعلان‌ها</strong>

            <button
              type="button"
              onClick={fetchNotifications}
              className="notifications-refresh"
            >
              بروزرسانی
            </button>
          </div>

          {error && (
            <p className="notifications-error" role="alert">
              {error}
            </p>
          )}

          {loading ? (
            <p className="notifications-empty">در حال دریافت...</p>
          ) : notifications.length === 0 ? (
            <p className="notifications-empty">
              اعلانی ندارید.
            </p>
          ) : (
            <ul className="notifications-list">
              {notifications.map((notification) => (
                <li key={notification.id}>
                  <button
                    type="button"
                    className={`notification-item ${
                      notification.is_read ? 'read' : 'unread'
                    }`}
                    onClick={() =>
                      handleNotificationClick(notification)
                    }
                  >
                    <span className="notification-title">
                      {notification.title}
                    </span>

                    <span className="notification-message">
                      {notification.message}
                    </span>

                    {notification.task_title && (
                      <span className="notification-task">
                        تسک: {notification.task_title}
                      </span>
                    )}

                    <span className="notification-status">
                      {notification.is_read
                        ? 'خوانده‌شده'
                        : 'خوانده‌نشده'}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default Notifications

