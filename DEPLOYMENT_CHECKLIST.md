# 🚀 树莓派部署检查清单

## 📋 部署前准备

### ✅ 硬件准备
- [ ] 树莓派4/5 (推荐4GB+内存)
- [ ] MicroSD卡 (16GB+，推荐32GB+)
- [ ] Waveshare墨水屏 (2.13"/2.9"/4.2"/7.5")
- [ ] 杜邦线若干 (用于连接墨水屏)
- [ ] 网络连接 (WiFi或以太网)
- [ ] 电源适配器 (官方推荐5V 3A)

### ✅ 系统准备
- [ ] 安装Raspberry Pi OS (Bullseye或更新版本)
- [ ] 启用SSH (如需远程管理)
- [ ] 启用SPI接口 (`sudo raspi-config` → Interface Options → SPI → Enable)
- [ ] 更新系统 (`sudo apt update && sudo apt upgrade -y`)
- [ ] 配置时区 (`sudo timedatectl set-timezone Asia/Shanghai`)

## 🔌 硬件连接检查

### ✅ 墨水屏连接 (以2.13英寸为例)
- [ ] VCC → 3.3V (物理引脚1)
- [ ] GND → GND (物理引脚6)
- [ ] DIN → GPIO10 (物理引脚19)
- [ ] CLK → GPIO11 (物理引脚23)
- [ ] CS → GPIO8 (物理引脚24)
- [ ] DC → GPIO25 (物理引脚22)
- [ ] RST → GPIO17 (物理引脚11)
- [ ] BUSY → GPIO24 (物理引脚18)

### ✅ 连接验证
- [ ] 检查所有连线是否牢固
- [ ] 确认没有短路或接错
- [ ] 墨水屏型号与配置文件匹配

## 💾 软件安装检查

### ✅ 自动安装方式
```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/daily-word-epaper/main/docs/assets/scripts/install.sh | bash
```

### ✅ 手动安装方式
- [ ] 克隆项目: `git clone https://github.com/your-repo/daily-word-epaper.git`
- [ ] 进入目录: `cd daily-word-epaper`
- [ ] 运行安装: `chmod +x docs/assets/scripts/install.sh && ./docs/assets/scripts/install.sh`

### ✅ 安装验证
- [ ] Python虚拟环境创建成功
- [ ] 所有依赖包安装完成
- [ ] 系统服务创建成功
- [ ] 配置文件生成正确

## ⚙️ 配置检查

### ✅ 硬件配置
- [ ] 墨水屏型号设置正确 (`src/word_config.py` → `EPAPER_MODEL`)
- [ ] GPIO引脚配置正确 (`GPIO_CONFIG`)
- [ ] SPI设置正确 (`SPI_CONFIG`)

### ✅ 显示配置
- [ ] 字体大小合适 (`FONT_CONFIG`)
- [ ] 布局样式满意 (`LAYOUT_CONFIG`)
- [ ] 主题选择正确 (`CURRENT_THEME`)

### ✅ 更新配置
- [ ] 更新时间设置合理 (`UPDATE_CONFIG` → `update_times`)
- [ ] 更新间隔适当 (`update_interval`)
- [ ] API配置正确 (`API_CONFIG`)

## 🚀 部署运行检查

### ✅ 服务管理
- [ ] 启动服务: `./manage.sh start`
- [ ] 检查状态: `./manage.sh status`
- [ ] 启用自启: `./manage.sh enable`
- [ ] 测试显示: `./manage.sh test`

### ✅ 功能测试
- [ ] 手动更新: `./manage.sh update`
- [ ] 查看日志: `./manage.sh logs`
- [ ] 清空显示: `./manage.sh clear`
- [ ] 重启服务: `./manage.sh restart`

### ✅ 显示效果
- [ ] 墨水屏正常显示内容
- [ ] 文字清晰可读
- [ ] 布局美观合理
- [ ] 无显示异常或残影

