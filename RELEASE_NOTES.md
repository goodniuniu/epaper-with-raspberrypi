# 每日单词墨水屏显示系统 v1.1.0

## 📦 发布包内容

### 🔧 核心代码文件（统一命名规则）
```
src/
├── daily_word_config.py           # 系统配置管理
├── daily_word_api_client.py       # API客户端（获取单词和句子）
├── daily_word_display_controller.py # 墨水屏显示控制器
├── daily_word_main.py             # 主程序入口（推荐）
└── daily_word_test.py             # 系统测试脚本
```

### 📚 完整文档体系
```
docs/
├── README.md                      # 文档总览
├── installation-guide/            # 安装指南
│   ├── README.md                  # 安装流程总览
│   ├── 01-system-requirements.md # 系统要求
│   ├── 02-hardware-setup.md      # 硬件连接
│   ├── 03-software-installation.md # 软件安装
│   ├── 04-configuration.md       # 系统配置
│   ├── 05-deployment.md          # 部署运行
│   ├── 06-maintenance.md         # 维护管理
│   └── 07-troubleshooting.md     # 故障排除
├── user-manual/
│   └── user-guide.md             # 用户使用手册
├── api-reference/
│   └── api-documentation.md      # API接口文档
└── assets/scripts/
    ├── install.sh                 # 自动安装脚本
    └── manage.sh                  # 系统管理脚本
```

### 🛠️ 部署工具
```
install_daily_word.sh              # 一键安装脚本
daily_word_service.py              # 服务管理器
DEPLOYMENT_CHECKLIST.md           # 部署检查清单
```

### 📋 项目文档
```
README.md                          # 项目主页
PROJECT_STRUCTURE.md              # 项目结构说明
COMPLETION_SUMMARY.md             # 完成总结
RELEASE_NOTES.md                  # 发布说明（本文件）
```

## 🚀 快速部署

### 方法一：一键安装（推荐）
```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/daily-word-epaper/main/install_daily_word.sh | sudo bash

# 或者本地安装
sudo chmod +x install_daily_word.sh
sudo ./install_daily_word.sh
```

### 方法二：手动安装
```bash
# 1. 复制文件到目标目录
sudo mkdir -p /opt/daily-word-epaper
sudo cp -r src/ /opt/daily-word-epaper/
sudo cp -r docs/ /opt/daily-word-epaper/

# 2. 安装Python依赖
cd /opt/daily-word-epaper
python3 -m venv venv
source venv/bin/activate
pip install requests pillow pathlib typing-extensions

# 3. 测试系统
python src/daily_word_test.py

# 4. 运行系统
python src/daily_word_main.py --test
```

## 🎯 主要特性

### ✅ 功能特性
- **多源API支持**：集成多个单词和句子API
- **智能缓存**：本地缓存减少网络请求
- **备用内容**：内置高质量单词和句子库
- **墨水屏优化**：专为E-Paper显示优化的布局
- **多种运行模式**：支持一次性、定时、守护进程模式
- **完整日志**：详细的运行日志和错误追踪

### ✅ 技术特性
- **模块化设计**：清晰的代码结构，易于维护
- **配置驱动**：灵活的配置系统
- **错误恢复**：完善的异常处理和自动恢复
- **服务集成**：systemd服务支持
- **硬件抽象**：支持多种墨水屏型号

### ✅ 部署特性
- **一键安装**：自动化安装脚本
- **服务管理**：完整的服务管理工具
- **文档完整**：详细的安装和使用文档
- **测试覆盖**：完整的系统测试

## 📊 系统要求

### 硬件要求
- **树莓派4/5**（推荐）或兼容的ARM设备
- **墨水屏**：支持SPI接口的E-Paper显示屏
- **存储空间**：至少500MB可用空间
- **内存**：至少512MB RAM

### 软件要求
- **操作系统**：Raspberry Pi OS（推荐）或Ubuntu
- **Python**：3.7或更高版本
- **网络连接**：用于获取API内容（可选）

## 🔧 管理命令

安装完成后，可使用以下命令管理系统：

```bash
# 服务管理
daily-word start      # 启动服务
daily-word stop       # 停止服务
daily-word restart    # 重启服务
daily-word status     # 查看状态

# 内容管理
daily-word update     # 更新显示
daily-word clear      # 清空显示
daily-word test       # 测试系统

# 系统管理
daily-word logs       # 查看日志
daily-word enable     # 开机自启
daily-word disable    # 禁用自启
```

## 📁 目录结构

安装后的目录结构：
```
/opt/daily-word-epaper/
├── src/                    # 源代码
├── docs/                   # 文档
├── data/                   # 数据文件
├── logs/                   # 日志文件
├── cache/                  # 缓存文件
├── venv/                   # Python虚拟环境
└── manage.sh              # 管理脚本
```

## 🐛 已知问题

1. **网络API限制**：某些API可能有访问频率限制
2. **字体依赖**：需要安装适当的字体文件
3. **权限问题**：需要适当的GPIO和SPI权限

## 🔄 更新日志

### v1.1.0 (2025-10-29)
- 安全：默认启用 SSL 证书校验；支持自定义 CA；提供可选的非安全回退开关（不推荐）。
- 跨平台：文件管理器在 Windows 上不再依赖 fcntl，使用 `os.replace` 原子写入；统一使用 `DATA_DIR`。
- 预览：模拟模式下预览图保存至 `DATA_DIR/debug_preview.png`。
- 版本：项目版本提升至 `1.1.0`。

### v1.0.0 (2025-08-30)
– 初始版本发布，包含 API 客户端、显示控制器、运行模式、文档与安装脚本等。

## 📞 支持

如遇到问题，请：

1. **查看文档**：`docs/installation-guide/07-troubleshooting.md`
2. **运行测试**：`daily-word test`
3. **查看日志**：`daily-word logs`
4. **检查状态**：`daily-word status`

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

感谢以下开源项目和API服务：
- Raspberry Pi Foundation
- Waveshare E-Paper库
- 各种单词和句子API服务提供商

---

**每日单词墨水屏显示系统** - 让学习英语成为每天的美好时光 📚✨
