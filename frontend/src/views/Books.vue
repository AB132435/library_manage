<template>
  <div class="books-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图书列表</span>
          <el-button type="primary" @click="showAddDialog" v-if="userStore.isAdmin">新增图书</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.search" placeholder="请输入书名或ISBN" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadBooks">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="books" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="书名" min-width="160" />
        <el-table-column prop="isbn" label="ISBN" width="140" />
        <el-table-column label="出版社" width="120">
          <template #default="{ row }">{{ row.publisher || '-' }}</template>
        </el-table-column>
        <el-table-column label="分类" width="100">
          <template #default="{ row }">{{ row.category || '-' }}</template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="80" />
        <el-table-column prop="stock" label="库存" width="70" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewBook(row)">详情</el-button>
            <el-button size="small" type="primary" @click="borrowBook(row)" v-if="row.stock > 0 && (userStore.isReader || userStore.isAdmin)">借阅</el-button>
            <el-button size="small" type="success" @click="editBook(row)" v-if="userStore.isAdmin">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteBook(row)" v-if="userStore.isAdmin">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadBooks"
        @current-change="loadBooks"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑图书' : '新增图书'" width="600px">
      <el-form :model="bookForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="bookForm.title" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookForm.isbn" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="bookForm.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="bookForm.stock" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- Book Detail Dialog -->
    <el-dialog v-model="detailVisible" title="图书详情" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="书名">{{ currentBook.title }}</el-descriptions-item>
        <el-descriptions-item label="ISBN">{{ currentBook.isbn }}</el-descriptions-item>
        <el-descriptions-item label="出版社">{{ currentBook.publisher || '-' }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentBook.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ currentBook.price }}</el-descriptions-item>
        <el-descriptions-item label="库存">{{ currentBook.stock }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'
import { bookApi } from '../api/modules'

const userStore = useUserStore()
const loading = ref(false)
const books = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentBook = ref({})

const searchForm = reactive({
  search: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const bookForm = reactive({
  id: null,
  title: '',
  isbn: '',
  publisher_id: null,
  category_id: null,
  price: 0,
  stock: 1
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }]
}

const loadBooks = async () => {
  loading.value = true
  try {
    const res = await bookApi.getAll({
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchForm.search
    })
    const data = res.data
    books.value = data.books || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载图书列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.search = ''
  pagination.page = 1
  loadBooks()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(bookForm, { id: null, title: '', isbn: '', publisher_id: null, category_id: null, price: 0, stock: 1 })
  dialogVisible.value = true
}

const editBook = (row) => {
  isEdit.value = true
  Object.assign(bookForm, {
    id: row.id,
    title: row.title,
    isbn: row.isbn,
    price: row.price || 0,
    stock: row.stock || 1
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await bookApi.update(bookForm.id, bookForm)
        ElMessage.success('更新成功')
      } else {
        await bookApi.create(bookForm)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadBooks()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteBook = async (row) => {
  await ElMessageBox.confirm('确定要删除这本书吗？', '提示', { type: 'warning' })
  try {
    await bookApi.delete(row.id)
    ElMessage.success('删除成功')
    loadBooks()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const borrowBook = async (row) => {
  try {
    await bookApi.borrow(row.id)
    ElMessage.success('借阅成功')
    loadBooks()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '借阅失败')
  }
}

const viewBook = (row) => {
  currentBook.value = row
  detailVisible.value = true
}

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.books-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
