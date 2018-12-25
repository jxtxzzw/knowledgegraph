<template lang="pug">
    #cy
</template>

<script>
import { query } from '@/api'

export default {
  name: 'Graph',
  data: function () {
    return {}
  },
  mounted: function () {
    const cytoscape = require('cytoscape')
    this.cy = cytoscape({
      container: document.getElementById('cy'),
      headless: false,

      style: [ // the stylesheet for the graph
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(id)'
          }
        },

        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle'
          }
        }
      ],

      layout: {
        name: 'cose'
      }
    })

    this.generate('肺炎')
    this.generate('胸闷')
  },
  methods: {
    tryAddNode (u) {
      this.cy.add({ group: 'nodes', data: { id: u } })
    },
    addEdge (u, v) {
      console.log(u, v)
      this.cy.add({ group: 'edges', data: { id: u + '-' + v, source: u, target: v } })
    },
    async generate (label) {
      const data = await query(label)
      if (!data.hasOwnProperty('csyn')) return
      console.log(data)
      const self = data.csyn[0]
      this.tryAddNode(self)
      for (let key in data) {
        if (['病史', '病史逆', '相关症状', '相关症状逆'].indexOf(key) === -1) continue
        const reverse = key[key.length - 1] === '逆'
        for (let i in data[key]) {
          const to = data[key][i]
          this.tryAddNode(to)
          if (!reverse) this.addEdge(self, to)
          else this.addEdge(to, self)
        }
      }
      let layout = this.cy.layout({ name: 'cose' })
      layout.run()
    }
  }
}
</script>

<style scoped>
  #cy {
    width: 800px;
    height: 800px;
    display: block;
  }
</style>
