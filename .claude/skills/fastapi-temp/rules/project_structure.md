# FastAPI 项目结构规范

## 标准目录结构

```
project_name/
├── dependencies/          # 依赖项模块
├── docs/                  # 相关文档与手册
├── items/                 # 数据结构模块（基于 pydantic）
├── logs/                  # 日志文件目录
├── middlewares/           # 中间件目录
├── models/                # 数据库 ORM 模块
├── routers/               # 路由模块
├── scripts/               # 脚本目录（区分 linux 和 windows）
├── services/              # 服务逻辑模块
├── settings/              # 配置模块
├── statics/               # 静态资源目录
│   ├── certificates/      # 证书目录
│   ├── icons/             # 图标目录
│   ├── javascripts/       # JavaScript 脚本
│   ├── jsons/             # JSON 数据
│   └── styles/            # 样式文件
├── temps/                 # 缓存目录
├── tests/                 # 测试代码目录
├── tools/                 # 命令行工具类目录
├── utils/                 # 公用工具模块
│   └── clients/           # 客户端工具（如 Redis、MinIO）
├── __init__.py
├── app.py                 # 启动项目入口文件
├── requirements.txt       # 项目依赖包
└── README.md              # 项目说明文档
```

## 目录用途说明

### dependencies/
存放依赖注入相关的函数和类，用于 FastAPI 的 Depends 机制。

### items/
基于 pydantic 的数据结构模块，用于请求和响应的自动化解析和验证。

### middlewares/
存放中间件实现，如权限中间件、会话中间件等。

### models/
数据库 ORM 模块，使用 SQLAlchemy 实现数据表映射。所有模型必须继承 BaseModel。

### routers/
路由模块，每个路由文件定义一个 APIRouter 实例。必须保留 swagger_router.py。

### services/
业务逻辑实现层，与 routers 对应，路由层只负责参数接收和响应，具体逻辑在 services 实现。

### settings/
配置模块，存放各类配置项，如目录配置、环境配置、文件配置等。

### utils/
公用工具模块，存放各类工具函数和常量定义。

### tests/
测试代码目录，存放单元测试和集成测试。
