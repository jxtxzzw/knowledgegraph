const axios = require('axios')

export function query (v) {
  return axios.get('http://211.144.102.58:8082/NLI', { params: { p: v } })
}
