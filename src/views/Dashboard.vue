<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon :size="32"><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalBooks }}</div>
            <div class="stat-label">图书总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon :size="32"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.currentBorrowed }}</div>
            <div class="stat-label">当前借出</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <el-icon :size="32"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overdueCount }}</div>
            <div class="stat-label">逾期未还</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="$router.push('/books')">
              <el-icon><Plus /></el-icon>图书入库
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/borrow')">
              <el-icon><Tickets /></el-icon>借阅管理
            </el-button>
            <el-button type="warning" size="large" @click="$router.push('/statistics')">
              <el-icon><DataAnalysis /></el-icon>查看报表
            </el-button>
            <el-button v-if="userStore.isAdmin" type="danger" size="large" @click="$router.push('/users')">
              <el-icon><User /></el-icon>用户管理
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>欢迎</span>
            </div>
          </template>
          <div class="welcome-info">
            <el-avatar :size="64" icon="UserFilled" />
            <div class="welcome-text">
              <h3>{{ userStore.currentUser?.name || userStore.currentUser?.username }}</h3>
              <p>{{ userStore.isAdmin ? '系统管理员' : '普通用户' }}</p>
              <p class="time">{{ currentTime }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 借阅排行 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>借阅排行榜 TOP 5</span>
            </div>
          </template>
          <el-table :data="stats.bookRanking?.slice(0, 5) || []" stripe>
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="title" label="书名" />
            <el-table-column prop="count" label="借阅次数" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近期借阅记录</span>
            </div>
          </template>
          <el-table :data="recentRecords" stripe>
            <el-table-column prop="bookTitle" label="书名" />
            <el-table-column prop="userName" label="借阅人" width="100" />
            <el-table-column prop="borrowDate" label="借阅日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.borrowDate) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../store/user'
import { useBookStore } from '../store/book'
import { useBorrowStore } from '../store/borrow'

const userStore = useUserStore()
const bookStore = useBookStore()
const borrowStore = useBorrowStore()

const currentTime = ref(new Date().toLocaleString('zh-CN'))

// 更新时间
setInterval(() => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}, 1000)

const stats = computed(() => {
  const borrowStats = borrowStore.getStatistics()
  return {
    totalBooks: bookStore.books.length,
    totalUsers: userStore.users.length,
    currentBorrowed: borrowStats.currentBorrowed,
    overdueCount: borrowStats.overdueCount,
    bookRanking: borrowStats.bookRanking
  }
})

const recentRecords = computed(() => {
  const { data } = borrowStore.getRecordsPaginated(1, 5)
  return data
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function getStatusType(status) {
  const map = { borrowed: 'primary', returned: 'success', overdue: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { borrowed: '借阅中', returned: '已归还', overdue: '已逾期' }
  return map[status] || status
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.quick-actions {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.welcome-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-text h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.welcome-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.welcome-text .time {
  margin-top: 10px;
  color: #999;
}

.chart-section {
  margin-bottom: 20px;
}
</style>
