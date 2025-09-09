# 每日单词墨水屏系统 - Windows 快速启动脚本
# Daily Word E-Paper System - Windows Quick Start Script

param(
    [string]$Action = "setup"
)

Write-Host "=== 每日单词墨水屏系统 - Windows 快速启动 ===" -ForegroundColor Green
Write-Host ""

function Test-PythonVersion {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 9) {
                Write-Host "[OK] Python版本: $pythonVersion" -ForegroundColor Green
                return $true
            } else {
                Write-Host "[ERROR] Python版本过低: $pythonVersion (需要3.9+)" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "[ERROR] 未找到Python，请先安装Python 3.9+" -ForegroundColor Red
        return $false
    }
}

function Setup-Environment {
    Write-Host "1. 检查Python环境..." -ForegroundColor Yellow
    if (-not (Test-PythonVersion)) {
        Write-Host "请从 https://www.python.org/downloads/ 下载并安装Python 3.9+" -ForegroundColor Red
        exit 1
    }

    Write-Host "2. 创建虚拟环境..." -ForegroundColor Yellow
    if (Test-Path "venv") {
        Write-Host "[INFO] 虚拟环境已存在，跳过创建" -ForegroundColor Blue
    } else {
        python -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] 虚拟环境创建成功" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] 虚拟环境创建失败" -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "3. 激活虚拟环境..." -ForegroundColor Yellow
    try {
        & ".\venv\Scripts\Activate.ps1"
        Write-Host "[OK] 虚拟环境已激活" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] 虚拟环境激活失败，尝试设置执行策略..." -ForegroundColor Yellow
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        & ".\venv\Scripts\Activate.ps1"
    }

    Write-Host "4. 安装依赖包..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] 依赖包安装成功" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] 依赖包安装失败" -ForegroundColor Red
        exit 1
    }

    Write-Host "5. 检查配置文件..." -ForegroundColor Yellow
    if (-not (Test-Path "config.ini")) {
        Write-Host "[INFO] 创建默认配置文件..." -ForegroundColor Blue
        Copy-Item "config.ini" "config.ini.backup" -ErrorAction SilentlyContinue
    }

    Write-Host ""
    Write-Host "✅ 环境设置完成！" -ForegroundColor Green
    Write-Host ""
}

function Run-Tests {
    Write-Host "运行系统测试..." -ForegroundColor Yellow
    
    Write-Host "1. 测试模块导入..." -ForegroundColor Blue
    python src/daily_word_test_simple.py
    
    Write-Host "2. 测试API连接..." -ForegroundColor Blue
    python src/test_word_api.py
    
    Write-Host "3. 验证项目完整性..." -ForegroundColor Blue
    python validate_project.py
    
    Write-Host ""
    Write-Host "✅ 测试完成！" -ForegroundColor Green
}

function Show-Status {
    Write-Host "系统状态检查..." -ForegroundColor Yellow
    
    Write-Host "Python环境:" -ForegroundColor Blue
    python --version
    
    Write-Host "虚拟环境:" -ForegroundColor Blue
    if (Test-Path "venv") {
        Write-Host "[OK] 虚拟环境存在" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] 虚拟环境不存在" -ForegroundColor Yellow
    }
    
    Write-Host "依赖包:" -ForegroundColor Blue
    pip list | Select-String -Pattern "pillow|requests|gpiozero"
    
    Write-Host "项目文件:" -ForegroundColor Blue
    $pyFiles = (Get-ChildItem src/*.py).Count
    Write-Host "Python文件数: $pyFiles" -ForegroundColor Green
    
    Write-Host "配置文件:" -ForegroundColor Blue
    if (Test-Path "config.ini") {
        Write-Host "[OK] config.ini 存在" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] config.ini 不存在" -ForegroundColor Yellow
    }
}

function Show-Help {
    Write-Host "使用方法:" -ForegroundColor Yellow
    Write-Host "  .\quick_start.ps1 setup    - 设置开发环境" -ForegroundColor White
    Write-Host "  .\quick_start.ps1 test     - 运行测试" -ForegroundColor White
    Write-Host "  .\quick_start.ps1 status   - 查看状态" -ForegroundColor White
    Write-Host "  .\quick_start.ps1 help     - 显示帮助" -ForegroundColor White
    Write-Host ""
    Write-Host "开发命令:" -ForegroundColor Yellow
    Write-Host "  python src/daily_word_test_simple.py  - 简单测试" -ForegroundColor White
    Write-Host "  python src/test_word_api.py           - API测试" -ForegroundColor White
    Write-Host "  python validate_project.py            - 项目验证" -ForegroundColor White
    Write-Host ""
    Write-Host "更多信息请查看 WINDOWS_SETUP_GUIDE.md" -ForegroundColor Blue
}

# 主逻辑
switch ($Action.ToLower()) {
    "setup" {
        Setup-Environment
    }
    "test" {
        Run-Tests
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "未知操作: $Action" -ForegroundColor Red
        Show-Help
    }
}

Write-Host ""
Write-Host "🚀 每日单词墨水屏系统已准备就绪！" -ForegroundColor Green
Write-Host "📚 查看 WINDOWS_SETUP_GUIDE.md 获取详细使用说明" -ForegroundColor Blue