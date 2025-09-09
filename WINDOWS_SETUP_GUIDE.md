# Windows 开发环境设置指南

## 🎯 项目概述

这是一个基于树莓派和墨水屏的每日英语单词学习系统，支持：
- 📚 每日单词学习（单词、音标、定义、例句）
- 💬 励志句子显示
- 🖥️ 多种墨水屏支持
- 🔄 自动定时更新
- 📱 智能缓存机制

## 🚀 Windows 开发环境快速设置

### 1. 环境准备

```powershell
# 检查Python版本（需要3.9+）
python --version

# 如果没有Python，请从官网下载安装
# https://www.python.org/downloads/
```

### 2. 创建虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果执行策略限制，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. 安装依赖

```powershell
# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 4. 配置项目

```powershell
# 复制配置文件
copy config.ini.example config.ini

# 编辑配置文件（使用你喜欢的编辑器）
notepad config.ini
```

## 🔧 开发和测试

### 运行测试

```powershell
# 运行简单测试
python src/daily_word_test_simple.py

# 运行完整测试
python src/daily_word_test.py

# 测试API连接
python src/test_word_api.py
```

### 模拟显示测试

```powershell
# 在Windows上模拟墨水屏显示（生成图片文件）
python src/daily_word_display.py --simulate

# 测试单词获取
python src/class_word_api.py

# 测试配置加载
python src/get_config.py
```

### 查看项目结构

```powershell
# 验证项目完整性
python validate_project.py

# 查看项目统计
python -c "import os; print(f'Python文件数: {len([f for f in os.listdir(\"src\") if f.endswith(\".py\")])}')"
```

## 📊 项目文件说明

### 核心模块
- `src/daily_word_rpi.py` - 主程序入口
- `src/class_word_api.py` - 单词API客户端
- `src/epaper_display_rpi.py` - 墨水屏显示控制
- `src/word_config.py` - 系统配置

### 测试文件
- `src/daily_word_test_simple.py` - 简化测试
- `src/daily_word_test.py` - 完整测试
- `src/test_word_api.py` - API测试

### 配置文件
- `config.ini` - 主配置文件
- `src/word_config.py` - Python配置
- `requirements.txt` - 依赖包列表

## 🎨 开发工作流

### 1. 代码修改
```powershell
# 修改源代码后，运行测试
python src/daily_word_test_simple.py

# 检查语法
python -m py_compile src/your_file.py
```

### 2. 功能测试
```powershell
# 测试单词获取
python -c "from src.class_word_api import WordAPI; api = WordAPI(); print(api.get_daily_word())"

# 测试配置加载
python -c "from src.word_config import DISPLAY_CONFIG; print(DISPLAY_CONFIG)"
```

### 3. 提交代码
```powershell
# 添加修改的文件
git add .

# 提交更改
git commit -m "描述你的修改"

# 查看状态
git status
```

## 🔍 调试技巧

### 查看日志
```powershell
# 查看应用日志
type data\daily_word.log

# 实时监控日志（需要安装Get-Content）
Get-Content data\daily_word.log -Wait
```

### 调试API
```powershell
# 测试网络连接
curl -I https://api.quotable.io/random

# 测试单词API
python -c "import requests; print(requests.get('https://api.quotable.io/random').json())"
```

### 环境检查
```powershell
# 检查Python包
pip list

# 检查虚拟环境
where python

# 检查项目文件
dir src\*.py
```

## 📱 部署到树莓派

### 1. 准备文件
```powershell
# 打包项目（排除不必要的文件）
git archive --format=tar.gz --output=daily-word-epaper.tar.gz HEAD
```

### 2. 传输到树莓派
```bash
# 在树莓派上执行
scp user@windows-pc:/path/to/daily-word-epaper.tar.gz ~/
tar -xzf daily-word-epaper.tar.gz
cd daily-word-epaper
```

### 3. 树莓派安装
```bash
# 运行安装脚本
chmod +x install_rpi.sh
./install_rpi.sh

# 启动服务
./manage.sh start
./manage.sh enable
```

## 🛠️ 常见问题解决

### Python环境问题
```powershell
# 重新创建虚拟环境
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 依赖安装问题
```powershell
# 升级pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### 编码问题
```powershell
# 设置环境变量
$env:PYTHONIOENCODING="utf-8"

# 或在代码中设置
# -*- coding: utf-8 -*-
```

## 📚 学习资源

- **项目文档**: `docs/` 目录
- **API参考**: `docs/api-reference/`
- **安装指南**: `docs/installation-guide/`
- **用户手册**: `docs/user-manual/`

## 🤝 贡献代码

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

## 📞 获取帮助

- 查看 `README.md` 了解项目概述
- 查看 `PROJECT_STRUCTURE.md` 了解项目结构
- 运行 `python validate_project.py` 检查项目完整性
- 查看 `docs/troubleshooting/` 目录获取故障排除指南

---

**开始您的每日单词学习系统开发之旅！** 🚀📚✨