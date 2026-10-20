@echo off
setlocal
cd /d "%~dp0"
echo === R PATH
if not defined R_HOME (
  echo ERROR: Set R_HOME to the installed R 4.6.0 directory.
  exit /b 1
)
set "PATH=%R_HOME%\bin;%PATH%"
echo === R user libraries
if not defined R_LIBS_USER (
  echo ERROR: Set R_LIBS_USER to existing native R package libraries.
  exit /b 1
)
echo === R dependency libraries
if not defined R_LIBS (
  echo ERROR: Set R_LIBS to existing native R dependency libraries.
  exit /b 1
)
echo === R environment file
set "R_ENVIRON_USER=NUL"
echo === Existing Playwright package
if not defined PLAYWRIGHT_MODULE (
  echo ERROR: Set PLAYWRIGHT_MODULE to an installed Playwright module or package path.
  exit /b 1
)
rem The existing browser wrapper consumes PLAYWRIGHT_PATH.
set "PLAYWRIGHT_PATH=%PLAYWRIGHT_MODULE%"
echo === Verify prepared source and original reference integrity
python -X utf8 analysis/recut_integrity.py
if errorlevel 1 exit /b 1
echo === Node preflight
node --version
if errorlevel 1 exit /b 1
echo === Native R package version preflight
Rscript analysis/recut_preflight.R
if errorlevel 1 exit /b 1
echo === Preserve earlier scratch outputs
python -X utf8 analysis/preserve_rerun.py
if errorlevel 1 exit /b 1
echo === Stage scratch wrappers and immutable input copies
python -X utf8 analysis/run_recut.py stage
if errorlevel 1 exit /b 1
echo === Parse archive browser wrapper
node --check analysis/run_browser.cjs
if errorlevel 1 exit /b 1
echo === Parse copied extras wrapper
node --check rerun/plus/proportion-ma/validate/check-plus.archive.mjs
if errorlevel 1 exit /b 1
echo === Re-run original validation against current app and capture observations
node analysis/run_browser.cjs original
if errorlevel 1 exit /b 1
echo === Compare fresh app observations with original R references
python -X utf8 analysis/run_recut.py compare-original
if errorlevel 1 exit /b 1
echo === Refit original R validation against fresh app observations
python -X utf8 analysis/run_recut.py original-r
if errorlevel 1 exit /b 1
echo === Check native extras pairs and generate exact browser R script
node rerun/plus/proportion-ma/validate/check-plus.archive.mjs --write-r
if errorlevel 1 exit /b 1
echo === Execute generated extras script in native R
python -X utf8 analysis/run_recut.py plus-r
if errorlevel 1 exit /b 1
echo === Compare new native script results with both GLMM references
node rerun/plus/proportion-ma/validate/check-plus.archive.mjs --runtime-log rerun/plus-runtime.log
if errorlevel 1 exit /b 1
echo === Check retained GLMM warnings and diagnostic evidence
node rerun/plus/proportion-ma/validate/check-plus-diagnostics.mjs
if errorlevel 1 exit /b 1
echo === Replay extras presentation and JSON export offline
node analysis/run_browser.cjs extras
if errorlevel 1 exit /b 1
echo === Re-run full live webR GLMM documented-exceptions contract
node analysis/run_browser.cjs live-plus
if errorlevel 1 exit /b 1
echo === Reproduce historical publication outputs
python -X utf8 analysis/make_outputs.py
if errorlevel 1 exit /b 1
echo === Verify no protected source changed during reruns
python -X utf8 analysis/recut_integrity.py
if errorlevel 1 exit /b 1
echo === Regenerate app and source inventories
python -X utf8 analysis/refresh_manifests.py
if errorlevel 1 exit /b 1
echo === Verify regenerated source and reference manifests
python -X utf8 analysis/recut_integrity.py
if errorlevel 1 exit /b 1
echo === Full historical archive metadata table and image verification
python -X utf8 analysis/verify_archive.py
if errorlevel 1 exit /b 1
exit /b 0
