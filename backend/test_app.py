"""
图书馆管理系统 - 单元测试
"""
import unittest
import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app, init_data, load_data, save_data, hash_password, DATA_DIR

class TestLibrarySystem(unittest.TestCase):
    """图书馆管理系统测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试前初始化"""
        app.testing = True
        cls.client = app.test_client()
        # 备份原有数据
        cls.backup_files = {}
        for filename in ['users.json', 'books.json', 'borrow_records.json']:
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls.backup_files[filename] = f.read()
        init_data()
    
    @classmethod
    def tearDownClass(cls):
        """测试后恢复数据"""
        for filename, content in cls.backup_files.items():
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def setUp(self):
        """每个测试前重新初始化"""
        init_data()
    
    # ==================== 用户模块测试 ====================
    def test_login_success(self):
        """TC-001: 测试正确用户名密码登录"""
        response = self.client.post('/api/auth/login', 
            json={'username': 'admin', 'password': 'admin123'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['username'], 'admin')
        self.assertEqual(data['data']['role'], 'admin')
    
    def test_login_wrong_password(self):
        """TC-002: 测试错误密码登录"""
        response = self.client.post('/api/auth/login',
            json={'username': 'admin', 'password': 'wrongpass'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('密码错误', data['message'])
    
    def test_login_user_not_exist(self):
        """TC-003: 测试不存在的用户登录"""
        response = self.client.post('/api/auth/login',
            json={'username': 'notexist', 'password': '123456'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('用户不存在', data['message'])
    
    def test_register_success(self):
        """TC-004: 测试用户注册成功"""
        response = self.client.post('/api/auth/register',
            json={
                'username': 'testuser',
                'password': 'test123',
                'name': '测试用户',
                'email': 'test@test.com',
                'phone': '13900000000'
            },
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('注册成功', data['message'])
    
    def test_register_duplicate_username(self):
        """TC-005: 测试重复用户名注册"""
        response = self.client.post('/api/auth/register',
            json={'username': 'admin', 'password': 'test123'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('用户名已存在', data['message'])
    
    # ==================== 图书模块测试 ====================
    def test_get_books(self):
        """TC-006: 测试获取图书列表"""
        response = self.client.get('/api/books')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('list', data['data'])
        self.assertGreater(len(data['data']['list']), 0)
    
    def test_get_books_with_filter(self):
        """TC-007: 测试按书名筛选图书"""
        response = self.client.get('/api/books?title=JavaScript')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        for book in data['data']['list']:
            self.assertIn('JavaScript', book['title'])
    
    def test_add_book_success(self):
        """TC-008: 测试添加图书成功"""
        response = self.client.post('/api/books',
            json={
                'isbn': '978-7-000-00000-0',
                'title': '测试图书',
                'author': '测试作者',
                'publisher': '测试出版社',
                'category': '测试',
                'price': 50.00,
                'total': 5
            },
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['title'], '测试图书')
    
    def test_add_book_duplicate_isbn(self):
        """TC-009: 测试添加重复ISBN图书"""
        # 先获取现有图书的ISBN
        books = load_data('books.json')
        existing_isbn = books[0]['isbn']
        
        response = self.client.post('/api/books',
            json={
                'isbn': existing_isbn,
                'title': '重复ISBN图书',
                'author': '测试',
                'category': '测试',
                'total': 1
            },
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('ISBN已存在', data['message'])
    
    def test_delete_book(self):
        """TC-010: 测试删除图书"""
        books = load_data('books.json')
        book_id = books[-1]['id']
        
        response = self.client.delete(f'/api/books/{book_id}')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
    
    # ==================== 借阅模块测试 ====================
    def test_borrow_book_success(self):
        """TC-011: 测试借阅图书成功"""
        books = load_data('books.json')
        available_book = next(b for b in books if b['stock'] > 0)
        
        response = self.client.post('/api/borrow',
            json={
                'userId': 1,
                'bookId': available_book['id'],
                'userName': '管理员'
            },
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['status'], 'borrowed')
    
    def test_borrow_book_no_stock(self):
        """TC-012: 测试库存为0时借书"""
        # 将某本书库存设为0
        books = load_data('books.json')
        books[0]['stock'] = 0
        save_data('books.json', books)
        
        response = self.client.post('/api/borrow',
            json={'userId': 1, 'bookId': books[0]['id']},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('库存不足', data['message'])
    
    def test_borrow_book_already_borrowed(self):
        """TC-013: 测试重复借阅同一本书"""
        books = load_data('books.json')
        book_id = books[0]['id']
        
        # 第一次借阅
        self.client.post('/api/borrow',
            json={'userId': 1, 'bookId': book_id, 'userName': '测试'},
            content_type='application/json')
        
        # 第二次借阅同一本书
        response = self.client.post('/api/borrow',
            json={'userId': 1, 'bookId': book_id, 'userName': '测试'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('已借阅', data['message'])
    
    def test_return_book_success(self):
        """TC-014: 测试归还图书成功"""
        # 先借一本书
        books = load_data('books.json')
        book_id = books[1]['id']
        
        borrow_response = self.client.post('/api/borrow',
            json={'userId': 1, 'bookId': book_id, 'userName': '测试'},
            content_type='application/json')
        record_id = json.loads(borrow_response.data)['data']['id']
        
        # 归还
        response = self.client.post(f'/api/borrow/{record_id}/return')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['status'], 'returned')
    
    def test_return_book_already_returned(self):
        """TC-015: 测试重复归还图书"""
        # 先借一本书并归还
        books = load_data('books.json')
        book_id = books[2]['id']
        
        borrow_response = self.client.post('/api/borrow',
            json={'userId': 1, 'bookId': book_id, 'userName': '测试'},
            content_type='application/json')
        record_id = json.loads(borrow_response.data)['data']['id']
        
        # 第一次归还
        self.client.post(f'/api/borrow/{record_id}/return')
        
        # 第二次归还
        response = self.client.post(f'/api/borrow/{record_id}/return')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('已归还', data['message'])
    
    # ==================== 统计模块测试 ====================
    def test_get_statistics(self):
        """TC-016: 测试获取统计数据"""
        response = self.client.get('/api/statistics')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('totalBorrows', data['data'])
        self.assertIn('totalBooks', data['data'])
        self.assertIn('bookRanking', data['data'])
    
    def test_get_categories(self):
        """TC-017: 测试获取图书分类"""
        response = self.client.get('/api/books/categories')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIsInstance(data['data'], list)
    
    # ==================== 分页测试 ====================
    def test_books_pagination(self):
        """TC-018: 测试图书分页功能"""
        response = self.client.get('/api/books?page=1&pageSize=2')
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertLessEqual(len(data['data']['list']), 2)
        self.assertEqual(data['data']['page'], 1)
        self.assertEqual(data['data']['pageSize'], 2)


class TestPasswordSecurity(unittest.TestCase):
    """密码安全测试"""
    
    def test_password_hash(self):
        """TC-019: 测试密码哈希"""
        password = 'test123'
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertEqual(len(hashed), 64)  # SHA256 输出64个字符
    
    def test_password_hash_consistency(self):
        """TC-020: 测试密码哈希一致性"""
        password = 'test123'
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertEqual(hash1, hash2)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
