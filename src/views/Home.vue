<template lang="pug">
  .layout
    Layout
      Sider(:style="{position: 'fixed', height: '100vh', left: 0, overflow: 'auto'}")
        Menu
          tree-menu(label="ALL", :children="tree", depth="1")
      Layout(:style="{marginLeft: '200px'}")
        Header(:style="{background: '#fff', boxShadow: '0 2px 3px 2px rgba(0,0,0,.1)'}") Header
        Content(:style="{padding: '0 16px 16px'}")
          Card(:style="{margin: '16px 0'}")
            div(style="height: 600px")
            | content
        Content(:style="{padding: '0 16px 16px'}")
          Card(:style="{margin: '16px 0'}")
            div(style="height: 100px")
            | content
</template>

<script>
import TreeMenu from '@/components/TreeMenu.vue'
// import { query } from '@/api.js'

export default {
  data: () => {
    return {
      tree: [
        {
          label: '疾病',
          children: [
            {
              label: 'aaa',
              children: [
                {
                  label: 'xxx',
                  children: []
                }
              ]
            },
            {
              label: 'bbb',
              children: [
                {
                  label: 'yyy',
                  children: []
                }
              ]
            }
          ]
        }
      ]
    }
  },
  name: 'home',
  components: {
    TreeMenu
  },
  created () {
    // this.getTree(['疾病']).then(res => { this.tree = res })
  },
  methods: {
    async getTree (arr) {
      // arr.map(x => )
      let data = []
      return data
    }
  }
}
</script>

<style scoped>
  .layout{
    border: 1px solid #d7dde4;
    background: #f5f7f9;
    position: relative;
    border-radius: 4px;
    overflow: hidden;
  }
</style>
