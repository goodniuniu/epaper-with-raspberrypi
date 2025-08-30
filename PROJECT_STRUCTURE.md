# 项目结构说明

## 📁 完整目录结构

```
daily-word-epaper/
├── README.md                           # 项目主页说明
├── PROJECT_STRUCTURE.md               # 项目结构说明（本文件）
├── LICENSE                            # 开源许可证
├── requirements.txt                   # Python依赖包列表
├── manage.sh                         # 系统管理脚本
│
├── src/                              # 源代码目录
│   ├── daily_word_rpi.py            # 主程序入口
│   ├── class_word_api.py            # 单词API客户端
│   ├── epaper_display_rpi.py        # 墨水屏显示控制器
│   ├── word_config.py               # 系统配置文件
│   └── __init__.py                  # Python包初始化
│
├── data/                            # 数据存储目录
│   ├── word_cache.json             # 单词缓存文件
│   ├── sentence_cache.json         # 句子缓存文件
│   ├── favorites.json              # 收藏内容
│   ├── daily_word.log              # 应用日志
│   └── metrics.json                # 系统指标数据
│
├── logs/                           # 日志文件目录
│   ├── cron.log                   # 定时任务日志
│   ├── error.log                  # 错误日志
│   ├── backup.log                 # 备份日志
│   └── maintenance.log            # 维护日志
│
├── scripts/                       # 工具脚本目录
│   ├── diagnose.py               # 系统诊断工具
│   ├── dashboard.py              # 监控仪表板
│   ├── auto_fix.py               # 自动修复工具
│   ├── backup.sh                 # 备份脚本
│   ├── restore.sh                # 恢复脚本
│   ├── optimize.sh               # 系统优化脚本
│   ├── monitor.py                # 系统监控脚本
│   ├── learning_stats.py         # 学习统计分析
│   ├── favorites.py              # 收藏管理器
│   ├── sync_manager.py           # 多设备同步
│   ├── smart_update.py           # 智能更新策略
│   ├── alert.py                  # 告警系统
│   └── collect_logs.sh           # 日志收集工具
│
├── themes/                       # 主题目录
│   ├── classic/                  # 经典主题
│   ├── modern/                   # 现代主题
│   ├── minimal/                  # 极简主题
│   └── custom/                   # 自定义主题
│
├── plugins/                      # 插件目录
│   ├── weather_plugin.py         # 天气信息插件
│   └── custom_plugin.py          # 自定义插件示例
│
├── docs/                         # 文档目录
│   ├── README.md                 # 文档总览
│   │
│   ├── installation-guide/       # 安装指南
│   │   ├── README.md             # 安装总览
│   │   ├── 01-system-requirements.md    # 系统要求
│   │   ├── 02-hardware-setup.md         # 硬件设置
│   │   ├── 03-software-installation.md  # 软件安装
│   │   ├── 04-configuration.md          # 系统配置
│   │   ├── 05-deployment.md             # 部署运行
│   │   ├── 06-maintenance.md            # 维护管理
│   │   └── 07-troubleshooting.md        # 故障排除
│   │
│   ├── user-manual/              # 用户手册
│   │   └── user-guide.md         # 用户指南
│   │
│   ├── api-reference/            # API参考
│   │   └── api-documentation.md  # API文档
│   │
│   ├── assets/                   # 文档资源
│   │   ├── images/               # 图片资源
│   │   └── scripts/              # 安装脚本
│   │       ├── install.sh        # 自动安装脚本
│   │       └── manage.sh         # 管理脚本模板
│   │
│   └── docker/                   # Docker相关
│       ├── Dockerfile            # Docker镜像构建文件
│       └── 安装过程.md           # Docker安装说明
│
├── tests/                        # 测试目录
│   ├── test_word_api.py          # API测试
│   ├── test_display.py           # 显示测试
│   └── test_integration.py       # 集成测试
│
└── venv/                         # Python虚拟环境
    ├── bin/                      # 可执行文件
    ├── lib/                      # 库文件
    └── pyvenv.cfg               # 虚拟环境配置
```

## 📋 核心文件说明

### 🔧 主要程序文件

