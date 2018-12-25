module.exports = {
  devServer: {
    proxy: {
      '/NLI': {
        target: 'http://211.144.102.58:8082',
        changeOrigin: true
      }
    }
  }
}
