<template>
  <div class="data-dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="4" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>出版社分布</template>
          <div ref="publisherChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>图书分类分布</template>
          <div ref="categoryChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>评分 TOP10</template>
          <div ref="topRatedChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>图书状态比例</template>
          <div ref="statusChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '../api/modules'
import { ElMessage } from 'element-plus'

const publisherChart = ref(null)
const categoryChart = ref(null)
const topRatedChart = ref(null)
const statusChart = ref(null)

const stats = ref([
  { label: '图书总数', value: 0 },
  { label: '用户总数', value: 0 },
  { label: '活跃用户', value: 0 },
  { label: '借阅中图书', value: 0 },
  { label: '逾期图书', value: 0 }
])

let charts = []
let timer = null

const loadStats = async () => {
  try {
    const res = await dashboardApi.getStats()
    const data = res.data
    stats.value = [
      { label: '图书总数', value: data.total_books || 0 },
      { label: '用户总数', value: data.total_users || 0 },
      { label: '活跃用户', value: data.active_users || 0 },
      { label: '借阅中图书', value: data.borrowed_books || 0 },
      { label: '逾期图书', value: data.overdue_books || 0 }
    ]
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const initChart = (refEl, option) => {
  if (!refEl) return
  const chart = echarts.init(refEl)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

const loadCharts = async () => {
  try {
    const [pubRes, catRes, topRes, statusRes] = await Promise.all([
      dashboardApi.getPublisherStats(),
      dashboardApi.getCategoryStats(),
      dashboardApi.getTopRated(),
      dashboardApi.getStatusStats()
    ])

    // Publisher chart
    if (publisherChart.value) {
      const pubData = pubRes.data
      initChart(publisherChart.value, {
        tooltip: { trigger: 'axis' },
        xAxis: { 
          type: 'category', 
          data: (pubData || []).map(i => i.publisher || i.name).slice(0, 10)
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: (pubData || []).map(i => i.book_count || i.count || 0).slice(0, 10),
          itemStyle: { color: '#409EFF' }
        }]
      })
    }

    // Category chart
    if (categoryChart.value) {
      const catData = catRes.data
      initChart(categoryChart.value, {
        tooltip: { trigger: 'axis' },
        xAxis: { 
          type: 'category', 
          data: (catData || []).map(i => i.category || i.name).slice(0, 10)
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: (catData || []).map(i => i.book_count || i.count || 0).slice(0, 10),
          itemStyle: { color: '#67C23A' }
        }]
      })
    }

    // Top rated chart
    if (topRatedChart.value) {
      const topData = topRes.data
      initChart(topRatedChart.value, {
        tooltip: { trigger: 'axis' },
        xAxis: { 
          type: 'category', 
          data: (topData || []).map(i => i.title || i.name).slice(0, 10)
        },
        yAxis: { type: 'value', min: 0 },
        series: [{
          type: 'bar',
          data: (topData || []).map(i => i.borrow_count || i.rating || 0).slice(0, 10),
          itemStyle: { color: '#E6A23C' }
        }]
      })
    }

    // Status chart
    if (statusChart.value) {
      const statusData = statusRes.data
      const statusList = statusData.status_stats || statusData || []
      initChart(statusChart.value, {
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '50%',
          data: statusList.map(i => ({ value: i.count, name: i.status })),
          label: { show: true, formatter: '{b}: {c} ({d}%)' }
        }]
      })
    }
  } catch (error) {
    ElMessage.error('加载图表数据失败')
    console.error(error)
  }
}

onMounted(() => {
  loadStats()
  loadCharts()
  timer = setInterval(() => {
    loadStats()
    loadCharts()
  }, 300000) // 5 minutes
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  charts.forEach(chart => chart.dispose())
})
</script>

<style scoped>
.data-dashboard {
  padding: 20px;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  margin-top: 10px;
  color: #909399;
}

.charts-row {
  margin-bottom: 20px;
}
</style>
