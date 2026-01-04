<template>
  <div class="statistics-page">
    <!-- 概览统计 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalBorrows }}</div>
            <div class="stat-label">总借阅次数</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#409EFF"><Tickets /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.currentBorrowed }}</div>
            <div class="stat-label">当前借出</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#67C23A"><Reading /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.overdueCount }}</div>
            <div class="stat-label">逾期未还</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#F56C6C"><Warning /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ bookStore.books.length }}</div>
            <div class="stat-label">图书总数</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#E6A23C"><Collection /></el-icon>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>借阅排行榜 TOP 10</span>
            </div>
          </template>
          <div class="ranking-list">
            <div v-for="(item, index) in stats.bookRanking" :key="index" class="ranking-item">
              <div class="ranking-info">
                <span class="ranking-index" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</span>
                <span class="ranking-title">{{ item.title }}</span>
              </div>
              <div class="ranking-bar-container">
                <div class="ranking-bar" :style="{ width: getBarWidth(item.count) + '%' }"></div>
                <span class="ranking-count">{{ item.count }}次</span>
              </div>
            </div>
            <el-empty v-if="!stats.bookRanking?.length" description="暂无借阅数据" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近6个月借阅趋势</span>
            </div>
          </template>
          <div class="monthly-chart">
            <div class="chart-bars">
              <div v-for="item in stats.monthlyStats" :key="item.month" class="chart-bar-wrapper">
                <div class="chart-bar" :style="{ height: getMonthlyBarHeight(item.count) + '%' }">
                  <span class="chart-value">{{ item.count }}</span>
                </div>
                <span class="chart-label">{{ item.month.slice(5) }}月</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分类统计 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分类借阅统计</span>
            </div>
          </template>
          <div class="category-stats">
            <div v-for="(count, category) in stats.categoryStats" :key="category" class="category-item">
              <span class="category-name">{{ category }}</span>
              <el-progress :percentage="getCategoryPercentage(count)" :stroke-width="20" :format="() => count + '次'" />
            </div>
            <el-empty v-if="Object.keys(stats.categoryStats || {}).length === 0" description="暂无分类数据" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>图书库存概览</span>
            </div>
          </template>
          <el-table :data="stockOverview" stripe max-height="300">
            <el-table-column prop="title" label="书名" />
            <el-table-column prop="stock" label="库存" width="80" />
            <el-table-column prop="total" label="总量" width="80" />
            <el-table-column label="库存率" width="120">
              <template #default="{ row }">
                <el-progress 
                  :percentage="Math.round((row.stock / row.total) * 100)" 
                  :status="row.stock === 0 ? 'exception' : row.stock < row.total * 0.3 ? 'warning' : 'success'"
                  :stroke-width="10"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBookStore } from '../store/book'
import { useBorrowStore } from '../store/borrow'

const bookStore = useBookStore()
const borrowStore = useBorrowStore()

const stats = computed(() => borrowStore.getStatistics())

const stockOverview = computed(() => {
  return [...bookStore.books]
    .sort((a, b) => (a.stock / a.total) - (b.stock / b.total))
    .slice(0, 10)
})

const maxBorrowCount = computed(() => {
  if (!stats.value.bookRanking?.length) return 1
  return Math.max(...stats.value.bookRanking.map(item => item.count))
})

const maxMonthlyCount = computed(() => {
  if (!stats.value.monthlyStats?.length) return 1
  return Math.max(...stats.value.monthlyStats.map(item => item.count), 1)
})

const totalCategoryCount = computed(() => {
  if (!stats.value.categoryStats) return 1
  return Object.values(stats.value.categoryStats).reduce((a, b) => a + b, 0) || 1
})

function getBarWidth(count) {
  return (count / maxBorrowCount.value) * 100
}

function getMonthlyBarHeight(count) {
  return Math.max((count / maxMonthlyCount.value) * 100, 5)
}

function getCategoryPercentage(count) {
  return Math.round((count / totalCategoryCount.value) * 100)
}
</script>

<style scoped>
.stat-row { margin-bottom: 20px; }

.stat-card :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
}

.stat-content { flex: 1; }

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.stat-icon { opacity: 0.8; }

.card-header {
  font-weight: bold;
}

.ranking-list { padding: 10px 0; }

.ranking-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.ranking-info {
  width: 180px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.ranking-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
}

.ranking-index.top-three {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.ranking-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.ranking-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.ranking-bar {
  height: 20px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 10px;
  min-width: 20px;
  transition: width 0.3s;
}

.ranking-count {
  font-size: 12px;
  color: #666;
  min-width: 40px;
}

.monthly-chart {
  height: 250px;
  padding: 20px;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
}

.chart-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 50px;
}

.chart-bar {
  width: 40px;
  background: linear-gradient(180deg, #409EFF, #67C23A);
  border-radius: 5px 5px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: 20px;
  transition: height 0.3s;
}

.chart-value {
  color: #fff;
  font-size: 12px;
  margin-top: 5px;
}

.chart-label {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.category-stats { padding: 10px 0; }

.category-item {
  margin-bottom: 20px;
}

.category-name {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}
</style>
