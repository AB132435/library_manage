<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog">新增用户</el-button>
        </div>
      </template>

      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role_name" label="角色" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button size="small" :type="row.is_active ? 'warning' : 'success'" @click="toggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" @click="resetPassword(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="userForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi, roleApi } from '../api/modules'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const roles = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const userForm = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  role_id: null
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }]
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.getAll()
    const data = res.data
    users.value = data.users || data || []
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const res = await roleApi.getAll()
    const data = res.data
    roles.value = data.roles || data || []
  } catch (error) {
    console.error('Failed to load roles:', error)
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(userForm, { id: null, username: '', email: '', password: '', role_id: 2 })
  dialogVisible.value = true
}

const editUser = (row) => {
  isEdit.value = true
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    email: row.email || '',
    role_id: row.role_id
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
        await userApi.update(userForm.id, userForm)
        ElMessage.success('更新成功')
      } else {
        await userApi.create(userForm)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadUsers()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const toggleStatus = async (row) => {
  try {
    await userApi.toggleStatus(row.id)
    ElMessage.success('操作成功')
    loadUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const resetPassword = async (row) => {
  await ElMessageBox.confirm(`确定要重置用户 "${row.username}" 的密码为默认密码吗？`, '提示', { type: 'warning' })
  try {
    await userApi.resetPassword(row.id)
    ElMessage.success('密码已重置为 123456')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '重置失败')
  }
}

const deleteUser = async (row) => {
  await ElMessageBox.confirm('确定要删除该用户吗？', '提示', { type: 'warning' })
  try {
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

onMounted(() => {
  loadUsers()
  loadRoles()
})
</script>

<style scoped>
.users-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
