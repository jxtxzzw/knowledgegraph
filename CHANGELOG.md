# 更新日志

## Commit 37 - Version [0.2.24] - 2019-01-07

维护更新日志

## Commit 36 - Version [0.2.23] - 2019-01-06

### 优化

+   选择父节点下拉框同时增加搜索功能，整个字段任意位置匹配

    ![下拉框Filterable](https://dl.jxtxzzw.com/dl/attach/1546830304snipaste_LAPTOP-JQEH2B7G_20190107_110442290.jpg)

## Commit 35 - Version [0.2.22] - 2019-01-06

### 优化

+   添加节点时选择父节点的功能，父节点由query遍历得到，消除硬编码

    ```vue
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
    ```

## Commit 34 - Version [0.2.21] - 2019-01-06

Merge remote-tracking branch 'origin/master'

## Commit 33 - Version [0.2.20] - 2019-01-06



## Commit 32 - Version [0.2.19] - 2019-01-02

### 优化

+   美化滚动条样式

    ![](https://dl.jxtxzzw.com/dl/attach/1546830659snipaste_LAPTOP-JQEH2B7G_20190107_111047720.jpg)

## Commit 31 - Version [0.2.18] - 2019-01-02

### 优化

+   临时恢复成硬编码高度，自适应高度以后再说

## Commit 30 - Version [0.2.17] - 2019-01-02

### 优化

+   修改右侧样式，撑满整个宽度

## Commit 29 - Version [0.2.16] - 2019-01-01



## Commit 28 - Version [0.2.15] - 2019-01-01



## Commit 27 - Version [0.2.14] - 2019-01-01



## Commit 26 - Version [0.2.13] - 2018-12-31



## Commit 25 - Version [0.2.12] - 2018-12-29



## Commit 24 - Version [0.2.11] - 2018-12-26



## Commit 23 - Version [0.2.10] - 2018-12-26

Merge remote-tracking branch 'origin/master'

## Commit 22 - Version [0.2.9] - 2018-12-26



## Commit 21 - Version [0.2.8] - 2018-12-26



## Commit 20 - Version [0.2.7] - 2018-12-26



## Commit 19 - Version [0.2.6] - 2018-12-26



## Commit 18 - Version [0.2.5] - 2018-12-26

### 变更

* 可视化改用 vis 实现

## Commit 17 - Version [0.2.4] - 2018-12-26

维护更新日志

## Commit 16 - Version [0.2.3] - 2018-12-26

### 优化

*   自适应高度

## Commit 15 - Version [0.2.2] - 2018-12-26

### 修复

*   修复 Head 的图标点击不能触发收拢展开的问题

## Commit 14 - Version [0.2.1] - 2018-12-26

### 优化

*   图可以展开

## Commit 13 - Version [0.2.0] - 2018-12-25

### 新增

*   图的展示和布局

    >   `this.cy = cy`会导致整个浏览器无响应
    >
    >   因为不能递归地变成 getter/setter，Data 只能纯数据，这种复杂的开成局部变量，用`this.cy`
    >
    >   设置 Container、headless 见代码

## Commit 12 - Version [0.1.9] - 2018-12-25

### 变更

*   列表移至根目录
*   将 G6 从依赖移除，尝试使用 cytoscape

## Commit 11 - Version [0.1.8] - 2018-12-25

维护更新日志

## Commit 10 - Version [0.1.7] - 2018-12-25

### 修复

*   修复 build 白屏

    >   *   路由采用 hash 代替 history

*   修复 build 跨域问题

    >   Nginx 的配置文件需要增加
    >
    >   ```nginx
    >   location /NLI {
    >       add_header 'Access-Control-Allow-Origin' '*';
    >       proxy_pass http://211.144.102.58:8082;
    >   }
    >   ```

## Commit 9 - Version [0.1.6] - 2018-12-25

### 新增

*   增加 build 相关配置

    >   vue.config.js

### 修复

*   开发时的跨域问题

    >   ```js
    >   proxy: {
    >       '/NLI': {
    >           target: 'http://211.144.102.58:8082',
    >           changeOrigin: true
    >   ```

## Commit 8 - Version [0.1.5] - 2018-12-25

### 优化

*   增加自动展开

    >   点击以后，如果当前`?`，则请求到孩子数目以后自动触发一次点击
    >
    >   效果上等价于只点击一次就自动完成请求和展开

### 修复

*   恢复了一些误删的代码

    >   Collapsible 相关

## Commit 7 - Version [0.1.4] - 2018-12-25

### 新增

*   增加动态载入

    >   由于一次请求整棵树有点多，要等很久，所以动态展开
    >
    >   原理是点击当前节点，将当前节点的名称作为，并根据请求到的孩子节点画出树
    >
    >   默认提供所有的根结点（目前只有 1 个）
    >
    >   对于某个结点，以`Name ?`的形式展示，第 1 次点击以后，`?`替换成孩子的数量，例如`Name 3`，第 2 次点击以后，展开
    >
    >   ![动态载入](https://dl.jxtxzzw.com/dl/attach/1545730387snipaste_LAPTOP-JQEH2B7G_20181225_173300680.jpg)

*   增加加载条

    >   GET 请求开始，到结束，增加加载条

## Commit 6 - Version [0.1.3] - 2018-12-25

### 新增

-   左侧栏增加收起和展开功能

    >   -   Collapsible，点击可收起，再次点击可展开
    >
    >   -   左侧栏调整后，Content自动修改宽度撑满整个屏幕
    >
    >   -   目前已知问题：文字会超过侧栏宽度，处理时间待定

### 修复

*   修复布局错乱的问题

    >   *   左侧菜单宽度过小导致显示不完整，已修复
    >
    >   *   Content 框从上向下堆砌不美观，已修复
    >
    >   *   Padding 修复
    >
    >   *   美化 CSS
    >
    >   ![布局修复](https://dl.jxtxzzw.com/dl/attach/1545730345snipaste_LAPTOP-JQEH2B7G_20181225_173214448.jpg)

## Commit 5 - Version [0.1.2] - 2018-12-25

### 新增

*   增加 API 调用

## Commit 4 - Version [0.1.1] - 2018-12-24

### 新增

* 增加 axios 配置文件

## Commit 3 - Version [0.1.0] - 2018-12-24

### 新增

* 增加递归菜单组件

    >   由于 `G6` 的生态树不支持鼠标点击展开（交互功能弱），且树的展现形式不够美观，所以我们打算直接采用递归菜单作为导航树的展示
    >
    >   ![G6生态树展示](https://dl.jxtxzzw.com/dl/attach/1545729315snipaste_LAPTOP-JQEH2B7G_20181225_171459145.jpg)

## Commit 2 - Version [0.0.1] - 2018-12-24

### 新增

* 增加对 iview, pug, g6, axios 的依赖

## Commit 1 - Version [0.0.0] - 2018-12-24

### 新增

* 项目初始化
