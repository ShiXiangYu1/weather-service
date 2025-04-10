# 天气查询服务

## 项目概述
这是一个基于FastAPI和第三方天气API的天气查询服务，用于查询城市天气信息、保存历史记录并提供数据可视化功能。

## 功能
- 城市天气查询：用户可以查询指定城市的当前天气情况和天气预报
- 历史记录保存：保存用户的查询历史，方便用户查看过去的查询记录
- 数据可视化：以图表方式展示天气数据，使数据更加直观

## 技术栈
- **后端框架**：FastAPI
- **数据库**：SQLite
- **第三方API**：OpenWeatherMap API
- **数据可视化**：Matplotlib

## 学习要点
- API调用与集成
- 异步请求处理
- 数据缓存策略

## 项目结构
```
weather_service/
├── app/
│   ├── main.py            # FastAPI 应用程序入口
│   ├── api/               # API 端点
│   │   ├── __init__.py
│   │   └── weather.py     # 天气相关API路由
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── weather.py     # 天气数据模型
│   │   └── schemas.py     # Pydantic 模型
│   ├── services/          # 业务逻辑
│   │   ├── __init__.py
│   │   ├── weather_service.py  # 天气服务
│   │   ├── cache_service.py    # 缓存服务
│   │   └── visualization_service.py  # 可视化服务
│   ├── database/          # 数据库相关
│   │   ├── __init__.py
│   │   └── database.py    # 数据库连接配置
│   ├── templates/         # HTML 模板
│   │   └── index.html     # 首页模板
│   └── utils/             # 工具函数
│       └── __init__.py
├── tests/                 # 单元测试
│   ├── __init__.py
│   ├── conftest.py        # 测试配置
│   ├── test_models.py     # 模型测试
│   ├── test_api.py        # API 测试
│   └── test_cache_service.py  # 缓存服务测试
├── static/                # 静态文件
├── .env                   # 环境变量
├── .env.example           # 环境变量示例
├── run.py                 # 应用启动脚本
└── requirements.txt       # 项目依赖
```

## 开发进度
- [x] 项目初始化
- [x] 项目结构搭建
- [x] 数据库设计与实现
- [x] 天气API集成
- [x] 天气查询功能实现
- [x] 历史记录功能实现
- [x] 数据可视化功能实现
- [x] 单元测试编写
- [x] 文档完善

## 安装与运行

### 前提条件
- Python 3.8 或更高版本
- pip 包管理工具
- OpenWeatherMap API密钥

### 安装步骤
1. 克隆仓库
```bash
git clone <repository-url>
cd weather-service
```

2. 安装依赖
```bash
pip install -r weather_service/requirements.txt
```

3. 配置环境变量
```bash
# 复制环境变量示例文件
cp weather_service/.env.example weather_service/.env

# 编辑.env文件，添加你的API密钥
# WEATHER_API_KEY=your_api_key_here
```

4. 运行应用
```bash
python weather_service/run.py
```

5. 访问应用
在浏览器中打开 http://127.0.0.1:8000/

### 运行测试
```bash
pytest weather_service/tests/
```

## API文档
启动应用后，访问以下链接查看详细的API文档：
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 主要API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/weather/current/{city}` | GET | 获取指定城市的当前天气 |
| `/weather/forecast/{city}` | GET | 获取指定城市的天气预报 |
| `/weather/visualization/temperature/{city}` | GET | 获取温度趋势图 |
| `/weather/visualization/dashboard/{city}` | GET | 获取天气数据仪表板 |
| `/weather/history` | GET | 获取查询历史记录 |

## 注意事项
- 使用前需要在.env文件中配置有效的OpenWeatherMap API密钥
- 首次运行时会自动创建SQLite数据库文件 

## Vercel部署说明

为了部署到Vercel平台，本项目提供了必要的配置文件。

### 部署步骤

1. **准备工作**
   - 确保项目根目录包含`vercel.json`配置文件
   - 确保项目根目录包含`requirements.txt`依赖文件
   - 确保`api/index.py`入口文件存在

2. **部署到Vercel**
   - 在Vercel网站上导入GitHub仓库
   - 或使用Vercel CLI进行部署:
     ```bash
     npm install -g vercel
     vercel login
     vercel
     ```

3. **环境变量配置**
   - 在Vercel项目设置中添加环境变量
   - 必须包含`WEATHER_API_KEY`等关键配置
   - 可以通过Vercel网站或CLI进行配置:
     ```bash
     vercel env add WEATHER_API_KEY
     ```

4. **部署后的注意事项**
   - 因为Vercel为无状态服务，数据库部分可能需要修改为使用外部数据库服务
   - 确保API请求量不超过Vercel免费版的限制
   - 文件系统操作应谨慎使用，建议使用外部存储服务

### 配置文件说明

- **vercel.json**: 定义了构建配置和路由规则
- **api/index.py**: Vercel的函数入口点，用于导入FastAPI应用

### 验证部署

部署成功后，可以通过以下方式验证:
- 访问`https://<your-project-name>.vercel.app/health`应返回健康状态
- 访问`https://<your-project-name>.vercel.app/docs`查看API文档 

### Vercel部署大小限制

由于Vercel对无服务器函数有250MB大小限制，而本项目的完整依赖（特别是数据可视化库）可能超过此限制，我们提供了两种解决方案：

#### 方案一：精简部署（推荐）

1. 使用精简版`requirements.txt`，移除大型依赖：
   - 移除matplotlib、plotly等数据可视化库
   - 移除测试相关依赖
   - 保留核心功能依赖

2. 修改`vercel.json`添加优化配置：
   ```json
   {
     "config": {
       "maxLambdaSize": "15mb",
       "excludeFiles": ["weather_service/tests/**", "weather_service/static/images/**"]
     }
   }
   ```

3. 使用API入口的错误处理，确保即使某些依赖缺失，应用仍能提供基本功能。

**注意**：使用此方案部署后，数据可视化功能将不可用，但基础天气查询功能仍然可用。

#### 方案二：拆分服务

对于需要完整功能的生产环境：

1. **API服务**：部署精简版到Vercel，提供基础天气查询功能
2. **可视化服务**：将数据可视化功能部署到支持大型依赖的平台（如Heroku、Railway等）
3. **前端整合**：通过前端应用整合两个后端服务

#### 方案三：使用其他部署平台

如果需要保留所有功能且不拆分服务，可以考虑以下平台：

1. **Railway**：支持更大的部署包大小
2. **Heroku**：提供更灵活的资源配置
3. **云服务器**：AWS、Azure或阿里云等提供的虚拟机
4. **Docker部署**：使用容器化部署到支持Docker的平台 