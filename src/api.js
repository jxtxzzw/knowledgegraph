export async function query (v) {
  const res = await window.axios.get('/search/' + v)
  return res.data
}
