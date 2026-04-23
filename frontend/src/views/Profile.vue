<template>
  <div class="profile-page">
    <el-card header="个人中心">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ userStore.user?.name }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userStore.user?.email }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ userStore.user?.role }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userStore.user?.register_time }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ userStore.user?.last_login }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>修改密码</h3>
      <el-form :model="passwordForm" :rules="rules" ref="formRef" label-width="100px" style="max-width: 400px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="loading">提交</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store/user'
import { authApi } from '../api/modules'

const userStore = useUserStore()
const loading = ref(false)
const formRef = ref(null)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码至少 6 位', trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateConfirm, trigger: 'blur' }]
}

const changePassword = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authApi.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
      ElMessage.success('密码修改成功')
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '修改失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.profile-page {
  padding: 20px;
}
</style>
