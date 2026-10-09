export function getApiErrorMessage(error, fallback = 'درخواست انجام نشد.') {
  const data = error?.response?.data
  if (!data) {
    return 'ارتباط با سرور برقرار نشد. اتصال و روشن بودن بک‌اند را بررسی کن.'
  }

  if (typeof data.message === 'string' && data.message.trim()) {
    const nested = data.errors
    if (!nested) return data.message
    const details = Object.values(nested).flatMap((value) =>
      Array.isArray(value) ? value : [value]
    ).map((value) => String(value)).filter(Boolean)
    return details.length ? [...new Set(details)].join(' ') : data.message
  }

  if (typeof data.detail === 'string') return data.detail

  const details = Object.values(data).flatMap((value) =>
    Array.isArray(value) ? value : [value]
  ).map((value) => String(value)).filter(Boolean)

  return details.length ? [...new Set(details)].join(' ') : fallback
}
