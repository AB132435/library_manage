<template>
  <div class="books-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ userStore.isAdmin ? '图书管理' : '图书查询' }}</span>
          <el-button type="primary" @click="showAddDialog" v-if="userStore.isAdmin">新增图书</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.search" placeholder="书名 / ISBN" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category_id" placeholder="全部分类" clearable style="width: 140px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出版社">
          <el-select v-model="searchForm.publisher_id" placeholder="全部出版社" clearable style="width: 160px">
            <el-option v-for="p in publishers" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadBooks">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="books" v-loading="loading" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="书名" min-width="160" />
        <el-table-column prop="isbn" label="ISBN" width="130" />
        <el-table-column label="出版社" width="130">
          <template #default="{ row }">{{ row.publisher || '-' }}</template>
        </el-table-column>
        <el-table-column label="分类" width="100">
          <template #default="{ row }">{{ row.category || '-' }}</template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="80">
          <template #default="{ row }">¥{{ row.price || 0 }}</template>
        </el-table-column>
        <el-table-column label="借阅状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock > 0 ? 'success' : 'danger'">
              {{ row.stock > 0 ? '可借阅' : '已借出' }}
            </el-tag>
          </template>
        </el-table-column>
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
          <el-input v-model="bookForm.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookForm.isbn" placeholder="请输入ISBN编号" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher_id">
          <el-select v-model="bookForm.publisher_id" placeholder="请选择出版社" clearable style="width: 100%">
            <el-option v-for="p in publishers" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="bookForm.category_id" placeholder="请选择分类" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="bookForm.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="bookForm.stock" :min="0" style="width: 100%" />
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
        <el-descriptions-item label="ISBN">{{ currentBook.isbn || '-' }}</el-descriptions-item>
        <el-descriptions-item label="出版社">{{ currentBook.publisher || '-' }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentBook.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ currentBook.price || 0 }}</el-descriptions-item>
        <el-descriptions-item label="库存">{{ currentBook.stock || 0 }}</el-descriptions-item>
        <el-descriptions-item label="借阅状态">
          <el-tag :type="currentBook.stock > 0 ? 'success' : 'danger'">
            {{ currentBook.stock > 0 ? '可借阅' : '已借出' }}
          </el-tag>
        </el-descriptions-item>
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
const publishers = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentBook = ref({})

const searchForm = reactive({
  search: '',
  category_id: null,
  publisher_id: null
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
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  publisher_id: [{ required: true, message: '请选择出版社', trigger: 'change' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

const loadBooks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (searchForm.search) params.search = searchForm.search
    if (searchForm.category_id) params.category_id = searchForm.category_id
    if (searchForm.publisher_id) params.publisher_id = searchForm.publisher_id

    const res = await bookApi.getAll(params)
    const data = res.data
    books.value = data.books || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载图书列表失败')
  } finally {
    loading.value = false
  }
}

const loadPublishers = async () => {
  try {
    const res = await bookApi.getPublishers()
    publishers.value = res.data || []
  } catch (error) {
    console.error('Failed to load publishers:', error)
  }
}

const loadCategories = async () => {
  try {
    const res = await bookApi.getCategories()
    categories.value = res.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const resetSearch = () => {
  searchForm.search = ''
  searchForm.category_id = null
  searchForm.publisher_id = null
  pagination.page = 1
  loadBooks()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(bookForm, {
    id: null,
    title: '',
    isbn: '',
    publisher_id: null,
    category_id: null,
    price: 0,
    stock: 1
  })
  dialogVisible.value = true
}

const editBook = (row) => {
  isEdit.value = true
  Object.assign(bookForm, {
    id: row.id,
    title: row.title,
    isbn: row.isbn || '',
    price: row.price || 0,
    stock: row.stock || 0,
    publisher_id: row.publisher_id || null,
    category_id: row.category_id || null
  })
  // 查找 publisher_id 和 category_id
  const pub = publishers.value.find(p => p.name === row.publisher)
  const cat = categories.value.find(c => c.name === row.category)
  if (pub) bookForm.publisher_id = pub.id
  if (cat) bookForm.category_id = cat.id
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        title: bookForm.title,
        isbn: bookForm.isbn,
        price: bookForm.price,
        stock: bookForm.stock,
        publisher_id: bookForm.publisher_id,
        category_id: bookForm.category_id
      }
      if (isEdit.value) {
        await bookApi.update(bookForm.id, payload)
        ElMessage.success('更新成功')
      } else {
        await bookApi.create(payload)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadBooks()
    } catch (error) {
      ElMessage.error(error.response?.data?.msg || '操作失败')
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
    ElMessage.error(error.response?.data?.msg || '删除失败')
  }
}

const borrowBook = async (row) => {
  try {
    await bookApi.borrow(row.id)
    ElMessage.success('借阅成功')
    loadBooks()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '借阅失败')
  }
}

const viewBook = (row) => {
  currentBook.value = row
  detailVisible.value = true
}

onMounted(() => {
  loadBooks()
  loadPublishers()
  loadCategories()
})
</script>

<style scoped>
.books-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>