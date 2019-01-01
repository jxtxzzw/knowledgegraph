<template lang="pug">
  #network
</template>

<script>
import { query } from '@/api'
import { cutName } from '@/utils'

export default {
  name: 'Graph',
  data: function () {
    return { value: '' }
  },
  mounted: function () {
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
        Group1: {
          color: {
            background: '#69c0ff' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 0,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group2: {
          color: {
            background: '#fadb14' },
          borderWidth: 3,
          shape: 'ellipse'
        },
        Group3: {
          color: {
            background: '#73d13d' },
          borderWidth: 3,
          shape: 'circle'
        },
        Group4: {
          color: {
            background: '#597ef7' },
          borderWidth: 3,
          shape: 'circle'
        },
        Group5: {
          color: {
            background: '#ff7a45' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 5,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group6: {
          color: {
            background: '#fadb14' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 10,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group7: {
          color: {
            background: '#bae637' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 0,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group8: {
          color: {
            background: '#73d13d' },
          borderWidth: 3,
          shape: 'ellipse'
        },
        Group9: {
          color: {
            background: '#36cfc9' },
          borderWidth: 3,
          shape: 'circle'
        },
        Group10: {
          color: {
            background: '#40a9ff' },
          borderWidth: 3,
          shape: 'ellipse'
        },
        Group11: {
          color: {
            background: '#9254de' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 5,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group12: {
          color: {
            background: '#f759ab' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 10,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group13: {
          color: {
            background: '#60acfc' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 0,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        },
        Group14: {
          color: {
            background: '#b7eb8f' },
          borderWidth: 3,
          shape: 'box',
          shapeProperties: {
            borderDashes: false,
            borderRadius: 5,
            interpolation: true,
            useImageSize: false,
            useBorderWithImage: false
          }
        }
      },
      physics: {
        solver: 'forceAtlas2Based'
      },
      manipulation: {
        enabled: true,
        addNode: (nodeData, callback) => {
          this.$Modal.confirm({
            render: (h, v) => {
              return h('Input', {
                props: { value: '', autofocus: true, placeholder: `请输入节点名称` },
                on: {
                  input: (val) => { nodeData.label = nodeData.id = val }
                }
              })
            },
            onCancel: () => {
              callback()
            },
            onOk: () => {
              console.log(this.value)
              query(`实例add=${nodeData.label}`).then(res => {
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
              console.log(this.value)
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
        editEdge: false,
        editNode: false
      }
    }
    const data = { nodes: this.nodes, edges: this.edges }
    this.network = new vis.Network(document.getElementById('network'), data, options)
    this.network.on('selectNode', ({ nodes }) => this.generate(nodes[0]))
    this.generate('肺癌')
  },
  methods: {
    async tryAddNode (u) {
      if (this.nodes.get(u) != null) return

      const data = await query(u)
      const cons = data.parents[0]

      if (!(cons in this.consToGroupMap)) this.consToGroupMap[cons] = this.groupSet[this.lastUnusedGroup++]
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
      const self = data.csyn[0]

      await this.tryAddNode(self)

      for (let key in data) {
        if (['病史', '病史逆',
          '相关症状', '相关症状逆',
          '病因', '病因逆',
          '鉴别诊断', '鉴别诊断逆',
          '引发', '引发逆',
          '相关疾病', '相关疾病逆'].indexOf(key) === -1) continue
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
