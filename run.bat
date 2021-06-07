@echo off
set "$py=0"
call:construct

for /f "delims=" %%a in ('python #.py ^| findstr "2"') do set "$py=2"
for /f "delims=" %%a in ('python #.py ^| findstr "3"') do set "$py=3"
del #.py
goto:%$py%

echo python is not installed or python's path Path is not in the %%$path%% env. var
exit/b

:2
echo Please install python 3
pause
exit/b

:3
python "%~dp0\autoswitch.py"
pause
exit/b

:construct
echo import sys; print('{0[0]}.{0[1]}'.format(sys.version_info^)^) >#.py