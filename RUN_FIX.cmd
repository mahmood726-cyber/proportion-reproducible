@echo off
setlocal
cd /d "%~dp0"
rem Host follow-up: supply R_HOME, R_LIBS_USER, R_LIBS and PLAYWRIGHT_MODULE
rem as documented in RUN_PLAN_EXPECTED.md. The original host run already passed.
echo === Review working-tree status - Git unavailable in fix sandbox
git status --short
if errorlevel 1 exit /b 1
echo === Review whitespace - Git unavailable in fix sandbox
git diff --check
if errorlevel 1 exit /b 1
echo === Check browser wrapper syntax - Node unavailable in fix sandbox
node --check analysis/run_browser.cjs
if errorlevel 1 exit /b 1
echo === Run portable Node R browser and full Python verification on host
call RUN_PLAN.cmd
if errorlevel 1 exit /b 1
exit /b 0
