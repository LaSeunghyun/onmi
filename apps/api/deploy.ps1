# Vercel 배포 스크립트 (apps/api)
# 사용 전: npx vercel login, Vercel 대시보드에서 DATABASE_URL, JWT_SECRET 설정

$ErrorActionPreference = "Stop"
$apiRoot = $PSScriptRoot

Set-Location $apiRoot
Write-Host "Deploying from $apiRoot ..." -ForegroundColor Cyan
npx vercel --prod
Write-Host "Done. Check the deployment URL (e.g. /health)." -ForegroundColor Green
