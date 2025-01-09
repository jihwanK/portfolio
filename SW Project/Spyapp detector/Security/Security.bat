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

echo 분석중...
timeout /t 1 /nobreak
echo.
echo 보고서 작성중...
timeout /t 1 /nobreak
echo.

:WAIT
timeout /t 1 /nobreak

adb pull /mnt/sdcard/permission  >> log.txt

if exist Report.html (
echo.
echo 완료!!
echo.
) else (
goto WAIT
echo 다시
)

adb shell rm -r /mnt/sdcard/permission >> log.txt
adb shell rm -r /mnt/sdcard/tmp >> log.txt

adb uninstall detect.spy.app >> log.txt