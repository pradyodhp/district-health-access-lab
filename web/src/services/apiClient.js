export async function apiClient(path, init) {
  const response = await fetch('/api/' + path, init)
  let data
  try { data = await response.json() } catch { throw Error('The API returned an unreadable response') }
  if (!response.ok) {
    const message = typeof data.detail === 'string' ? data.detail : 'Inputs failed validation'
    throw Error(`${message}${data.request_id ? ` (request ${data.request_id})` : ''}`)
  }
  return data
}
