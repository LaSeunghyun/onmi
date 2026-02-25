# Vercel 프론트 배포 (Expo 웹) - apps/mobile
# 사용 전: npx vercel login (최초 1회)

$ErrorActionPreference = "Stop"
$mobileRoot = $PSScriptRoot

Set-Location $mobileRoot
Write-Host "Deploying frontend (Expo web) from $mobileRoot ..." -ForegroundColor Cyan
npx vercel --prod --yes
Write-Host "Done. Open the deployment URL in browser." -ForegroundColor Green
