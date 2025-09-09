# 每日单词墨水屏系统部署检查清单

## 部署前检查 (Pre-deployment Checklist)

### 硬件环境
- [ ] 树莓派正常运行，SSH连接正常
- [ ] 墨水屏硬件连接正确 (SPI接口)
- [ ] 确认墨水屏型号 (推荐: Waveshare 3.52英寸)

### 软件环境
- [ ] Python 3.x 已安装
- [ ] Git 已安装
- [ ] 网络连接正常，可访问外部API

### 冲突检查
```bash
# 检查现有墨水屏服务
ps aux | grep -E "(epd|display|epaper)" | grep -v grep

# 检查crontab冲突
crontab -l | grep -E "(epd|display|epaper)"

# 检查systemd服务冲突
systemctl list-units | grep -E "(epd|display|epaper)"
```

---

## 部署过程检查 (Deployment Process)

### 1. 安装脚本执行
- [ ] `chmod +x install_daily_word.sh` 成功
- [ ] `sudo ./install_daily_word.sh` 执行完成
- [ ] 安装过程无致命错误

### 2. 文件结构验证
```bash
# 检查安装目录
ls -la /opt/daily-word-epaper/

# 必需文件检查
[ -f /opt/daily-word-epaper/src/daily_word_main.py ] && echo "✓ 主程序存在"
[ -f /opt/daily-word-epaper/src/daily_word_epaper_controller.py ] && echo "✓ 墨水屏控制器存在"
[ -d /opt/daily-word-epaper/src/waveshare_epd ] && echo "✓ 墨水屏驱动库存在"
[ -f /opt/daily-word-epaper/pic/Font.ttc ] && echo "✓ 字体文件存在"
```

### 3. 服务配置验证
```bash
# 检查systemd服务文件
[ -f /etc/systemd/system/daily-word.service ] && echo "✓ 服务文件存在"

# 检查管理脚本
[ -f /usr/local/bin/daily-word ] && echo "✓ 管理脚本存在"
[ -x /usr/local/bin/daily-word ] && echo "✓ 管理脚本可执行"
```

---

## 部署后验证 (Post-deployment Verification)

### 1. 基础功能测试
```bash
# 系统测试
daily-word test
# 预期: 4/4 测试通过

# 墨水屏显示测试
daily-word update
# 预期: 墨水屏显示内容更新
```

### 2. 服务状态检查
```bash
# 启动服务
daily-word start

# 检查服务状态
daily-word status
# 预期: 服务运行中，显示进程ID和状态信息

# 检查服务日志
daily-word logs
# 预期: 无错误日志，显示正常运行信息
```

### 3. 配置验证
```bash
# 检查更新配置
grep -A 10 "UPDATE_CONFIG" /opt/daily-word-epaper/src/daily_word_config.py
# 预期: mode: 'interval', interval_seconds: 600
```

### 4. 自启动验证
```bash
# 检查服务是否已启用
systemctl is-enabled daily-word
# 预期: enabled

# 模拟重启测试 (可选)
sudo systemctl daemon-reload
daily-word restart
sleep 10
daily-word status
```

---

## 故障排查快速指南

### 墨水屏无显示
1. 检查硬件连接
2. 验证驱动兼容性: `python3 -c "from waveshare_epd import epd3in52; print('OK')"`
3. 检查字体文件: `ls -la /opt/daily-word-epaper/pic/Font.ttc`

### 服务启动失败
1. 查看详细日志: `daily-word logs`
2. 检查Python环境: `/opt/daily-word-epaper/venv/bin/python --version`
3. 验证依赖安装: `/opt/daily-word-epaper/venv/bin/pip list | grep -E "(PIL|requests|RPi)"`

### 权限问题
1. 检查文件权限: `ls -la /opt/daily-word-epaper/`
2. 验证GPIO权限: `groups $USER | grep gpio`
3. 必要时重新运行安装脚本

---

## 性能监控

### 系统资源使用
```bash
# CPU和内存使用
ps aux | grep daily_word | grep -v grep

# 磁盘使用
du -sh /opt/daily-word-epaper/

# 日志大小
ls -lh /opt/daily-word-epaper/logs/
```

### 运行状态监控
```bash
# 检查最后更新时间
daily-word status | grep "最后更新"

# 检查错误计数
daily-word logs | grep -i error | wc -l
```

---

## 维护建议

### 定期检查项目
- [ ] 每周检查服务状态: `daily-word status`
- [ ] 每月检查日志大小: `ls -lh /opt/daily-word-epaper/logs/`
- [ ] 每季度更新系统: `daily-word update`

### 备份重要配置
```bash
# 备份配置文件
cp /opt/daily-word-epaper/src/daily_word_config.py ~/backup/
cp /etc/systemd/system/daily-word.service ~/backup/
```

---

## 部署完成确认

当以下所有项目都通过时，部署即为成功:

- [ ] ✅ 安装脚本执行完成，无致命错误
- [ ] ✅ 系统测试 4/4 通过
- [ ] ✅ 墨水屏能正常显示内容
- [ ] ✅ 服务正常启动并运行
- [ ] ✅ 每10分钟自动更新配置生效
- [ ] ✅ 开机自启动已启用
- [ ] ✅ 冲突的crontab任务已处理
- [ ] ✅ 日志记录正常，无错误信息

**部署完成时间**: ___________  
**部署人员**: ___________  
**验证人员**: ___________  

---

**文档版本**: v1.0  
**创建时间**: 2025年9月5日