@echo off
cd c:\work\ytAlbumSplit
c:\Python26\python.exe ytAlbumSplit.py "%*"
if errorlevel 1 (
	color 0c
	echo ----------------
	echo FAILURE DETECTED
	echo ----------------
	pause
)