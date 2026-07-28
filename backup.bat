@echo off
for /f "tokens=2 delims==" %%A in ('findstr "BACKUP_DIR" .env') do set BACKUP_DIR=%%A
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -o "%BACKUP_DIR%\backup_%date:~-4%%date:~4,2%%date:~7,2%.json"
echo Backup complete
exit