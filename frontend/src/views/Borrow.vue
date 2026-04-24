<template>
  <div class="borrow-page">
    <el-card>
      <template #header>
        <span>我的借阅</span>
      </template>
      <el-table :data="borrows" v-loading="loading">
        <el-table-column prop="book_title" label="图书名称" />
        <el-table-column prop="borrow_time" label="借阅日期" width="180">
          <template #default="{ row }">{{ row.borrow_time ? new Date(row.borrow_time).toLocaleString('zh-CN') : '-' }}</template>
        </el-table-column>
        <el-table-column prop="due_time" label="应还日期" width="180">
          <template #default="{ row }">{{ row.due_time ? new Date(row.due_time).toLocaleString('zh-CN') : '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'success'">
              {{ row.is_overdue ? '已逾期' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="returnBook(row)" v-if="!row.returned">归还</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { borrowApi } from '../api/modules'

const loading = ref(false)
const borrows = ref([])

const loadBorrows = async () => {
  loading.value = true
  try {
    const res = await borrowApi.getMyBorrows()
    const data = res.data
    borrows.value = data.records || data || []
  } catch (error) {
    ElMessage.error('加载借阅记录失败')
  } finally {
    loading.value = false
  }
}

const returnBook = async (row) => {
  try {
    await borrowApi.returnBook(row.id)
    ElMessage.success('归还成功')
    loadBorrows()
  } catch (error) {
    ElMessage.error('归还失败')
  }
}

onMounted(() => {
  loadBorrows()
})
</script>

<style scoped>
.borrow-page {
  padding: 20px;
}
</style>
