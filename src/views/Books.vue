<template>
  <div class="books-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>图书管理</span>
          <el-button v-if="userStore.isAdmin" type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon>新增图书
          </el-button>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="filters" class="search-form">
        <el-form-item label="书名">
          <el-input v-model="filters.title" placeholder="请输入书名" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="filters.author" placeholder="请输入作者" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="选择分类" clearable>
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 图书列表 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="title" label="书名" min-width="180" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="publisher" label="出版社" width="140" />
        <el-table-column prop="category" label="分类" width="80" />
        <el-table-column prop="price" label="价格" width="80">
          <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="库存/总量" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock > 0 ? 'success' : 'danger'" size="small">
              {{ row.stock }}/{{ row.total }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewBook(row)">详情</el-button>
            <el-button v-if="userStore.isAdmin" type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-button v-if="userStore.isAdmin" type="danger" size="small" @click="deleteBook(row)">删除</el-button>
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
    
    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑图书' : '新增图书'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="ISBN" prop="isbn">
              <el-input v-model="form.isbn" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input v-model="form.title" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input v-model="form.author" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出版社" prop="publisher">
              <el-input v-model="form.publisher" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="选择分类" allow-create filterable>
                <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number v-model="form.price" :min="0" :precision="2" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总量" prop="total">
              <el-input-number v-model="form.total" :min="1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出版日期">
              <el-date-picker v-model="form.publishDate" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="图书详情" width="500px">
      <el-descriptions :column="2" border v-if="currentBook">
        <el-descriptions-item label="ISBN">{{ currentBook.isbn }}</el-descriptions-item>
        <el-descriptions-item label="书名">{{ currentBook.title }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentBook.author }}</el-descriptions-item>
        <el-descriptions-item label="出版社">{{ currentBook.publisher }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentBook.category }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ currentBook.price?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="库存">{{ currentBook.stock }}</el-descriptions-item>
        <el-descriptions-item label="总量">{{ currentBook.total }}</el-descriptions-item>
        <el-descriptions-item label="出版日期">{{ currentBook.publishDate }}</el-descriptions-item>
        <el-descriptions-item label="简介" :span="2">{{ currentBook.description || '暂无简介' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'
import { useBookStore } from '../store/book'

const userStore = useUserStore()
const bookStore = useBookStore()

const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const currentBook = ref(null)
const formRef = ref(null)

const filters = reactive({ title: '', author: '', category: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])

const categories = computed(() => bookStore.getCategories())

const form = reactive({
  isbn: '', title: '', author: '', publisher: '',
  category: '', price: 0, total: 1, publishDate: '', description: ''
})

const rules = {
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入出版社', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  total: [{ required: true, message: '请输入总量', trigger: 'blur' }]
}

function fetchData() {
  loading.value = true
  const { data, total } = bookStore.getBooksPaginated(pagination.page, pagination.pageSize, filters)
  tableData.value = data
  pagination.total = total
  loading.value = false
}

function search() {
  pagination.page = 1
  fetchData()
}

function resetFilters() {
  filters.title = ''
  filters.author = ''
  filters.category = ''
  search()
}

function openDialog(book = null) {
  isEdit.value = !!book
  if (book) {
    Object.assign(form, book)
  } else {
    Object.assign(form, { isbn: '', title: '', author: '', publisher: '', category: '', price: 0, total: 1, publishDate: '', description: '' })
  }
  dialogVisible.value = true
}

function viewBook(book) {
  currentBook.value = book
  detailVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          bookStore.updateBook(form.id, form)
          ElMessage.success('更新成功')
        } else {
          bookStore.addBook(form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(error.message)
      }
    }
  })
}

function deleteBook(book) {
  ElMessageBox.confirm(`确定删除《${book.title}》吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    bookStore.deleteBook(book.id)
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => fetchData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
