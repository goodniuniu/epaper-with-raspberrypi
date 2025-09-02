# 贡献指南 / Contributing Guide

感谢您对每日单词墨水屏显示系统的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题 (Bug Reports)

在提交问题前，请：
1. 检查 [Issues](https://github.com/your-repo/daily-word-epaper/issues) 中是否已有相同问题
2. 使用问题模板提供详细信息
3. 包含系统信息、错误日志和复现步骤

### 功能建议 (Feature Requests)

1. 在 [Discussions](https://github.com/your-repo/daily-word-epaper/discussions) 中讨论新功能
2. 说明功能的使用场景和预期效果
3. 考虑向后兼容性和维护成本

### 代码贡献 (Code Contributions)

#### 开发环境设置

```bash
# 1. Fork 并克隆项目
git clone https://github.com/your-username/daily-word-epaper.git
cd daily-word-epaper

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 4. 运行测试
python -m pytest tests/
```

#### 代码规范

- **Python 版本**: 3.9+
- **代码风格**: 遵循 PEP 8
- **文档字符串**: 使用 Google 风格
- **类型提示**: 推荐使用类型注解
- **测试覆盖**: 新功能需要包含测试

#### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(display): add IP address display functionality

- Add IP address retrieval in get_ipaddress.py
- Integrate IP display in footer section
- Add configuration option for IP display toggle

Closes #123
```

#### Pull Request 流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   ```bash
   # 开发代码
   # 运行测试
   python -m pytest tests/
   # 运行代码检查
   flake8 src/
   black src/
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

4. **创建 Pull Request**
   - 使用 PR 模板
   - 详细描述更改内容
   - 关联相关 Issues
   - 确保 CI 检查通过

## 📁 项目结构

```
epaper-with-raspberrypi/
├── src/                    # 源代码
│   ├── api/               # API 客户端
│   ├── display/           # 显示控制
│   ├── config/            # 配置管理
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── docs/                  # 文档
├── scripts/               # 脚本工具
├── data/                  # 数据文件
└── themes/                # 主题文件
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_api.py

# 生成覆盖率报告
python -m pytest --cov=src tests/
```

### 测试类型

- **单元测试**: 测试单个函数/类
- **集成测试**: 测试模块间交互
- **硬件测试**: 需要实际硬件环境

## 📝 文档贡献

### 文档类型

- **用户文档**: 安装、使用指南
- **开发文档**: API 参考、架构说明
- **示例代码**: 使用示例和教程

### 文档规范

- 使用 Markdown 格式
- 包含代码示例
- 提供截图和图表
- 支持多语言（中英文）

## 🔍 代码审查

### 审查要点

- **功能正确性**: 代码是否实现预期功能
- **代码质量**: 可读性、可维护性
- **性能影响**: 是否影响系统性能
- **安全性**: 是否存在安全隐患
- **兼容性**: 是否影响现有功能

### 审查流程

1. 自动化检查（CI/CD）
2. 代码审查（至少一位维护者）
3. 测试验证
4. 文档更新
5. 合并到主分支

## 🏷️ 发布流程

### 版本号规范

使用 [Semantic Versioning](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- `1.0.0` → `1.0.1` (补丁)
- `1.0.0` → `1.1.0` (新功能)
- `1.0.0` → `2.0.0` (破坏性更改)

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 发布 GitHub Release
5. 更新文档

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/your-repo/daily-word-epaper/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-repo/daily-word-epaper/discussions)
- **邮件**: your-email@example.com

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

再次感谢您的贡献！🙏