<template lang="pug">
  .layout
    Layout
      Sider(ref="side1", hide-trigger, collapsible, :collapsed-width="78", v-model="isCollapsed", :style="{minHeight: '-webkit-fill-available'}")
        Scroll(height="1100")
          Div(v-if="!isCollapsed" )
            Menu(ref="sideMenu", width="auto", @on-select="loadData")
              MenuItem
                Icon(type="ios-search")
                | 查询
              tree-menu(v-for="(x, idx) in tree",
              :label="x.label",
              :children="x.children", :depth="idx.toString()", :loaded="true")
              MenuItem
                Icon(type="ios-settings")
                | 设置
              MenuItem
                Upload(action="https://dev.jxtxzzw.com/knowledge_graph/upload/index.php",
                :on-success="uploadHandleSuccess",
                :on-error="uploadHandleError"
                )
                  Button(icon="ios-cloud-upload-outline", :long="true") 上传文件
          Div(v-else)
            Menu(ref="sideMenu", width="auto")
              MenuItem
                Icon(type="ios-search")
              MenuItem
                Icon(type="ios-settings")
      Layout
        Header(:style="{padding:0}", class="layout-header-bar")
          Icon(@click.native="collapsedSider", :class="rotateIcon", :style="{margin: '0 20px'}", type="md-menu", size="24")
            | Header
        Content(:style="{margin: '20px', background: '#fff', height: 'auto'}")
          Card(:style="{width: 'auto', minHeight: '-webkit-fill-available'}")
            Graph(:style="{width: 'auto', minHeight: '-webkit-fill-available' }")
</template>

<script>
import TreeMenu from '@/components/TreeMenu.vue'
import Graph from '@/components/Graph.vue'
import { query } from '@/api.js'
export default {
  data: () => {
    return {
      tree: [
        {
          label: '疾病',
          children: [],
          loaded: false
        },
        {
          label: '症状',
          children: [],
          loaded: false
        },
        {
          label: '检查',
          children: [],
          loaded: false
        }
      ],
      isCollapsed: false,
      selfAdaptiveHeight: 0
    }
  },
  name: 'home',
  mounted: function () {
    this.selfAdaptiveHeight = document.body.getBoundingClientRect().height
  },
  computed: {
    rotateIcon () {
      return [
        'menu-icon',
        this.isCollapsed ? 'rotate-icon' : ''
      ]
    },
    menuitemClasses () {
      return [
        'menu-item',
        this.isCollapsed ? 'collapsed-menu' : ''
      ]
    }
  },
  components: {
    TreeMenu, Graph
  },
  methods: {
    success(nodesc) {
      this.$Notice.success({
        title: '文件上传成功',
        desc: nodesc ? '' : '文件上传成功，请耐心等待处理……'
      })
    },
    error(nodesc) {
      this.$Notice.error({
        title: '上传遇到错误',
        desc: nodesc ? '' : '上传遇到错误，错误代码：不予支持，反正就是错了，我也不知道哪里错了'
      });
    },
    uploadHandleSuccess () {
      console.log('handle success')
      this.success(false)
    },
    uploadHandleError () {
      console.log('handle error')
      this.error(false)
    },
    collapsedSider () {
      this.$refs.side1.toggleCollapse()
    },
    loadData (name) {
      let x = name.split('-').map(x => parseInt(x))
      let obj = this.tree
      for (let i = 0; i < x.length; ++i) {
        if (i !== 0) obj = obj.children
        obj = obj[x[i]]
      }
      if (obj.loaded) return
      obj.loaded = true
      query(obj.label).then(res => {
        if (res.hasOwnProperty('child')) {
          console.log(res)
          obj.children = res.child.map(x => { return { label: x, children: [], loaded: false } })
          this.$nextTick(() => {
            this.$refs.sideMenu.openedNames.push(name)
            this.$refs.sideMenu.updateOpened()
          })
        }
      })
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
  .list{
    height: 1500px;
  }
  .layout-header-bar{
    background: #fff;
    box-shadow: 0 1px 1px rgba(0,0,0,.1);
  }
  .layout-logo-left{
    width: 90%;
    height: 30px;
    background: #5b6270;
    border-radius: 3px;
    margin: 15px auto;
  }
  .menu-icon{
    transition: all .3s;
  }
  .rotate-icon{
    transform: rotate(-90deg);
  }
  .menu-item span{
    display: inline-block;
    overflow: hidden;
    width: 69px;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: bottom;
    transition: width .2s ease .2s;
  }
  .menu-item i{
    transform: translateX(0px);
    transition: font-size .2s ease, transform .2s ease;
    vertical-align: middle;
    font-size: 16px;
  }
  .collapsed-menu span{
    width: 0px;
    transition: width .2s ease;
  }
  .collapsed-menu i{
    transform: translateX(5px);
    transition: font-size .2s ease .2s, transform .2s ease .2s;
    vertical-align: middle;
    font-size: 22px;
  }
</style>

<style>
  ::-webkit-scrollbar{width:6px!important;height:6px!important;}
  body::-webkit-scrollbar{width:6px!important;height:6px!important;}
  ::-webkit-scrollbar-track{background:rgba(255,255,255,0.22)!important;border-radius:8px!important;}
  ::-webkit-scrollbar-thumb{background-color:#343434 !important;min-height:50px;border-radius:5px!important;}
  @keyframes fadein {
    0% {opacity: 0;}
    100% {}
  }
  body {
    animation-name: fadein;
    animation-duration: 0.4s;
  }
  scrollbar *
  scrollbar scrollbarbutton{visibility:collapse!important;}
  scrollbar scrollbarbutton{display:none!important;}
  scrollbar[orient="vertical"]{background:rgba(255,255,255,0.22) url(https://pbs.twimg.com/media/CKecQtCWoAA8keI.png)!important;-moz-appearance:none!important;min-width:2px!important;max-width:2px!important;border-radius:5px;}
  scrollbar[orient="vertical"]:hover{-moz-appearance:none!important;}
  scrollbar thumb[orient="vertical"]{background:#6B6B6B!important;-moz-appearance:none!important;border-radius:4px!important;min-height:25px!important;min-width:2px!important;max-width:2px!important;border:1px!important;opacity:0.87;}
  scrollbar thumb[orient="vertical"]:hover{background:#6B6B6B!important;border-radius:4px!important;border:0px!important;opacity:1;}
  scrollbar[orient="horizontal"]{background:rgba(255,255,255,0.22) url(https://pbs.twimg.com/media/CKecQtCWoAA8keI.png)!important;-moz-appearance:none!important;background-color:transparent!important;opacity:.75!important;min-height:2px!important;max-height:9px!important;border-radius:5px;}
  scrollbar[orient="horizontal"]:hover{-moz-appearance:none!important;background-color:transparent!important;min-height:9px!important;max-height:9px!important}
  scrollbar thumb[orient="horizontal"]{background:#6B6B6B!important;-moz-appearance:none!important;border-radius:4px!important;min-height:7px!important;max-height:7px!important;border:1px!important;margin-left:0px!important;opacity:0.87;}
  scrollbar thumb[orient="horizontal"]:hover{background:#6B6B6B!important;border-radius:4px!important;border:0px!important;opacity:1;}
  scrollcorner{opacity:0!important}
  scrollbar scrollcorner:hover{background:transparent!important}
</style>
