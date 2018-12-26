<template lang="pug">
    #network
</template>

<script>
import { query } from '@/api'
import { cutName } from '@/utils'

export default {
  name: 'Graph',
  data: function () {
    return {}
  },
  mounted: function () {
    const vis = require('vis')
    this.nodes = new vis.DataSet()
    this.edges = new vis.DataSet()
    const options = {
      interaction: { hover: true },
      edges: {
        arrows: 'to'
      }
    }
    const data = { nodes: this.nodes, edges: this.edges }
    this.network = new vis.Network(document.getElementById('network'), data, options)
    this.network.on('selectNode', ({ nodes }) => this.generate(nodes[0]))
    this.generate('肺炎')
  },
  methods: {
    tryAddNode (u) {
      if (this.nodes.get(u) != null) return
      this.nodes.add({ id: u, label: cutName(u), title: u })
    },
    addEdge (u, v, title) {
      const id = u + '-' + v
      if (this.edges.get(id) != null) return
      this.edges.add({ id: id, from: u, to: v, title })
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
          const title = reverse ? key.slice(0, -1) : key
          this.tryAddNode(to)
          if (!reverse) this.addEdge(self, to, title)
          else this.addEdge(to, self, title)
        }
      }
    }
  }
}
</script>

<style scoped>
  #network {
    width: 1000px;
    height: 800px;
    border: 1px solid lightgray;
  }
</style>