## 🔍 系统验证

### ✅ 网络连接
- [ ] 网络连接正常: `ping 8.8.8.8`
- [ ] API访问正常: `curl -I https://api.quotable.io`
- [ ] DNS解析正常: `nslookup api.quotable.io`

### ✅ 系统资源
- [ ] CPU使用率正常 (< 50%)
- [ ] 内存使用合理 (< 80%)
- [ ] 存储空间充足 (> 2GB可用)
- [ ] 系统温度正常 (< 70°C)

### ✅ 日志检查
- [ ] 应用日志正常: `tail -f data/daily_word.log`
- [ ] 系统日志无错误: `sudo journalctl -u daily-word -f`
- [ ] 定时任务正常: `crontab -l`

## 📊 监控设置

### ✅ 系统监控
- [ ] 启用监控: `python3 scripts/monitor.py --daemon`
- [ ] 配置告警: `python3 scripts/alert.py --setup`
- [ ] 测试仪表板: `python3 scripts/dashboard.py`

### ✅ 定时任务
- [ ] 定时更新任务: `crontab -l | grep daily-word`
- [ ] 系统维护任务: `crontab -l | grep maintenance`
- [ ] 备份任务: `crontab -l | grep backup`

## 🛠️ 故障排除

### ✅ 常见问题检查
- [ ] 运行诊断: `python3 scripts/diagnose.py`
- [ ] 自动修复: `python3 scripts/auto_fix.py`
- [ ] 收集日志: `./scripts/collect_logs.sh`

### ✅ 性能优化
- [ ] 系统优化: `./scripts/optimize.sh`
- [ ] 清理缓存: `./manage.sh cleanup`
- [ ] 更新系统: `./scripts/system_update.sh`

## 📚 文档确认

### ✅ 文档完整性
- [ ] 运行文档验证: `python3 docs/validate_docs.py`
- [ ] 查看安装指南: `docs/installation-guide/`
- [ ] 阅读用户手册: `docs/user-manual/user-guide.md`
- [ ] 了解API文档: `docs/api-reference/api-documentation.md`

## 🎯 最终验证

### ✅ 完整流程测试
1. [ ] 重启树莓派: `sudo reboot`
2. [ ] 等待系统启动完成 (约2分钟)
3. [ ] 检查服务自启: `./manage.sh status`
4. [ ] 验证显示内容: 观察墨水屏显示
5. [ ] 测试手动更新: `./manage.sh update`
6. [ ] 确认日志记录: `./manage.sh logs`

### ✅ 长期运行测试
- [ ] 连续运行24小时无异常
- [ ] 定时更新功能正常
- [ ] 系统资源使用稳定
- [ ] 无内存泄漏或异常重启

## 📝 部署记录

### 部署信息
- **部署日期**: _______________
- **树莓派型号**: _______________
- **系统版本**: _______________
- **墨水屏型号**: _______________
- **项目版本**: _______________

### 配置记录
- **更新时间**: _______________
- **主题选择**: _______________
- **特殊配置**: _______________

### 测试结果
- **功能测试**: ✅ 通过 / ❌ 失败
- **性能测试**: ✅ 通过 / ❌ 失败
- **稳定性测试**: ✅ 通过 / ❌ 失败

### 问题记录
- **遇到问题**: _______________
- **解决方案**: _______________
- **备注说明**: _______________

---

## 🎉 部署完成

恭喜！如果以上所有检查项都已完成，您的每日单词墨水屏显示系统已成功部署！

### 🔗 快速链接
- **管理命令**: `./manage.sh help`
- **系统状态**: `./manage.sh status`
- **查看日志**: `./manage.sh logs`
- **故障诊断**: `python3 scripts/diagnose.py`

### 📞 获取支持
- **文档**: [docs/](docs/)
- **问题反馈**: GitHub Issues
- **社区讨论**: GitHub Discussions

**享受您的每日单词学习之旅！** 🚀📚✨