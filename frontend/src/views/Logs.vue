<template>
  <div class="logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="操作人">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="请选择模块" clearable style="width: 140px">
            <el-option label="图书管理" value="books" />
            <el-option label="借阅管理" value="borrows" />
            <el-option label="用户管理" value="users" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" placeholder="请选择操作" clearable style="width: 140px">
            <el-option label="新增图书" value="新增图书" />
            <el-option label="编辑图书" value="编辑图书" />
            <el-option label="删除图书" value="删除图书" />
            <el-option label="借阅图书" value="借阅图书" />
            <el-option label="归还图书" value="归还图书" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="logs" v-loading="loading" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="op_time" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.op_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-tag :type="moduleTagType(row.module)">{{ moduleLabel(row.module) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="120" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadLogs"
        @current-change="loadLogs"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { logApi } from '../api/modules'

const loading = ref(false)
const logs = ref([])

const searchForm = reactive({
  username: '',
  module: '',
  action: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const moduleLabel = (module) => {
  const map = { books: '图书管理', borrows: '借阅管理', users: '用户管理' }
  return map[module] || module
}

const moduleTagType = (module) => {
  const map = { books: 'primary', borrows: 'success', users: 'warning' }
  return map[module] || ''
}

const formatTime = (isoStr) => {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  return d.toLocaleString('zh-CN')
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (searchForm.username) params.username = searchForm.username
    if (searchForm.module) params.module = searchForm.module
    if (searchForm.action) params.action = searchForm.action

    const res = await logApi.getAll(params)
    const data = res.data
    logs.value = data.logs || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载审计日志失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.username = ''
  searchForm.module = ''
  searchForm.action = ''
  pagination.page = 1
  loadLogs()
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-form {
  margin-bottom: 20px;
}
</style>
