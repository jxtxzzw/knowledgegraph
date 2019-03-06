<template lang="pug">
  #network
</template>

<script>
import { query } from '@/api'
import { cutName, groups } from '@/utils'

export default {
  name: 'Graph',
  data: function () {
    return {
      value: '',
      concepts: []
    }
  },
  mounted: function () {
    window.generateLabel = this.generate

    query('概念').then(res => {
      this.concepts = res.result
    })
    this.groupSet = ['Group1', 'Group2', 'Group3', 'Group4', 'Group5', 'Group6', 'Group7', 'Group8', 'Group9', 'Group10', 'Group11', 'Group12', 'Group13', 'Group14']
    this.consToGroupMap = {}
    this.lastUnusedGroup = 0
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
        ...groups
      },
      physics: {
        solver: 'forceAtlas2Based'
      },
      manipulation: {
        enabled: true,
        addNode: (nodeData, callback) => {
          this.$Modal.confirm({
            render: (h, v) => {
              let parentNodeList = []
              for (let concept of this.concepts) {
                parentNodeList.push(
                  h('Option', {
                    props: {
                      value: concept.toString()
                    }
                  }, concept.toString())
                )
              }
              return h('div',
                [h('Select', {
                  props: {
                    placeholder: `请选择节点父亲`,
                    filterable: ''
                  },
                  on: {
                    'on-change': (event) => { this.value = event }
                  }
                }, parentNodeList),
                h('Input', {
                  props: { value: '', autofocus: true, placeholder: `请输入节点名称` },
                  on: {
                    input: (val) => { nodeData.label = nodeData.id = val }
                  }
                })])
            },
            onCancel: () => {
              callback()
            },
            onOk: () => {
              // console.log(nodeData.parent)
              query(`实例add=${nodeData.label}`)
              query(`${this.value}.insadd=${nodeData.label}`).then(res => {
                callback(nodeData)
              }).catch(e => callback())
            }
          })
        },
        addEdge: (edgeData, callback) => {
          const { from, to } = edgeData
          this.$Modal.confirm({
            render: (h) => {
              return h('Input', {
                props: { value: '', autofocus: true, placeholder: `请输入 ${from} 到 ${to} 的关系（如：相关疾病）` },
                on: {
                  input: (val) => { this.value = val }
                }
              })
            },
            onCancel: () => {
              callback()
            },
            onOk: () => {
              query(`${from}.${this.value}add=${to}`).then(data => {
                callback(edgeData)
              }).catch(e => callback())
            }
          })
        },
        deleteEdge: (data, callback) => {
          const edge = this.edges.get(data.edges[0])

          this.$Modal.confirm({
            content: `你确定要删除${edge.from}到${edge.to}的${edge.title}的关系吗`,
            onCancel: () => { callback() },
            onOk: () => {
              query(`${edge.from}.${edge.title}minus=${edge.to}`).then(res => {
                callback(data)
              }).catch(e => callback())
            }
          })
        },
        deleteNode: (data, callback) => {
          const node = this.nodes.get(data.nodes[0])
          this.$Modal.confirm({
            content: `你确定要删除${node.id}节点吗`,
            onCancel: () => { callback() },
            onOk: () => {
              query(`概念minus=${node.id}`).then(res => {
                callback(data)
              }).catch(e => callback())
            }
          })
        },
        editEdge: false
        // editNode: false
      }
    }
    const data = { nodes: this.nodes, edges: this.edges }
    this.network = new vis.Network(document.getElementById('network'), data, options)
    this.network.on('selectNode', ({ nodes }) => this.generate(nodes[0]))
  },
  methods: {
    async tryAddNode (u) {
      if (this.nodes.get(u) != null) return
      const data = await query(u)
      if (!data.hasOwnProperty('parents')) return
      const cons = data.parents[0]
      if (!(cons in this.consToGroupMap)) this.consToGroupMap[cons] = this.groupSet[this.lastUnusedGroup++]
      this.nodes.add({ id: u, label: cutName(u), title: u, group: this.consToGroupMap[cons] })
    },
    async addEdge (u, v, title, dashes) {
      await this.tryAddNode(u)
      await this.tryAddNode(v)
      if (dashes === undefined) dashes = false
      const id = u + '-' + v
      this.edges.update({ id: id, from: u, to: v, title, dashes })
    },
    async applyRule (u, v, relationship) {
      const data = await query(v)
      if (!data.hasOwnProperty(relationship[1])) return
      for (let z of data[relationship[1]]) await this.addEdge(u, z, relationship[2], true)
    },
    async generate (label) {
      const data = await query(label)
      if (!data.hasOwnProperty('csyn')) return
      const self = data.csyn[0]

      await this.tryAddNode(self)

      for (let key in data) {
        if (['parents', 'attr', 'csyn'].indexOf(key) !== -1) continue
        const reverse = key[key.length - 1] === '逆'
        for (let i in data[key]) {
          const to = data[key][i]
          const title = reverse ? key.slice(0, -1) : key
          if (!reverse) await this.addEdge(self, to, title)
          else await this.addEdge(to, self, title)
          console.log('ssss')
          for (let x of window.customRule) {
            if (x[0] === key) await this.applyRule(self, to, x)
          }
        }
      }
    }
  }
}
</script>

<style scoped>
  #network {
    height: 1500px;
    width: 100%;
    border: 2px solid lightgray;
    border-radius: 5px;
  }
</style>