| 文件 | 功能描述 |
|------|----------|
| `src/daily_word_rpi.py` | 主程序入口，处理命令行参数和程序流程 |
| `src/class_word_api.py` | 单词API客户端，负责获取每日单词和句子 |
| `src/epaper_display_rpi.py` | 墨水屏显示控制器，处理内容渲染和显示 |
| `src/word_config.py` | 系统配置文件，包含所有可配置参数 |

### 🛠️ 管理工具

| 文件 | 功能描述 |
|------|----------|
| `manage.sh` | 系统管理脚本，提供启动、停止、监控等功能 |
| `scripts/diagnose.py` | 系统诊断工具，自动检测常见问题 |
| `scripts/dashboard.py` | 监控仪表板，实时显示系统状态 |
| `scripts/auto_fix.py` | 自动修复工具，尝试修复常见问题 |

### 📚 文档文件

| 文件 | 功能描述 |
|------|----------|
| `docs/installation-guide/` | 完整的安装部署指南 |
| `docs/user-manual/` | 用户使用手册 |
| `docs/api-reference/` | 开发者API参考文档 |
| `docs/assets/scripts/install.sh` | 一键安装脚本 |

### 📊 数据文件

| 文件 | 功能描述 |
|------|----------|
| `data/word_cache.json` | 单词数据缓存 |
| `data/sentence_cache.json` | 句子数据缓存 |
| `data/favorites.json` | 用户收藏的内容 |
| `data/daily_word.log` | 应用程序日志 |

## 🔄 文件流转关系

### 数据流向

```
外部API → class_word_api.py → 缓存文件 → epaper_display_rpi.py → 墨水屏显示
    ↓
本地备用内容 ← word_config.py
```

### 配置流向

```
word_config.py → 各个模块 → 运行时行为
```

### 日志流向

```
各个模块 → daily_word.log → 日志分析工具
```

## 🎯 开发指南

### 添加新功能

1. **新增API源**: 修改 `src/class_word_api.py`
2. **新增显示主题**: 在 `themes/` 目录创建新主题
3. **新增插件**: 在 `plugins/` 目录创建插件文件
4. **新增工具脚本**: 在 `scripts/` 目录添加工具

### 修改配置

1. **系统配置**: 修改 `src/word_config.py`
2. **服务配置**: 修改 `/etc/systemd/system/daily-word.service`
3. **定时任务**: 使用 `crontab -e` 修改

### 调试和测试

1. **查看日志**: `./manage.sh logs`
2. **运行诊断**: `python3 scripts/diagnose.py`
3. **运行测试**: `./manage.sh test`
4. **手动测试**: `python3 src/daily_word_rpi.py --test`

## 📦 部署结构

### 系统服务

- **服务名称**: `daily-word`
- **服务文件**: `/etc/systemd/system/daily-word.service`
- **工作目录**: `~/daily-word-epaper`
- **用户权限**: 当前用户 + gpio/spi组

### 定时任务

- **更新任务**: 每日8点、12点、18点更新显示
- **维护任务**: 每周日凌晨执行系统维护
- **备份任务**: 每日凌晨3点执行系统备份
- **监控任务**: 每5分钟执行系统监控

### 网络依赖

- **单词API**: Wordnik API / 备用API
- **句子API**: Quotable API / 备用API
- **同步服务**: 可选的多设备同步服务

## 🔒 安全考虑

### 文件权限

- **可执行文件**: 755权限
- **配置文件**: 644权限
- **日志目录**: 766权限
- **数据目录**: 766权限

### 系统安全

- **服务隔离**: systemd安全设置
- **资源限制**: CPU和内存限制
- **网络访问**: 仅必要的外部连接
- **用户权限**: 非root用户运行

## 📈 扩展性

### 水平扩展

- **多设备支持**: 通过同步服务支持多设备
- **负载均衡**: API请求的负载均衡
- **缓存策略**: 多级缓存提升性能

### 垂直扩展

- **插件系统**: 支持功能插件扩展
- **主题系统**: 支持自定义显示主题
- **API适配器**: 支持新的数据源接入

---

**这个项目结构设计确保了代码的可维护性、可扩展性和用户友好性。** 🚀