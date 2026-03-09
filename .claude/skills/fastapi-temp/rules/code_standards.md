# FastAPI 代码标准

## PEP8 规范

所有代码必须严格遵循 PEP8 规范。使用以下工具进行格式化：

- **black**：代码格式化
- **isort**：导入语句排序

模板提供了格式化脚本：
```bash
# Linux
./scripts/format.sh

# Windows
scripts\format.bat
```

## 导入规范

### 使用相对导入
在 Python 开发时，必须使用相对引用：

```python
# 正确
from .routers import hello_world_router
from .settings import environment_config
from .utils import log_util

# 错误
import fastapi_module_template.routers.hello_world_router
```

### 导入顺序
按照 PEP8 标准，导入应按以下顺序分组：
1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入

## 路由编写规范

### 路由定义
在 routers 目录注册路由，具体实现在 services 目录：

```python
# routers/hello_world_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def do_get_hello_world():
    return "Hello World!"
```

### 在 app.py 中引入
```python
from .routers import hello_world_router

app.include_router(hello_world_router.router)
```
