export async function query (v) {
  const params = new URLSearchParams()
  params.append('p', v)
  const res = await window.axios({
    method: 'post',
    url: 'http://127.0.0.1:5000/search/',
    data: params
  })
  console.log(res)
  return res
}
