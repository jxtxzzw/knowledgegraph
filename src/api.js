export async function query (v) {
  const res = await window.axios.get('/NLI', { params: { p: v } })
  return res.data
}
