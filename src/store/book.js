import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBookStore = defineStore('book', () => {
  // 初始化示例图书数据
  const defaultBooks = [
    { id: 1, isbn: '978-7-111-42175-2', title: 'JavaScript高级程序设计', author: 'Nicholas C. Zakas', publisher: '机械工业出版社', category: '计算机', price: 99.00, stock: 5, total: 10, publishDate: '2020-01-01', description: 'JavaScript经典教程' },
    { id: 2, isbn: '978-7-111-48437-5', title: 'Vue.js设计与实现', author: '霍春阳', publisher: '人民邮电出版社', category: '计算机', price: 79.00, stock: 3, total: 8, publishDate: '2022-03-01', description: 'Vue.js 3源码解析' },
    { id: 3, isbn: '978-7-115-52148-6', title: '深入理解计算机系统', author: 'Randal E. Bryant', publisher: '机械工业出版社', category: '计算机', price: 139.00, stock: 2, total: 5, publishDate: '2016-07-01', description: '计算机系统经典教材' },
    { id: 4, isbn: '978-7-020-02308-4', title: '红楼梦', author: '曹雪芹', publisher: '人民文学出版社', category: '文学', price: 59.70, stock: 8, total: 15, publishDate: '1996-12-01', description: '中国古典四大名著之一' },
    { id: 5, isbn: '978-7-544-27827-2', title: '百年孤独', author: '加西亚·马尔克斯', publisher: '南海出版公司', category: '文学', price: 55.00, stock: 4, total: 10, publishDate: '2017-08-01', description: '魔幻现实主义文学代表作' },
    { id: 6, isbn: '978-7-108-06332-5', title: '人类简史', author: '尤瓦尔·赫拉利', publisher: '中信出版社', category: '历史', price: 68.00, stock: 6, total: 12, publishDate: '2014-11-01', description: '从认知革命到科学革命' },
    { id: 7, isbn: '978-7-5086-5562-7', title: '经济学原理', author: '曼昆', publisher: '北京大学出版社', category: '经济', price: 128.00, stock: 3, total: 8, publishDate: '2015-05-01', description: '经济学入门教材' },
    { id: 8, isbn: '978-7-5327-6548-6', title: '三体', author: '刘慈欣', publisher: '重庆出版社', category: '科幻', price: 95.00, stock: 7, total: 20, publishDate: '2008-01-01', description: '中国科幻里程碑之作' },
  ]

  const books = ref(JSON.parse(localStorage.getItem('books') || 'null') || defaultBooks)
  
  // 保存到本地存储
  function saveBooks() {
    localStorage.setItem('books', JSON.stringify(books.value))
  }

  // 获取所有图书
  function getAllBooks() {
    return books.value
  }

  // 分页查询
  function getBooksPaginated(page = 1, pageSize = 10, filters = {}) {
    let result = [...books.value]
    
    // 筛选
    if (filters.title) {
      result = result.filter(b => b.title.includes(filters.title))
    }
    if (filters.author) {
      result = result.filter(b => b.author.includes(filters.author))
    }
    if (filters.category) {
      result = result.filter(b => b.category === filters.category)
    }
    if (filters.isbn) {
      result = result.filter(b => b.isbn.includes(filters.isbn))
    }
    
    const total = result.length
    const start = (page - 1) * pageSize
    const data = result.slice(start, start + pageSize)
    
    return { data, total, page, pageSize }
  }

  // 添加图书
  function addBook(bookData) {
    if (books.value.find(b => b.isbn === bookData.isbn)) {
      throw new Error('ISBN已存在')
    }
    const newBook = {
      id: Math.max(...books.value.map(b => b.id), 0) + 1,
      ...bookData,
      stock: bookData.total || 1
    }
    books.value.push(newBook)
    saveBooks()
    return newBook
  }

  // 更新图书
  function updateBook(id, data) {
    const index = books.value.findIndex(b => b.id === id)
    if (index === -1) throw new Error('图书不存在')
    books.value[index] = { ...books.value[index], ...data }
    saveBooks()
    return books.value[index]
  }

  // 删除图书
  function deleteBook(id) {
    const index = books.value.findIndex(b => b.id === id)
    if (index === -1) throw new Error('图书不存在')
    books.value.splice(index, 1)
    saveBooks()
  }

  // 获取图书详情
  function getBookById(id) {
    return books.value.find(b => b.id === id)
  }

  // 获取分类列表
  function getCategories() {
    return [...new Set(books.value.map(b => b.category))]
  }

  // 更新库存
  function updateStock(id, change) {
    const book = books.value.find(b => b.id === id)
    if (!book) throw new Error('图书不存在')
    if (book.stock + change < 0) throw new Error('库存不足')
    if (book.stock + change > book.total) throw new Error('库存不能超过总量')
    book.stock += change
    saveBooks()
    return book
  }

  return {
    books,
    getAllBooks,
    getBooksPaginated,
    addBook,
    updateBook,
    deleteBook,
    getBookById,
    getCategories,
    updateStock
  }
})
