<template>
  <div class="borrow-page">
    <!-- 借阅操作卡片 -->
    <el-card shadow="hover" class="borrow-card">
      <template #header>
        <div class="card-header">
          <span>借阅图书</span>
        </div>
      </template>
      <el-form :inline="true" :model="borrowForm" class="borrow-form">
        <el-form-item label="选择图书">
          <el-select v-model="borrowForm.bookId" placeholder="请选择图书" filterable style="width: 300px;">
            <el-option
              v-for="book in availableBooks"
              :key="book.id"
              :label="`${book.title} (库存: ${book.stock})`"
              :value="book.id"
              :disabled="book.stock <= 0"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleBorrow" :disabled="!borrowForm.bookId">
            <el-icon><Tickets /></el-icon>确认借阅
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 借阅记录 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>{{ userStore.isAdmin ? '所有借阅记录' : '我的借阅记录' }}</span>
        </div>
      </template>
      
      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="search-form">
        <el-form-item label="书名">
          <el-input v-model="filters.bookTitle" placeholder="请输入书名" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="借阅中" value="borrowed" />
            <el-option label="已归还" value="returned" />
            <el-option label="已逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 记录列表 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="bookTitle" label="书名" min-width="180" />
        <el-table-column v-if="userStore.isAdmin" prop="userName" label="借阅人" width="100" />
        <el-table-column prop="borrowDate" label="借阅日期" width="120">
          <template #default="{ row }">{{ formatDate(row.borrowDate) }}</template>
        </el-table-column>
        <el-table-column prop="dueDate" label="应还日期" width="120">
          <template #default="{ row }">{{ formatDate(row.dueDate) }}</template>
        </el-table-column>
        <el-table-column prop="returnDate" label="归还日期" width="120">
          <template #default="{ row }">{{ row.returnDate ? formatDate(row.returnDate) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fine" label="罚款" width="80">
          <template #default="{ row }">
            <span :class="{ 'fine-amount': row.fine > 0 }">¥{{ row.fine.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'returned'"
              type="success"
              size="small"
              @click="handleReturn(row)"
            >
              还书
            </el-button>
            <span v-else class="returned-text">已归还</span>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'
import { useBookStore } from '../store/book'
import { useBorrowStore } from '../store/borrow'

const userStore = useUserStore()
const bookStore = useBookStore()
const borrowStore = useBorrowStore()

const loading = ref(false)
const borrowForm = reactive({ bookId: null })
const filters = reactive({ bookTitle: '', status: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])

const availableBooks = computed(() => bookStore.getAllBooks())

function fetchData() {
  loading.value = true
  const queryFilters = { ...filters }
  // 非管理员只能看自己的记录
  if (!userStore.isAdmin) {
    queryFilters.userId = userStore.currentUser.id
  }
  const { data, total } = borrowStore.getRecordsPaginated(pagination.page, pagination.pageSize, queryFilters)
  tableData.value = data
  pagination.total = total
  loading.value = false
}

function search() {
  pagination.page = 1
  fetchData()
}

function resetFilters() {
  filters.bookTitle = ''
  filters.status = ''
  search()
}

function handleBorrow() {
  const book = bookStore.getBookById(borrowForm.bookId)
  if (!book) return
  
  ElMessageBox.confirm(`确定借阅《${book.title}》吗？借阅期限为30天。`, '确认借阅', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    try {
      borrowStore.borrowBook(
        userStore.currentUser.id,
        book.id,
        userStore.currentUser.name || userStore.currentUser.username,
        book.title
      )
      ElMessage.success('借阅成功')
      borrowForm.bookId = null
      fetchData()
    } catch (error) {
      ElMessage.error(error.message)
    }
  })
}

function handleReturn(record) {
  const message = record.fine > 0
    ? `确定归还《${record.bookTitle}》吗？逾期罚款：¥${record.fine.toFixed(2)}`
    : `确定归还《${record.bookTitle}》吗？`
  
  ElMessageBox.confirm(message, '确认归还', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: record.fine > 0 ? 'warning' : 'info'
  }).then(() => {
    try {
      const result = borrowStore.returnBook(record.id)
      if (result.fine > 0) {
        ElMessage.warning(`归还成功，逾期罚款：¥${result.fine.toFixed(2)}`)
      } else {
        ElMessage.success('归还成功')
      }
      fetchData()
    } catch (error) {
      ElMessage.error(error.message)
    }
  })
}

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

onMounted(() => fetchData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.borrow-card { margin-bottom: 20px; }
.search-form { margin-bottom: 20px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.fine-amount { color: #f56c6c; font-weight: bold; }
.returned-text { color: #67c23a; font-size: 12px; }
</style>
