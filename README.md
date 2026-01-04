# 图书馆管理系统

基于 Vue 3 + Flask 的图书馆管理系统

## 技术栈

### 前端
- Vue 3.4
- Element Plus 2.4
- Pinia 2.1
- Vue Router 4.2
- Axios 1.6
- Vite 5.0

### 后端
- Python 3.x
- Flask
- Flask-CORS

### 数据存储
- JSON 文件持久化

## 项目结构

```
library-system/
├── backend/                # 后端服务
│   ├── app.py              # Flask 主程序
│   ├── requirements.txt    # Python 依赖
│   └── data/               # 数据存储目录
├── src/                    # 前端源码
│   ├── views/              # 页面组件
│   ├── store/              # Pinia 状态管理
│   ├── router/             # 路由配置
│   └── utils/              # 工具函数
├── package.json            # 前端依赖
└── vite.config.js          # Vite 配置
```

## 运行说明

### 1. 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
npm install
```

### 2. 启动服务

#### 启动后端（端口 5000）
```bash
cd backend
python app.py
```

#### 启动前端（端口 5173）
```bash
npm run dev
```

### 3. 访问系统
- 前端地址：http://localhost:5173
- 后端API：http://localhost:5000

### 4. 默认账户
- 用户名：admin
- 密码：admin123

## 依赖清单

### Python 依赖 (requirements.txt)
```
flask
flask-cors
```

### Node.js 依赖 (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^4.5.0"
  }
}
```

## 功能模块

1. **用户管理** - 登录/注册/用户信息管理
2. **图书管理** - 图书增删改查/分类管理
3. **借阅管理** - 借书/还书/逾期罚款
4. **统计报表** - 借阅排行/月度统计/分类统计
