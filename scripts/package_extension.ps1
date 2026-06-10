# Chrome 扩展打包脚本
# 将扩展打包成 .zip 文件

$ErrorActionPreference = "Stop"

# 获取项目根目录
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ExtensionDir = Join-Path $ProjectRoot "extension"
$DistDir = Join-Path $ProjectRoot "dist"

# 创建输出目录
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

# 读取 manifest.json
$ManifestPath = Join-Path $ExtensionDir "manifest.json"
$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

$Name = $Manifest.name
$Version = $Manifest.version

# 清理文件名
$SafeName = $Name -replace '[^a-zA-Z0-9\-_]', ''
$ZipName = "${SafeName}_${Version}.zip"
$ZipPath = Join-Path $DistDir $ZipName

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Chrome 扩展打包工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "扩展名称: $Name" -ForegroundColor Yellow
Write-Host "版本号: $Version" -ForegroundColor Yellow
Write-Host ""

# 删除旧的 ZIP 文件
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
    Write-Host "已删除旧的 ZIP 文件" -ForegroundColor Gray
}

# 创建 ZIP 文件
Write-Host "正在创建 ZIP 文件..." -ForegroundColor Green

# 使用 .NET 的 ZipFile 类
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($ExtensionDir, $ZipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "打包完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "ZIP 文件: $ZipPath" -ForegroundColor Yellow
Write-Host "文件大小: $([math]::Round((Get-Item $ZipPath).Length / 1024, 2)) KB" -ForegroundColor Yellow
Write-Host ""
Write-Host "安装方法:" -ForegroundColor Cyan
Write-Host "1. 打开 chrome://extensions/" -ForegroundColor White
Write-Host "2. 开启右上角的开发者模式" -ForegroundColor White
Write-Host "3. 将 ZIP 文件拖拽到页面中" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
