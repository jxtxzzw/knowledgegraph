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
    this.groupSet = ['disease', 'symptom', 'examination']
    this.lastUnusedColor = 0
    this.consToGroupMap = {}

    const vis = require('vis')
    this.nodes = new vis.DataSet()
    this.edges = new vis.DataSet()
    const options = {
      interaction: { hover: true },
      edges: {
        arrows: 'to'
      },
      groups: {
        useDefaultGroups: true,
        disease: {
          color: {
            background: '#60acfc' },
          borderWidth: 3,
          shape: 'box'
        },
        symptom: {
          color: {
            background: '#feb64d' },
          borderWidth: 3,
          shape: 'circle'
        },
        examination: {
          color: {
            background: '#5bc49f' },
          borderWidth: 3,
          shape: 'square'
        }
      },
      physics: {
        solver: 'forceAtlas2Based'
      }
    }
    const data = { nodes: this.nodes, edges: this.edges }
    this.network = new vis.Network(document.getElementById('network'), data, options)
    this.network.on('selectNode', ({ nodes }) => this.generate(nodes[0]))
    this.generate('肺炎')
  },
  methods: {
    async tryAddNode (u) {
      if (this.nodes.get(u) != null) return

      const data = await query(u)
      const cons = data.parents[0]
      console.log(cons, this.groupSet)
      if (!(cons in this.consToGroupMap)) this.consToGroupMap[cons] = this.groupSet[this.lastUnusedColor++]
      this.nodes.add({ id: u, label: cutName(u), title: u, group: this.consToGroupMap[cons] })
    },
    async addEdge (u, v, title) {
      await this.tryAddNode(u)
      await this.tryAddNode(v)

      const id = u + '-' + v
      this.edges.update({ id: id, from: u, to: v, title })
    },
    async generate (label) {
      const data = await query(label)
      if (!data.hasOwnProperty('csyn')) return
      console.log(data)
      const self = data.csyn[0]

      for (let key in data) {
        if (['病史', '病史逆',
          '相关症状', '相关症状逆',
          '病因', '病因逆',
          '鉴别诊断', '鉴别诊断逆',
          '引发', '引发逆'].indexOf(key) === -1) continue
        const reverse = key[key.length - 1] === '逆'
        for (let i in data[key]) {
          const to = data[key][i]
          const title = reverse ? key.slice(0, -1) : key
          if (!reverse) await this.addEdge(self, to, title)
          else await this.addEdge(to, self, title)
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
