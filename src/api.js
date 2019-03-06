export async function query (v) {
  const params = new URLSearchParams()
  params.append('p', v)
  console.log('res')
  const res = await window.axios({
    method: 'post',
    url: './search/',
    data: params
  }).then(
    function (response) {
      console.log('response')
      if (response.status === 200) {
        return response.data
      }
    }
  )['catch']((error) => {
    console.log(error)
  })
  return res
}
