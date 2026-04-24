import api from './index'

export const authApi = {
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },
  register(userData) {
    return api.post('/auth/register', userData)
  },
  changePassword(oldPassword, newPassword) {
    return api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword })
  },
  resetPassword(email) {
    return api.post('/auth/reset-password', { email })
  }
}

export const userApi = {
  getAll() {
    return api.get('/users')
  },
  getById(id) {
    return api.get(`/users/${id}`)
  },
  create(userData) {
    return api.post('/users', userData)
  },
  update(id, userData) {
    return api.put(`/users/${id}`, userData)
  },
  delete(id) {
    return api.delete(`/users/${id}`)
  },
  toggleStatus(id) {
    return api.patch(`/users/${id}/toggle-status`)
  },
  resetPassword(id) {
    return api.post(`/users/${id}/reset-password`)
  }
}

export const bookApi = {
  getAll(params) {
    return api.get('/books', { params })
  },
  getById(id) {
    return api.get(`/books/${id}`)
  },
  create(bookData) {
    return api.post('/books', bookData)
  },
  update(id, bookData) {
    return api.put(`/books/${id}`, bookData)
  },
  delete(id) {
    return api.delete(`/books/${id}`)
  },
  borrow(id) {
    return api.post(`/books/${id}/borrow`)
  },
  return(id) {
    return api.post(`/books/${id}/return`)
  },
  collect(id) {
    return api.post(`/books/${id}/collect`)
  },
  getPublishers() {
    return api.get('/books/publishers')
  },
  getCategories() {
    return api.get('/books/categories')
  }
}

export const borrowApi = {
  getAll(params) {
    return api.get('/borrows', { params })
  },
  getMyBorrows() {
    return api.get('/borrows/my')
  },
  returnBook(id) {
    return api.post(`/borrows/${id}/return`)
  }
}

export const dashboardApi = {
  getStats() {
    return api.get('/dashboard/stats')
  },
  getPublisherStats() {
    return api.get('/dashboard/publishers')
  },
  getCategoryStats() {
    return api.get('/dashboard/categories')
  },
  getTopRated() {
    return api.get('/dashboard/top-rated')
  },
  getStatusStats() {
    return api.get('/dashboard/status')
  }
}

export const announcementApi = {
  getAll() {
    return api.get('/announcements')
  },
  create(data) {
    return api.post('/announcements', data)
  },
  delete(id) {
    return api.delete(`/announcements/${id}`)
  }
}

export const logApi = {
  getAll(params) {
    return api.get('/logs', { params })
  },
  getStats() {
    return api.get('/logs/stats')
  }
}

export const roleApi = {
  getAll() {
    return api.get('/roles')
  },
  create(data) {
    return api.post('/roles', data)
  },
  update(id, data) {
    return api.put(`/roles/${id}`, data)
  },
  delete(id) {
    return api.delete(`/roles/${id}`)
  }
}
