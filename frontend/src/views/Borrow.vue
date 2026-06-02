<template>
  <div class="borrow-page">
    <el-card>
      <template #header>
        <span>我的借阅</span>
      </template>
      <el-table :data="borrows" v-loading="loading" @sort-change="handleSortChange">
        <el-table-column prop="book_title" label="图书名称" />
        <el-table-column 
          prop="borrow_time" 
          label="借阅日期" 
          width="180"
          sortable="custom"
          :sort-order="sortOrder === 'borrow_time' ? sortDirection : null"
        >
          <template #default="{ row }">{{ row.borrow_time ? new Date(row.borrow_time).toLocaleString('zh-CN') : '-' }}</template>
        </el-table-column>
        <el-table-column 
          prop="due_time" 
          label="应还日期" 
          width="180"
          sortable="custom"
          :sort-order="sortOrder === 'due_time' ? sortDirection : null"
        >
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
const sortOrder = ref('borrow_time')
const sortDirection = ref(null)

const loadBorrows = async (params = {}) => {
  loading.value = true
  try {
    const res = await borrowApi.getMyBorrows(params)
    const data = res.data
    borrows.value = data.records || data || []
  } catch (error) {
    ElMessage.error('加载借阅记录失败')
  } finally {
    loading.value = false
  }
}

const handleSortChange = ({ prop, order }) => {
  if (!prop || !order) {
    // 取消排序，使用默认排序
    sortOrder.value = 'borrow_time'
    sortDirection.value = null
    loadBorrows()
    return
  }
  
  sortOrder.value = prop
  sortDirection.value = order
  
  loadBorrows({
    sort_by: prop,
    sort_order: order === 'ascending' ? 'asc' : 'desc'
  })
}

const returnBook = async (row) => {
  try {
    await borrowApi.returnBook(row.id)
    ElMessage.success('归还成功')
    loadBorrows({
      sort_by: sortOrder.value,
      sort_order: sortDirection.value === 'ascending' ? 'asc' : 'desc'
    })
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
