# 每日单词墨水屏显示系统 - 完整文档

## 📋 文档概述

欢迎使用每日单词墨水屏显示系统！这是一套完整的文档集合，包含从安装部署到日常使用的所有指南。

## 📚 文档结构

### 📁 安装指南 (`installation-guide/`)

完整的安装部署文档，确保您能在树莓派4/5上成功部署系统：

- **[总览](installation-guide/README.md)** - 安装流程概述
- **[系统要求](installation-guide/01-system-requirements.md)** - 硬件和软件要求
- **[硬件设置](installation-guide/02-hardware-setup.md)** - 墨水屏连接和配置
- **[软件安装](installation-guide/03-software-installation.md)** - 系统软件和依赖安装
- **[系统配置](installation-guide/04-configuration.md)** - 参数配置和个性化设置
- **[部署运行](installation-guide/05-deployment.md)** - 服务部署和启动配置
- **[维护管理](installation-guide/06-maintenance.md)** - 日常维护和监控
- **[故障排除](installation-guide/07-troubleshooting.md)** - 常见问题和解决方案

### 📖 用户手册 (`user-manual/`)

日常使用指南，帮助您充分利用系统功能：

- **[用户指南](user-manual/user-guide.md)** - 完整的用户使用手册

### 🔧 API参考 (`api-reference/`)

开发者文档，用于系统扩展和定制：

- **[API文档](api-reference/api-documentation.md)** - 完整的API参考文档

### 🛠️ 安装工具 (`assets/scripts/`)

自动化安装和管理脚本：

- **[自动安装脚本](assets/scripts/install.sh)** - 一键安装脚本
- **[系统管理脚本](assets/scripts/manage.sh)** - 日常管理工具

## 🚀 快速开始

### 方式一：自动安装（推荐）

```bash
# 下载并运行自动安装脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/daily-word-epaper/main/docs/assets/scripts/install.sh | bash

# 或者手动下载后运行
wget https://raw.githubusercontent.com/your-repo/daily-word-epaper/main/docs/assets/scripts/install.sh
chmod +x install.sh
./install.sh
```

### 方式二：手动安装

1. **查看系统要求** → [系统要求文档](installation-guide/01-system-requirements.md)
2. **连接硬件** → [硬件设置文档](installation-guide/02-hardware-setup.md)
3. **安装软件** → [软件安装文档](installation-guide/03-software-installation.md)
4. **配置系统** → [系统配置文档](installation-guide/04-configuration.md)
5. **部署运行** → [部署运行文档](installation-guide/05-deployment.md)

## 📊 系统特性

### ✨ 核心功能

- **📚 每日单词学习** - 自动获取每日英语单词，包含音标、定义、例句
- **💬 励志句子显示** - 每日更新励志名言和智慧句子
- **🖥️ 墨水屏显示** - 支持多种型号的墨水屏，低功耗显示
- **🔄 自动更新** - 可配置的定时更新，支持多种更新策略
- **📱 智能缓存** - 本地缓存机制，离线时使用备用内容

### 🛠️ 高级特性

- **🎨 主题定制** - 多种预设主题，支持自定义布局和样式
- **🌐 多API支持** - 支持多个内容源，自动故障转移
- **📊 学习统计** - 记录学习历史，提供统计分析
- **🔧 系统监控** - 实时监控系统状态和性能指标
- **🔄 自动维护** - 自动日志清理、系统优化、备份恢复

### 🎯 技术特点

- **🐍 Python 3.9+** - 现代Python开发，代码清晰易维护
- **🔌 GPIO控制** - 直接控制树莓派GPIO，支持SPI通信
- **📦 模块化设计** - 清晰的代码结构，易于扩展和定制
- **🛡️ 错误处理** - 完善的异常处理和恢复机制
- **📝 详细日志** - 完整的日志记录，便于调试和监控

## 🎯 适用场景

### 🏠 个人学习

- **英语学习者** - 每日单词积累，提升词汇量
- **学生群体** - 宿舍、书房的学习装饰
- **语言爱好者** - 沉浸式语言学习环境

### 🏢 教育机构

- **教室展示** - 课堂词汇展示和学习氛围营造
- **图书馆** - 阅读区域的学习内容展示
- **培训机构** - 英语培训的辅助工具

### 🏪 商业应用

- **咖啡厅/书店** - 文化氛围营造
- **办公室** - 员工学习激励
- **展示厅** - 智能家居演示

## 🔧 支持的硬件

### 🖥️ 主控设备

