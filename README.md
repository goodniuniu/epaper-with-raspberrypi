# 每日单词墨水屏显示系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

一个基于树莓派和墨水屏的每日英语单词学习系统，每天自动显示新的单词、定义、例句和励志句子。

![系统展示](docs/assets/images/system-demo.jpg)

## ✨ 主要特性

- 📚 **每日单词学习** - 自动获取每日英语单词，包含音标、定义、例句
- 💬 **励志句子显示** - 每日更新励志名言和智慧句子  
- 🖥️ **墨水屏显示** - 支持多种型号墨水屏，低功耗长时间显示
- 🔄 **自动更新** - 可配置的定时更新，支持多种更新策略
- 📱 **智能缓存** - 本地缓存机制，离线时使用备用内容
- 🎨 **主题定制** - 多种预设主题，支持自定义布局和样式
- 🌐 **多API支持** - 支持多个内容源，自动故障转移
- 📊 **学习统计** - 记录学习历史，提供统计分析
- 🔧 **系统监控** - 实时监控系统状态和性能指标

## 🚀 快速开始

### 一键安装（推荐）

```bash
# 下载并运行自动安装脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/daily-word-epaper/main/docs/assets/scripts/install.sh | bash
```

### 手动安装

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/daily-word-epaper.git
cd daily-word-epaper

# 2. 运行安装脚本
chmod +x docs/assets/scripts/install.sh
./docs/assets/scripts/install.sh

# 3. 启动服务
./manage.sh start
./manage.sh enable  # 启用开机自启
```

## 📋 系统要求

### 硬件要求

- **主控**: 树莓派4/5 (推荐4GB+内存)
- **显示**: Waveshare墨水屏 (2.13"/2.9"/4.2"/7.5")
- **存储**: 16GB+ MicroSD卡
- **网络**: WiFi或以太网连接

### 软件要求

- **系统**: Raspberry Pi OS (Bullseye+)
- **Python**: 3.9+
- **接口**: SPI已启用

## 🔌 硬件连接

### 标准接线图 (以2.13英寸为例)

| 墨水屏 | 树莓派GPIO | 物理引脚 |
|--------|------------|----------|
| VCC    | 3.3V       | 1        |
| GND    | GND        | 6        |
| DIN    | GPIO10     | 19       |
| CLK    | GPIO11     | 23       |
| CS     | GPIO8      | 24       |
| DC     | GPIO25     | 22       |
| RST    | GPIO17     | 11       |
| BUSY   | GPIO24     | 18       |

## 🎯 基本使用

### 管理命令

```bash
# 服务管理
./manage.sh start      # 启动服务
./manage.sh stop       # 停止服务
./manage.sh restart    # 重启服务
./manage.sh status     # 查看状态

# 内容管理
./manage.sh update     # 手动更新显示
./manage.sh clear      # 清空显示
./manage.sh test       # 运行测试

# 系统维护
./manage.sh logs       # 查看日志
./manage.sh diagnose   # 系统诊断
./manage.sh backup     # 系统备份
```

### 配置定制

```bash
# 编辑配置文件
nano src/word_config.py

# 修改更新时间
UPDATE_CONFIG = {
    'update_times': ['08:00', '12:00', '18:00'],  # 自定义更新时间
    'update_interval': 3600,                      # 更新间隔(秒)
}

# 调整显示样式
FONT_CONFIG = {
    'font_size_word': 20,       # 单词字体大小
    'font_size_definition': 12, # 定义字体大小
    'line_spacing': 2           # 行间距
}

# 重启服务使配置生效
./manage.sh restart
```

## 📊 系统监控

### 实时状态监控

```bash
# 查看系统状态
./manage.sh status

# 实时监控仪表板
python3 scripts/dashboard.py

# 持续监控模式
python3 scripts/dashboard.py --continuous
```

### 学习统计

```bash
# 查看学习统计
python3 scripts/learning_stats.py

# 管理收藏内容
python3 scripts/favorites.py list      # 查看收藏
python3 scripts/favorites.py word      # 收藏当前单词
python3 scripts/favorites.py sentence  # 收藏当前句子
```

## 🛠️ 高级功能

### 主题定制

```python
# 在 word_config.py 中选择主题
CURRENT_THEME = 'modern'    # 现代主题
# CURRENT_THEME = 'classic' # 经典主题
# CURRENT_THEME = 'minimal' # 极简主题
```

### 多设备同步

```bash
# 启用设备同步
python3 scripts/sync_manager.py upload    # 上传内容
python3 scripts/sync_manager.py download  # 下载内容
```

### 智能更新策略

```bash
# 使用智能更新(替代固定时间)
python3 scripts/smart_update.py
```

## 🔧 故障排除

### 常见问题

1. **墨水屏无显示**
   ```bash
   ./manage.sh clear    # 清空显示
   ./manage.sh test     # 运行测试
   ./manage.sh restart  # 重启服务
   ```

2. **网络连接问题**
   ```bash
   ping 8.8.8.8                    # 测试网络
   curl -I https://api.quotable.io # 测试API
   ```

3. **服务启动失败**
   ```bash
   sudo systemctl status daily-word  # 查看服务状态
   ./manage.sh diagnose             # 运行诊断
   python3 scripts/auto_fix.py      # 自动修复
   ```

### 诊断工具

```bash
# 系统诊断
python3 scripts/diagnose.py

# 自动修复
python3 scripts/auto_fix.py

# 收集支持信息
./scripts/collect_logs.sh
```

## 📚 完整文档

- **[安装指南](docs/installation-guide/)** - 详细的安装部署文档
- **[用户手册](docs/user-manual/)** - 完整的使用指南
- **[API参考](docs/api-reference/)** - 开发者文档
- **[故障排除](docs/installation-guide/07-troubleshooting.md)** - 问题解决方案

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Raspberry Pi Foundation](https://www.raspberrypi.org/) - 优秀的硬件平台
- [Waveshare](https://www.waveshare.com/) - 墨水屏硬件和驱动支持
- [Wordnik API](https://developer.wordnik.com/) - 单词数据源
- [Quotable API](https://github.com/lukePeavey/quotable) - 句子数据源

## 📞 支持

- **文档**: [完整文档](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/daily-word-epaper/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-repo/daily-word-epaper/discussions)

---

**开始您的每日单词学习之旅！** 🚀📚✨

![效果展示](docs/assets/images/display-examples.jpg)