import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useBookStore } from './book'

export const useBorrowStore = defineStore('borrow', () => {
  const borrowRecords = ref(JSON.parse(localStorage.getItem('borrowRecords') || '[]'))
  
  // 借阅期限（天）
  const BORROW_DAYS = 30
  
  // 保存到本地存储
  function saveRecords() {
    localStorage.setItem('borrowRecords', JSON.stringify(borrowRecords.value))
  }

  // 借书
  function borrowBook(userId, bookId, userName, bookTitle) {
    const bookStore = useBookStore()
    const book = bookStore.getBookById(bookId)
    
    if (!book) throw new Error('图书不存在')
    if (book.stock <= 0) throw new Error('库存不足')
    
    // 检查是否已借阅该书且未归还
    const existing = borrowRecords.value.find(
      r => r.userId === userId && r.bookId === bookId && r.status === 'borrowed'
    )
    if (existing) throw new Error('您已借阅此书，请先归还')
    
    const now = new Date()
    const dueDate = new Date(now.getTime() + BORROW_DAYS * 24 * 60 * 60 * 1000)
    
    const record = {
      id: Math.max(...borrowRecords.value.map(r => r.id), 0) + 1,
      userId,
      bookId,
      userName,
      bookTitle,
      borrowDate: now.toISOString(),
      dueDate: dueDate.toISOString(),
      returnDate: null,
      status: 'borrowed', // borrowed, returned, overdue
      fine: 0
    }
    
    borrowRecords.value.push(record)
    bookStore.updateStock(bookId, -1)
    saveRecords()
    
    return record
  }

  // 还书
  function returnBook(recordId) {
    const bookStore = useBookStore()
    const record = borrowRecords.value.find(r => r.id === recordId)
    
    if (!record) throw new Error('借阅记录不存在')
    if (record.status === 'returned') throw new Error('已归还')
    
    const now = new Date()
    const dueDate = new Date(record.dueDate)
    
    record.returnDate = now.toISOString()
    record.status = 'returned'
    
    // 计算逾期罚款（每天0.5元）
    if (now > dueDate) {
      const overdueDays = Math.ceil((now - dueDate) / (24 * 60 * 60 * 1000))
      record.fine = overdueDays * 0.5
    }
    
    bookStore.updateStock(record.bookId, 1)
    saveRecords()
    
    return record
  }

  // 获取用户借阅记录
  function getUserRecords(userId) {
    return borrowRecords.value.filter(r => r.userId === userId)
  }

  // 获取所有借阅记录（分页）
  function getRecordsPaginated(page = 1, pageSize = 10, filters = {}) {
    let result = [...borrowRecords.value]
    
    // 更新逾期状态
    const now = new Date()
    result.forEach(r => {
      if (r.status === 'borrowed' && new Date(r.dueDate) < now) {
        r.status = 'overdue'
      }
    })
    
    // 筛选
    if (filters.userId) {
      result = result.filter(r => r.userId === filters.userId)
    }
    if (filters.status) {
      result = result.filter(r => r.status === filters.status)
    }
    if (filters.bookTitle) {
      result = result.filter(r => r.bookTitle.includes(filters.bookTitle))
    }
    
    // 按借阅时间倒序
    result.sort((a, b) => new Date(b.borrowDate) - new Date(a.borrowDate))
    
    const total = result.length
    const start = (page - 1) * pageSize
    const data = result.slice(start, start + pageSize)
    
    return { data, total, page, pageSize }
  }

  // 获取借阅统计
  function getStatistics() {
    const now = new Date()
    const records = borrowRecords.value
    
    // 总借阅次数
    const totalBorrows = records.length
    
    // 当前借出数量
    const currentBorrowed = records.filter(r => r.status !== 'returned').length
    
    // 逾期数量
    const overdueCount = records.filter(r => 
      r.status === 'borrowed' && new Date(r.dueDate) < now
    ).length
    
    // 图书借阅排行
    const bookBorrowCount = {}
    records.forEach(r => {
      bookBorrowCount[r.bookTitle] = (bookBorrowCount[r.bookTitle] || 0) + 1
    })
    const bookRanking = Object.entries(bookBorrowCount)
      .map(([title, count]) => ({ title, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
    
    // 月度借阅统计（最近6个月）
    const monthlyStats = []
    for (let i = 5; i >= 0; i--) {
      const date = new Date()
      date.setMonth(date.getMonth() - i)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const count = records.filter(r => {
        const borrowDate = new Date(r.borrowDate)
        return borrowDate.getFullYear() === year && borrowDate.getMonth() + 1 === month
      }).length
      monthlyStats.push({ month: `${year}-${String(month).padStart(2, '0')}`, count })
    }
    
    // 分类借阅统计
    const bookStore = useBookStore()
    const categoryStats = {}
    records.forEach(r => {
      const book = bookStore.getBookById(r.bookId)
      if (book) {
        categoryStats[book.category] = (categoryStats[book.category] || 0) + 1
      }
    })
    
    return {
      totalBorrows,
      currentBorrowed,
      overdueCount,
      bookRanking,
      monthlyStats,
      categoryStats
    }
  }

  return {
    borrowRecords,
    borrowBook,
    returnBook,
    getUserRecords,
    getRecordsPaginated,
    getStatistics
  }
})