- **树莓派4 Model B** (推荐 4GB/8GB内存版本)
- **树莓派5** (全系列支持)
- **树莓派Zero 2 W** (性能受限，基本功能可用)

### 📺 墨水屏型号

- **Waveshare 2.13英寸** (250×122像素)
- **Waveshare 2.9英寸** (296×128像素)
- **Waveshare 4.2英寸** (400×300像素)
- **Waveshare 7.5英寸** (800×480像素)
- **其他兼容型号** (通过配置文件支持)

### 🔌 连接方式

- **SPI接口** - 标准4线SPI连接
- **GPIO控制** - RST、DC、BUSY信号控制
- **电源供应** - 3.3V/5V电源支持

## 📋 系统要求

### 💻 最低配置

- **CPU**: ARM Cortex-A72 (树莓派4) 或更高
- **内存**: 2GB RAM (推荐4GB+)
- **存储**: 16GB MicroSD卡 (推荐32GB+)
- **网络**: WiFi或以太网连接
- **系统**: Raspberry Pi OS (Bullseye或更新版本)

### 🌐 网络要求

- **互联网连接** - 用于获取每日内容
- **API访问** - 支持HTTPS连接
- **DNS解析** - 正常的域名解析功能

## 📖 使用指南

### 🎯 基本操作

```bash
# 进入项目目录
cd ~/daily-word-epaper

# 查看系统状态
./manage.sh status

# 手动更新显示
./manage.sh update

# 启动/停止服务
./manage.sh start
./manage.sh stop

# 查看日志
./manage.sh logs
```

### ⚙️ 配置定制

```bash
# 编辑配置文件
nano src/word_config.py

# 修改更新时间
UPDATE_CONFIG = {
    'update_times': ['08:00', '12:00', '18:00'],
    'update_interval': 3600
}

# 调整显示样式
FONT_CONFIG = {
    'font_size_word': 20,
    'font_size_definition': 12
}

# 重启服务使配置生效
./manage.sh restart
```

### 🔍 监控和维护

```bash
# 运行系统诊断
python3 scripts/diagnose.py

# 查看性能监控
python3 scripts/dashboard.py

# 执行系统备份
./scripts/backup.sh

# 自动修复问题
python3 scripts/auto_fix.py
```

## 🆘 获取帮助

### 📚 文档资源

1. **安装问题** → [故障排除文档](installation-guide/07-troubleshooting.md)
2. **使用问题** → [用户指南](user-manual/user-guide.md)
3. **开发问题** → [API文档](api-reference/api-documentation.md)

### 🔧 诊断工具

```bash
# 快速诊断
python3 scripts/diagnose.py

# 收集支持信息
./scripts/collect_logs.sh

# 查看详细状态
./manage.sh status
```

### 💬 社区支持

- **GitHub Issues** - 报告问题和功能请求
- **技术论坛** - 社区讨论和经验分享
- **用户群组** - 实时交流和互助

## 🔄 更新和升级

### 📦 系统更新

```bash
# 更新系统软件
./scripts/system_update.sh

# 更新应用程序
./scripts/app_update.sh

# 检查更新
git pull origin main
pip install -r requirements.txt --upgrade
```

### 🆕 版本升级

```bash
# 备份当前系统
./scripts/backup.sh

# 下载新版本
git fetch --tags
git checkout v2.0.0

# 更新依赖
pip install -r requirements.txt

# 重启服务
./manage.sh restart
```

## 🤝 贡献指南

### 🐛 报告问题

1. 使用诊断工具收集信息
2. 在GitHub创建Issue
3. 提供详细的错误描述
4. 附上系统信息和日志

### 💡 功能建议

1. 在GitHub Discussions讨论想法
2. 创建Feature Request Issue
3. 提供详细的需求描述
4. 考虑实现的可行性

### 🔧 代码贡献

1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证，详见[LICENSE](../LICENSE)文件。

## 🙏 致谢

感谢以下项目和社区的支持：

- **Raspberry Pi Foundation** - 提供优秀的硬件平台
- **Waveshare** - 提供墨水屏硬件和驱动
- **Python社区** - 提供丰富的开源库
- **开源贡献者** - 提供代码和文档贡献

---

## 📞 联系方式

- **项目主页**: https://github.com/your-repo/daily-word-epaper
- **文档网站**: https://your-repo.github.io/daily-word-epaper
- **技术支持**: support@your-domain.com

---

**开始您的每日单词学习之旅吧！** 🚀📚✨