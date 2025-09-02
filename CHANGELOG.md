# 更新日志 / Changelog

本文件记录了项目的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [未发布] - Unreleased

### 新增 Added
- IP地址显示功能
- 系统状态监控增强
- 配置文件验证功能

### 更改 Changed
- 优化显示控制器性能
- 改进错误处理机制
- 更新文档结构

### 修复 Fixed
- 修复缓存清理问题
- 解决字体加载异常
- 修正时区显示错误

## [1.0.0] - 2025-01-02

### 新增 Added
- 🎉 首次发布
- 📚 每日英语单词显示功能
- 💬 励志句子显示功能
- 🖥️ 多型号墨水屏支持 (2.13", 2.9", 4.2", 7.5")
- 🔄 自动定时更新机制
- 📱 智能缓存系统
- 🎨 多主题支持 (经典、现代、极简)
- 🌐 多API数据源支持
- 📊 学习统计功能
- 🔧 完整的系统监控
- 📋 详细的安装和使用文档

### API支持 API Support
- Wordnik API (单词数据)
- Dictionary API (备用单词数据)
- Quotable API (励志句子)
- ZenQuotes API (备用句子数据)

### 硬件支持 Hardware Support
- 树莓派 4/5 (推荐4GB+内存)
- Waveshare 墨水屏系列
- SPI 接口通信
- GPIO 控制

### 系统功能 System Features
- 守护进程模式运行
- 定时和间隔更新模式
- 自动故障转移
- 本地缓存机制
- 系统状态监控
- 日志记录和错误追踪

### 管理工具 Management Tools
- 一键安装脚本
- 服务管理脚本 (start/stop/restart/status)
- 系统诊断工具
- 自动修复功能
- 备份和恢复工具

### 文档 Documentation
- 完整的安装指南
- 详细的用户手册
- API参考文档
- 故障排除指南
- 开发者文档

---

## 版本说明 Version Notes

### 版本号格式 Version Format
- **主版本号 (MAJOR)**: 不兼容的API更改
- **次版本号 (MINOR)**: 向后兼容的功能新增
- **修订号 (PATCH)**: 向后兼容的问题修正

### 更改类型 Change Types
- **新增 (Added)**: 新功能
- **更改 (Changed)**: 现有功能的更改
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: 错误修复
- **安全 (Security)**: 安全相关更改

---

## 贡献 Contributing

如果您想为项目做出贡献，请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 许可证 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。