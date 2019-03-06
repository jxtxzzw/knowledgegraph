module.exports = {
  baseUrl: './',
  devServer: {
    proxy: {
      '/search': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
}
