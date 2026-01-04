"""
图书馆管理系统 - Flask后端API服务
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import hashlib
import json
import os

app = Flask(__name__)
CORS(app)

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 工具函数
def load_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """密码哈希"""
    salt = 'library_system_salt_2024'
    return hashlib.sha256((password + salt).encode()).hexdigest()

def get_next_id(data_list):
    """获取下一个ID"""
    if not data_list:
        return 1
    return max(item['id'] for item in data_list) + 1

# 初始化数据
def init_data():
    # 初始化管理员
    users = load_data('users.json')
    if not users:
        users = [{
            'id': 1,
            'username': 'admin',
            'password': hash_password('admin123'),
            'role': 'admin',
            'name': '系统管理员',
            'email': 'admin@library.com',
            'phone': '13800000000',
            'createTime': datetime.now().isoformat()
        }]
        save_data('users.json', users)
    
    # 初始化图书
    books = load_data('books.json')
    if not books:
        books = [
            {'id': 1, 'isbn': '978-7-111-42175-2', 'title': 'JavaScript高级程序设计', 'author': 'Nicholas C. Zakas', 'publisher': '机械工业出版社', 'category': '计算机', 'price': 99.00, 'stock': 5, 'total': 10, 'publishDate': '2020-01-01', 'description': 'JavaScript经典教程'},
            {'id': 2, 'isbn': '978-7-111-48437-5', 'title': 'Vue.js设计与实现', 'author': '霍春阳', 'publisher': '人民邮电出版社', 'category': '计算机', 'price': 79.00, 'stock': 3, 'total': 8, 'publishDate': '2022-03-01', 'description': 'Vue.js 3源码解析'},
            {'id': 3, 'isbn': '978-7-115-52148-6', 'title': '深入理解计算机系统', 'author': 'Randal E. Bryant', 'publisher': '机械工业出版社', 'category': '计算机', 'price': 139.00, 'stock': 2, 'total': 5, 'publishDate': '2016-07-01', 'description': '计算机系统经典教材'},
            {'id': 4, 'isbn': '978-7-020-02308-4', 'title': '红楼梦', 'author': '曹雪芹', 'publisher': '人民文学出版社', 'category': '文学', 'price': 59.70, 'stock': 8, 'total': 15, 'publishDate': '1996-12-01', 'description': '中国古典四大名著之一'},
            {'id': 5, 'isbn': '978-7-544-27827-2', 'title': '百年孤独', 'author': '加西亚·马尔克斯', 'publisher': '南海出版公司', 'category': '文学', 'price': 55.00, 'stock': 4, 'total': 10, 'publishDate': '2017-08-01', 'description': '魔幻现实主义文学代表作'},
            {'id': 6, 'isbn': '978-7-108-06332-5', 'title': '人类简史', 'author': '尤瓦尔·赫拉利', 'publisher': '中信出版社', 'category': '历史', 'price': 68.00, 'stock': 6, 'total': 12, 'publishDate': '2014-11-01', 'description': '从认知革命到科学革命'},
            {'id': 7, 'isbn': '978-7-5086-5562-7', 'title': '经济学原理', 'author': '曼昆', 'publisher': '北京大学出版社', 'category': '经济', 'price': 128.00, 'stock': 3, 'total': 8, 'publishDate': '2015-05-01', 'description': '经济学入门教材'},
            {'id': 8, 'isbn': '978-7-5327-6548-6', 'title': '三体', 'author': '刘慈欣', 'publisher': '重庆出版社', 'category': '科幻', 'price': 95.00, 'stock': 7, 'total': 20, 'publishDate': '2008-01-01', 'description': '中国科幻里程碑之作'},
        ]
        save_data('books.json', books)

# ==================== 用户接口 ====================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    users = load_data('users.json')
    user = next((u for u in users if u['username'] == data['username']), None)
    if not user:
        return jsonify({'code': 400, 'message': '用户不存在'}), 400
    if user['password'] != hash_password(data['password']):
        return jsonify({'code': 400, 'message': '密码错误'}), 400
    # 返回用户信息（不包含密码）
    user_info = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({'code': 200, 'data': user_info, 'message': '登录成功'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    users = load_data('users.json')
    if any(u['username'] == data['username'] for u in users):
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    new_user = {
        'id': get_next_id(users),
        'username': data['username'],
        'password': hash_password(data['password']),
        'role': 'user',
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'createTime': datetime.now().isoformat()
    }
    users.append(new_user)
    save_data('users.json', users)
    return jsonify({'code': 200, 'message': '注册成功'})

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = load_data('users.json')
    return jsonify({'code': 200, 'data': [{k: v for k, v in u.items() if k != 'password'} for u in users]})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    data = request.json
    users = load_data('users.json')
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    for key in ['name', 'email', 'phone', 'role']:
        if key in data:
            user[key] = data[key]
    if 'password' in data and data['password']:
        user['password'] = hash_password(data['password'])
    save_data('users.json', users)
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    users = load_data('users.json')
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    if user['role'] == 'admin':
        return jsonify({'code': 400, 'message': '不能删除管理员'}), 400
    users = [u for u in users if u['id'] != user_id]
    save_data('users.json', users)
    return jsonify({'code': 200, 'message': '删除成功'})

# ==================== 图书接口 ====================
@app.route('/api/books', methods=['GET'])
def get_books():
    """获取图书列表（支持分页和筛选）"""
    books = load_data('books.json')
    # 筛选
    title = request.args.get('title', '')
    author = request.args.get('author', '')
    category = request.args.get('category', '')
    if title:
        books = [b for b in books if title in b['title']]
    if author:
        books = [b for b in books if author in b['author']]
    if category:
        books = [b for b in books if b['category'] == category]
    # 分页
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    total = len(books)
    start = (page - 1) * page_size
    books = books[start:start + page_size]
    return jsonify({'code': 200, 'data': {'list': books, 'total': total, 'page': page, 'pageSize': page_size}})

@app.route('/api/books', methods=['POST'])
def add_book():
    """添加图书"""
    data = request.json
    books = load_data('books.json')
    if any(b['isbn'] == data['isbn'] for b in books):
        return jsonify({'code': 400, 'message': 'ISBN已存在'}), 400
    new_book = {
        'id': get_next_id(books),
        'isbn': data['isbn'],
        'title': data['title'],
        'author': data['author'],
        'publisher': data.get('publisher', ''),
        'category': data.get('category', ''),
        'price': data.get('price', 0),
        'stock': data.get('total', 1),
        'total': data.get('total', 1),
        'publishDate': data.get('publishDate', ''),
        'description': data.get('description', '')
    }
    books.append(new_book)
    save_data('books.json', books)
    return jsonify({'code': 200, 'data': new_book, 'message': '添加成功'})

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """更新图书"""
    data = request.json
    books = load_data('books.json')
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'code': 404, 'message': '图书不存在'}), 404
    for key in ['title', 'author', 'publisher', 'category', 'price', 'total', 'publishDate', 'description']:
        if key in data:
            book[key] = data[key]
    save_data('books.json', books)
    return jsonify({'code': 200, 'message': '更新成功'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """删除图书"""
    books = load_data('books.json')
    books = [b for b in books if b['id'] != book_id]
    save_data('books.json', books)
    return jsonify({'code': 200, 'message': '删除成功'})

@app.route('/api/books/categories', methods=['GET'])
def get_categories():
    """获取图书分类"""
    books = load_data('books.json')
    categories = list(set(b['category'] for b in books if b['category']))
    return jsonify({'code': 200, 'data': categories})

# ==================== 借阅接口 ====================
@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    """借书"""
    data = request.json
    user_id = data['userId']
    book_id = data['bookId']
    
    books = load_data('books.json')
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'code': 404, 'message': '图书不存在'}), 404
    if book['stock'] <= 0:
        return jsonify({'code': 400, 'message': '库存不足'}), 400
    
    records = load_data('borrow_records.json')
    # 检查是否已借阅
    existing = next((r for r in records if r['userId'] == user_id and r['bookId'] == book_id and r['status'] == 'borrowed'), None)
    if existing:
        return jsonify({'code': 400, 'message': '您已借阅此书，请先归还'}), 400
    
    now = datetime.now()
    due_date = now + timedelta(days=30)
    record = {
        'id': get_next_id(records) if records else 1,
        'userId': user_id,
        'bookId': book_id,
        'userName': data.get('userName', ''),
        'bookTitle': book['title'],
        'borrowDate': now.isoformat(),
        'dueDate': due_date.isoformat(),
        'returnDate': None,
        'status': 'borrowed',
        'fine': 0
    }
    records.append(record)
    book['stock'] -= 1
    save_data('borrow_records.json', records)
    save_data('books.json', books)
    return jsonify({'code': 200, 'data': record, 'message': '借阅成功'})

@app.route('/api/borrow/<int:record_id>/return', methods=['POST'])
def return_book(record_id):
    """还书"""
    records = load_data('borrow_records.json')
    record = next((r for r in records if r['id'] == record_id), None)
    if not record:
        return jsonify({'code': 404, 'message': '借阅记录不存在'}), 404
    if record['status'] == 'returned':
        return jsonify({'code': 400, 'message': '已归还'}), 400
    
    now = datetime.now()
    due_date = datetime.fromisoformat(record['dueDate'])
    record['returnDate'] = now.isoformat()
    record['status'] = 'returned'
    
    # 计算逾期罚款
    if now > due_date:
        overdue_days = (now - due_date).days
        record['fine'] = overdue_days * 0.5
    
    # 更新库存
    books = load_data('books.json')
    book = next((b for b in books if b['id'] == record['bookId']), None)
    if book:
        book['stock'] += 1
        save_data('books.json', books)
    
    save_data('borrow_records.json', records)
    return jsonify({'code': 200, 'data': record, 'message': '归还成功'})

@app.route('/api/borrow', methods=['GET'])
def get_borrow_records():
    """获取借阅记录"""
    records = load_data('borrow_records.json')
    user_id = request.args.get('userId')
    status = request.args.get('status')
    
    if user_id:
        records = [r for r in records if r['userId'] == int(user_id)]
    if status:
        records = [r for r in records if r['status'] == status]
    
    # 更新逾期状态
    now = datetime.now()
    for r in records:
        if r['status'] == 'borrowed' and datetime.fromisoformat(r['dueDate']) < now:
            r['status'] = 'overdue'
    
    records.sort(key=lambda x: x['borrowDate'], reverse=True)
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    total = len(records)
    start = (page - 1) * page_size
    records = records[start:start + page_size]
    
    return jsonify({'code': 200, 'data': {'list': records, 'total': total}})

# ==================== 统计接口 ====================
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    records = load_data('borrow_records.json')
    books = load_data('books.json')
    users = load_data('users.json')
    now = datetime.now()
    
    # 基础统计
    total_borrows = len(records)
    current_borrowed = len([r for r in records if r['status'] != 'returned'])
    overdue_count = len([r for r in records if r['status'] == 'borrowed' and datetime.fromisoformat(r['dueDate']) < now])
    
    # 借阅排行
    book_count = {}
    for r in records:
        book_count[r['bookTitle']] = book_count.get(r['bookTitle'], 0) + 1
    book_ranking = sorted([{'title': k, 'count': v} for k, v in book_count.items()], key=lambda x: x['count'], reverse=True)[:10]
    
    # 月度统计
    monthly_stats = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        count = len([r for r in records if datetime.fromisoformat(r['borrowDate']).year == year and datetime.fromisoformat(r['borrowDate']).month == month])
        monthly_stats.append({'month': f'{year}-{month:02d}', 'count': count})
    
    # 分类统计
    category_stats = {}
    for r in records:
        book = next((b for b in books if b['id'] == r['bookId']), None)
        if book:
            category_stats[book['category']] = category_stats.get(book['category'], 0) + 1
    
    return jsonify({
        'code': 200,
        'data': {
            'totalBorrows': total_borrows,
            'currentBorrowed': current_borrowed,
            'overdueCount': overdue_count,
            'totalBooks': len(books),
            'totalUsers': len(users),
            'bookRanking': book_ranking,
            'monthlyStats': monthly_stats,
            'categoryStats': category_stats
        }
    })

if __name__ == '__main__':
    init_data()
    print('='*50)
    print('图书馆管理系统后端服务启动')
    print('API地址: http://localhost:5000')
    print('='*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
