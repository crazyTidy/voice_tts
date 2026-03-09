---
name: fastapi-temp
description: 快速生成基于 FastAPI 的标准化项目模板。当用户需要创建新的 FastAPI 项目、搭建 FastAPI 应用、初始化 FastAPI 服务，或者提到"基于模板创建项目"、"FastAPI 脚手架"时使用此 skill。即使用户只是说"创建一个 API 项目"或"新建后端服务"，也应该考虑使用此 skill。
---

# FastAPI 项目模板生成器

这个 skill 帮助你快速生成标准化的 FastAPI 项目，基于经过验证的模板架构，包含完整的目录结构、工具脚本和最佳实践。

## 何时使用

当用户需要：
- 创建新的 FastAPI 项目
- 搭建 FastAPI 应用或服务
- 基于标准模板初始化项目
- 快速启动一个后端 API 项目

## 生成新项目

使用 `scripts/create_project.py` 脚本生成新项目：

```bash
python scripts/create_project.py <项目名称> [目标目录]
```

参数说明：
- `项目名称`：新项目的名称（必填）
- `目标目录`：生成项目的位置（可选，默认为当前目录）

示例：
```bash
# 在当前目录生成名为 my_api 的项目
python scripts/create_project.py my_api

# 在指定目录生成项目
python scripts/create_project.py my_api /path/to/projects
```

## 项目生成过程

脚本会自动执行以下操作：

1. **复制模板**：将完整的模板目录复制到目标位置
2. **重命名项目**：将目录名改为用户指定的项目名
3. **替换项目名称**：在以下文件中替换所有 `fastapi_module_template` 为新项目名：
   - `compile_app.py`
   - `compile_tool.py`
   - `README.md`
4. **清理文件**：删除不需要的文件（如 `.git` 目录）

## 架构规则

生成的项目遵循严格的架构规范，确保代码质量和可维护性。所有规则文档位于 `rules/` 目录：

### 项目结构规范（rules/project_structure.md）
定义标准目录结构和各目录用途：
- `routers/` - 路由定义
- `services/` - 业务逻辑
- `models/` - 数据库模型
- `items/` - 请求/响应数据结构
- `middlewares/` - 中间件
- `utils/` - 工具函数
- `settings/` - 配置管理
- `tests/` - 测试代码

### 命名规范（rules/naming_conventions.md）
- 路由文件：`xxx_router.py`，变量名必须为 `router`
- 服务文件：`xxx_service.py`
- 模型文件：`xxx_model.py`
- 数据结构：`xxx_item.py`
- 工具文件：`xxx_util.py`
- 测试文件：`test_xxx.py`

### 代码标准（rules/code_standards.md）
- 严格遵循 PEP8 规范
- 使用相对导入
- 引用文件名而非直接导入函数
- 使用 black 和 isort 格式化代码

### 架构约束（rules/architecture.md）
- 数据库 ID 必须使用 UUID4
- Depends 使用标准写法
- 路由不能直接返回 await 结果

## 开发新功能时的规则应用

当用户需要在生成的项目中添加新功能时，严格遵循以下规则：

### 添加新路由
1. 在 `routers/` 创建 `xxx_router.py`
2. 定义 `router = APIRouter()`
3. 在 `services/` 创建对应的 `xxx_service.py` 实现业务逻辑
4. 在 `app.py` 中引入：`app.include_router(xxx_router.router)`

### 添加数据模型
1. 在 `models/` 创建 `xxx_model.py`
2. 继承 `BaseModel` 基类
3. ID 字段使用 UUID4

### 添加请求/响应结构
1. 在 `items/` 创建 `xxx_item.py`
2. 使用 pydantic 定义数据结构

### 添加工具函数
1. 在 `utils/` 创建 `xxx_util.py`
2. 导入时使用：`from .utils import xxx_util`

### 代码格式化
生成代码后，运行格式化脚本确保符合 PEP8：
```bash
# Linux
./scripts/format.sh

# Windows
scripts\format.bat
```

## 重要提醒

在为用户生成任何代码时，必须：
1. 查阅对应的规则文档
2. 严格遵循命名规范
3. 使用正确的导入方式
4. 遵循架构约束
5. 确保代码符合 PEP8 规范
