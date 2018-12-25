module.exports = {
    baseUrl: './',
    outputDir: 'dist',
    assetsDir: 'assets',
    lintOnSave: true,
    runtimeCompiler: true,
    transpileDependencies: [],
    productionSourceMap: false,
    css: {
        // modules: true,
        // extract: true,
        sourceMap: false,
        loaderOptions: {
            sass: {
                data: ''//`@import "@/assets/scss/mixin.scss";`
            }
        }
    },
    parallel: require('os').cpus().length > 1,
    pluginOptions: {
    },
    pwa: {		
    },
    devServer: {
        open: true,
        host: '0.0.0.0',
        port: 80,
        https: false,
        hotOnly: false,
        proxy: {
		  '/NLI': {
			target: 'http://211.144.102.58:8082',
			changeOrigin: true
		  }
		},
        before: app => {}
    }
}