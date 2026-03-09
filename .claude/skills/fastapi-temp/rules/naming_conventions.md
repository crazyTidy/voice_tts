# FastAPI 命名规范

## 文件命名规范

### 路由文件
- 格式：`xxx_router.py`
- 示例：`hello_world_router.py`, `user_router.py`
- 变量命名：统一使用 `router = APIRouter()`

### 服务文件
- 格式：`xxx_service.py`
- 示例：`user_service.py`, `auth_service.py`

### 数据模型文件
- 格式：`xxx_model.py`
- 示例：`user_model.py`, `order_model.py`
- 必须继承 `BaseModel` 基类

### 数据结构文件（Items）
- 格式：`xxx_item.py`
- 示例：`user_item.py`, `login_item.py`

### 配置文件
- 格式：`xxx_config.py`
- 示例：`environment_config.py`, `file_config.py`

### 工具文件
- 格式：`xxx_util.py`
- 示例：`file_util.py`, `http_util.py`

### 测试文件
- 格式：`test_xxx.py`
- 示例：`test_hello_world.py`, `test_file_util.py`

## 导入规范

### 正确的导入方式
引用文件名，不要直接导入具体函数或变量：

```python
# 正确
from .settings import file_config, environment_config
from .utils import log_util

# 使用
environment_config.HOST
log_util.set_log(debug=True)
```

### 错误的导入方式
```python
# 错误
from .settings.environment_config import HOST, PORT
from .utils.log_util import set_log

# 使用
HOST
set_log(debug=True)
```

## 变量命名规范

### 路由变量
所有路由文件中的 APIRouter 实例必须命名为 `router`：

```python
from fastapi import APIRouter

router = APIRouter()
```

### 数据库 ID 规范
- 必须使用 UUID4
- 禁止使用自增 ID
