<template lang="pug">
    Button(type="primary", @click="handleRender") 添加推理规则
</template>

<script>
export default {
  name: 'Rule',
  created: function () {
    window.customRule = localStorage.ruleValue.split('\n').map(s => s.split(/\.|=/))
  },
  methods: {
    handleRender () {
      this.$Modal.confirm({
        render: (h) => {
          return h('Input', {
            props: {
              value: localStorage.ruleValue,
              type: 'textarea',
              autofocus: true,
              placeholder: '添加规则，使用回车分割 （如 相关症状逆.相关症状=新的相关症状）'
            },
            on: {
              input: (val) => {
                localStorage.ruleValue = val
                window.customRule = val.split('\n').map(s => s.split(/\.|=/))
              }
            }
          })
        }
      })
    }
  }
}
</script>

<style scoped>

</style>
