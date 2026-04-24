import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
    redirect: to => {
      const userStore = useUserStore()
      // 审计员默认进入审计看板，其他人进入数据大屏
      if (userStore.isAuditor) {
        return { path: '/dashboard/audit' }
      }
      return { path: '/dashboard/data' }
    },
    children: [
      {
        path: 'data',
        name: 'DataDashboard',
        component: () => import('../views/DataDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'audit',
        name: 'AuditDashboard',
        component: () => import('../views/AuditDashboard.vue'),
        meta: { requiresAuth: true, requiresAuditor: true }
      },
      {
        path: 'books',
        name: 'Books',
        component: () => import('../views/Books.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'borrow',
        name: 'Borrow',
        component: () => import('../views/Borrow.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('../views/Roles.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('../views/Announcements.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('../views/Logs.vue'),
        meta: { requiresAuth: true, requiresAuditor: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else if (to.meta.requiresAdmin && userStore.user?.role_id !== 1) {
    next('/dashboard')
  } else if (to.meta.requiresAuditor && ![1, 3].includes(userStore.user?.role_id)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
