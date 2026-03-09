#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FastAPI 项目生成脚本"""
import os
import shutil
import sys
from pathlib import Path


def replace_in_file(file_path, old_text, new_text):
    """替换文件中的文本"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_text, new_text)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_project(project_name, target_dir='.'):
    """生成新项目"""
    # 获取模板路径
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'template' / 'fastapi_module_template'

    if not template_dir.exists():
        print(f"错误：模板目录不存在 {template_dir}")
        return False

    # 目标路径
    target_path = Path(target_dir) / project_name

    if target_path.exists():
        print(f"错误：目标目录已存在 {target_path}")
        return False

    print(f"正在生成项目 {project_name}...")

    # 复制模板
    shutil.copytree(template_dir, target_path)

    # 替换项目名称
    files_to_replace = [
        target_path / 'compile_app.py',
        target_path / 'compile_tool.py',
        target_path / 'README.md'
    ]

    for file_path in files_to_replace:
        if file_path.exists():
            replace_in_file(file_path, 'fastapi_module_template', project_name)

    print(f"[OK] 项目生成成功：{target_path}")
    print(f"\n下一步：")
    print(f"  cd {project_name}")
    print(f"  python pip_requirements.py")
    print(f"  python -u -m {project_name}.app")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python create_project.py <项目名称> [目标目录]")
        sys.exit(1)

    project_name = sys.argv[1]
    target_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    success = create_project(project_name, target_dir)
    sys.exit(0 if success else 1)
