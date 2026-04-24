<template>
  <div class="audit-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" :size="40" color="#409EFF"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_count }}</div>
              <div class="stat-label">总日志数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" :size="40" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_count }}</div>
              <div class="stat-label">今日操作</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" :size="40" color="#E6A23C"><Reading /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ bookOps }}</div>
              <div class="stat-label">图书管理操作</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" :size="40" color="#F56C6C"><List /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ borrowOps }}</div>
              <div class="stat-label">借阅管理操作</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>按模块分布</span>
          </template>
          <div ref="moduleChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>按操作类型分布</span>
          </template>
          <div ref="actionChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近7天操作趋势</span>
          </template>
          <div ref="trendChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最新操作日志</span>
          </template>
          <el-table :data="latestLogs" style="width: 100%" size="small" border>
            <el-table-column prop="op_time" label="时间" width="160">
              <template #default="{ row }">{{ formatTime(row.op_time) }}</template>
            </el-table-column>
            <el-table-column prop="username" label="操作人" width="100" />
            <el-table-column prop="module" label="模块" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="moduleTagType(row.module)">{{ moduleLabel(row.module) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action" label="操作" width="100" />
            <el-table-column prop="detail" label="详情" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { logApi } from '../api/modules'
import { ElMessage } from 'element-plus'

const moduleChart = ref(null)
const actionChart = ref(null)
const trendChart = ref(null)

const stats = ref({
  total_count: 0,
  today_count: 0,
  module_stats: [],
  action_stats: [],
  date_stats: []
})

const latestLogs = ref([])
let charts = []

const bookOps = computed(() => {
  const m = stats.value.module_stats.find(item => item.module === 'books')
  return m ? m.count : 0
})

const borrowOps = computed(() => {
  const m = stats.value.module_stats.find(item => item.module === 'borrows')
  return m ? m.count : 0
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
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const initChart = (refEl, option) => {
  if (!refEl) return null
  const chart = echarts.init(refEl)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

const loadStats = async () => {
  try {
    const res = await logApi.getStats()
    stats.value = res.data

    // 加载最新日志
    const logRes = await logApi.getAll({ page: 1, per_page: 10 })
    latestLogs.value = logRes.data.logs || []

    renderCharts()
  } catch (error) {
    ElMessage.error('加载审计统计失败')
    console.error(error)
  }
}

const renderCharts = () => {
  // 模块分布饼图
  if (moduleChart.value) {
    const moduleData = stats.value.module_stats || []
    initChart(moduleChart.value, {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}' },
        data: moduleData.map(m => ({
          value: m.count,
          name: moduleLabel(m.module)
        }))
      }]
    })
  }

  // 操作类型饼图
  if (actionChart.value) {
    const actionData = stats.value.action_stats || []
    const colorMap = {
      '新增图书': '#409EFF',
      '编辑图书': '#67C23A',
      '删除图书': '#F56C6C',
      '借阅图书': '#E6A23C',
      '归还图书': '#909399'
    }
    initChart(actionChart.value, {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: actionData.map(a => ({
          value: a.count,
          name: a.action,
          itemStyle: { color: colorMap[a.action] || '#999' }
        })),
        label: { show: true, formatter: '{b}: {c}' }
      }]
    })
  }

  // 趋势柱状图
  if (trendChart.value) {
    const dateData = stats.value.date_stats || []
    initChart(trendChart.value, {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: dateData.map(d => d.date.slice(5)),
        axisLabel: { rotate: 0 }
      },
      yAxis: { type: 'value', minInterval: 1 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      series: [{
        type: 'bar',
        data: dateData.map(d => d.count),
        itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%'
      }]
    })
  }
}

onMounted(() => {
  loadStats()
})

onUnmounted(() => {
  charts.forEach(chart => chart.dispose())
})
</script>

<style scoped>
.audit-dashboard {
  padding: 20px;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.charts-row {
  margin-bottom: 20px;
}
</style>