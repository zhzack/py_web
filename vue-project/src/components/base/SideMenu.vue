<template>

    <el-menu :collapse="collapsed" class="side-menu" router>
      <el-menu-item  @click="$emit('toggle')">
        <el-icon>
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
        <span v-if="!collapsed">折叠</span>
      </el-menu-item>

      <el-menu-item index="/dashboard">
        <el-icon>
          <HomeFilled />
        </el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/system/user">
        <el-icon>
          <User />
        </el-icon>
        <span>用户管理</span>
      </el-menu-item>
    </el-menu>
</template>

<script setup>
import {
  HomeFilled,
  User,
  Fold,
  Expand
} from '@element-plus/icons-vue'
p
defineProps({
  collapsed: Boolean
})
</script>

<style scoped>
.side-menu-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}


.collapse-btn span {
  margin-left: 16px;
}

.collapse-btn:hover {
  background-color: var(--el-menu-hover-bg-color);
}

.side-menu {
  flex: 1;
  border-right: none;
}

</style>