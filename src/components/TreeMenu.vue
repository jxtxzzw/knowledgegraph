<template lang="pug">
    Submenu(v-if="children.length > 0", :name="depth")
      template(slot="title") {{ label }} {{ children.length }}
      TreeMenu(v-for="(c, idx) in children",
              :key="idx",
              :label="c.label",
              :children="c.children",
              :depth="depth + idx.toString()")
    MenuItem(v-else) {{ label }}
</template>

<script>
export default {
  name: 'TreeMenu',
  props: ['label', 'children', 'depth']
}
</script>

<style scoped>

</style>
