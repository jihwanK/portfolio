@echo off
adb uninstall detect.spy.report >> log.txt
adb uninstall detect.spy.app >> log.txt

adb shell rm -r /mnt/sdcard/permission >> log.txt
adb shell rm -r /mnt/sdcard/tmp >> log.txt

cd C:\Users\ABCD\Desktop\spydetect
del /q *.xml *.html *.jpg *.png *.pdf