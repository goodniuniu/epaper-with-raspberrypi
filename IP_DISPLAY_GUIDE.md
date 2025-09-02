# IP地址显示功能使用指南

## 📋 功能概述

每日单词墨水屏显示系统现已支持在底部显示树莓派的IP地址，方便用户了解设备的网络连接状态。

## 🎯 显示效果

墨水屏底部将显示如下格式：
```
2025-01-02    IP: 192.168.1.100    数据源: API
```

- **左侧**: 当前日期
- **中央**: IP地址（如果启用且获取成功）
- **右侧**: 数据源信息

## ⚙️ 配置说明

### 启用/禁用IP显示

编辑 `src/daily_word_config.py` 文件：

```python
MONITOR_CONFIG = {
    'monitored_metrics': {
        'show_ip_address': True,    # True=显示IP, False=隐藏IP
        # ... 其他配置
    }
}
```

### 配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `show_ip_address` | `True` | 是否在墨水屏上显示IP地址 |

## 🔧 使用方法

### 1. 启用IP显示功能

```bash
# 编辑配置文件
nano src/daily_word_config.py

# 确保 show_ip_address 设置为 True
# 'show_ip_address': True,
```

### 2. 重启服务

```bash
# 重启服务使配置生效
./manage.sh restart
```

### 3. 验证功能

```bash
# 查看系统状态（包含IP地址）
python3 src/daily_word_main.py --status

# 手动更新显示
./manage.sh update

# 运行测试脚本
python3 test_ip_display.py
```

## 📊 状态查询

使用以下命令查看包含IP地址的系统状态：

```bash
python3 src/daily_word_main.py --status
```

输出示例：
```
系统状态:
  名称: Daily Word E-Paper Display
  版本: 1.0.0
  运行状态: 运行中
  IP地址: 192.168.1.100
  CPU温度: 45.2°C
  时间戳: 2025-01-02T16:00:00
  API客户端: 正常
  显示控制器: 正常
```

## 🛠️ 故障排除

### IP地址不显示

1. **检查配置**:
   ```bash
   grep -n "show_ip_address" src/daily_word_config.py
   ```

2. **检查网络连接**:
   ```bash
   ip addr show
   ping 8.8.8.8
   ```

3. **查看日志**:
   ```bash
   ./manage.sh logs
   ```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| IP显示为空 | 网络未连接 | 检查WiFi/以太网连接 |
| 配置不生效 | 服务未重启 | 运行 `./manage.sh restart` |
| 显示位置重叠 | 屏幕尺寸问题 | 检查墨水屏型号配置 |

## 🔍 技术细节

### 实现原理

1. **IP获取**: 使用 `get_ipaddress.py` 中的 `get_ip_address()` 函数
2. **系统集成**: 通过 `word_config_rpi.py` 的 `get_system_info()` 函数集成
3. **显示渲染**: 在 `daily_word_display_controller.py` 的 `_draw_footer()` 方法中渲染
4. **状态查询**: 通过 `daily_word_main.py` 的 `get_system_status()` 方法提供

### 文件修改清单

- ✅ `src/daily_word_config.py` - 添加IP显示配置选项
- ✅ `src/word_config_rpi.py` - 集成IP地址获取到系统信息
- ✅ `src/daily_word_display_controller.py` - 添加IP地址显示逻辑
- ✅ `src/daily_word_main.py` - 更新系统状态包含IP信息

### 容错机制

- 网络断开时不显示IP地址
- 获取失败时记录警告日志但不影响其他功能
- 配置禁用时完全隐藏IP显示

## 📝 自定义选项

### 修改显示位置

编辑 `src/daily_word_display_controller.py` 中的 `_draw_footer()` 方法：

```python
# 当前: 居中显示
center_x = (self.width - ip_width) // 2

# 修改为左对齐
# center_x = left_margin + 100

# 修改为右对齐  
# center_x = self.width - right_margin - ip_width
```

### 修改显示格式

```python
# 当前格式
ip_text = f"IP: {ip_address}"

# 自定义格式
# ip_text = f"网络: {ip_address}"
# ip_text = f"{ip_address}"  # 仅显示IP
```

## 🚀 后续扩展

可以考虑添加的功能：
- 显示WiFi信号强度
- 显示网络连接类型（WiFi/以太网）
- 显示网络速度
- 支持IPv6地址显示

---

**注意**: 此功能需要在树莓派硬件环境中运行才能正常显示IP地址。