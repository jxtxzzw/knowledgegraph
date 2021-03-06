import Vue from 'vue'
import './plugins/axios'
import App from './App.vue'
import router from './router'
import './plugins/iview.js'

import 'vis/dist/vis.css'

Vue.config.productionTip = false

if (module.hot) {
  module.hot.accept()
}

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
