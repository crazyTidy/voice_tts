# FastAPI 架构规范

## 依赖注入（Depends）规范

### 正确写法
```python
from fastapi import Depends
from sqlalchemy.orm import Session

def login(login_items: dict, db: Session = Depends(get_db)):
    pass
```

### 错误写法
```python
from typing_extensions import Annotated

def login(login_items: dict, db: Annotated[Session, Depends(get_db)]):
    pass
```

### 注意事项
- `get_db` 函数不能使用 `yield` 关键字返回数据

## 数据库规范

### ID 字段规范
- 必须使用 UUID4
- 禁止使用自增 ID

### ORM 模型规范
- 所有模型必须继承 `BaseModel` 基类
- 模型文件命名：`xxx_model.py`
- 放置在 `models/` 目录

## 路由返回值规范

### 禁止直接返回 await
错误写法：
```python
@router.get("/")
async def do_await():
    return await async_function()
```

正确写法：
```python
from fastapi.responses import Response

@router.get("/")
async def do_await():
    return Response(await async_function())
```
