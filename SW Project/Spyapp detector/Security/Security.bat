@echo off

cd C:\Security
del /q *.xml *.html *.jpg *.png *.pdf

adb uninstall detect.spy.report > log.txt
adb uninstall detect.spy.app >> log.txt

adb shell rm -r /mnt/sdcard/permission >> log.txt
adb shell rm -r /mnt/sdcard/tmp >> log.txt

cd C:\Security
del /q *.xml *.html *.jpg *.png *.pdf

adb install -r SpyDetect.apk >> log.txt
cls
adb shell am start -n detect.spy.app/.MainActivity >> log.txt

echo �м���...
timeout /t 1 /nobreak
echo.
echo ���� �ۼ���...
timeout /t 1 /nobreak
echo.

:WAIT
timeout /t 1 /nobreak

adb pull /mnt/sdcard/permission  >> log.txt

if exist Report.html (
echo.
echo �Ϸ�!!
echo.
) else (
goto WAIT
echo �ٽ�
)

adb shell rm -r /mnt/sdcard/permission >> log.txt
adb shell rm -r /mnt/sdcard/tmp >> log.txt

adb uninstall detect.spy.app >> log.txt