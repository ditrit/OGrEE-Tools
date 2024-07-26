@echo off

rem Define the directory to zip (replace "mydirectory" with your actual directory)
set "dir_to_zip=skp2ocli"

rem Define the file to include (replace "myfile.txt" with your actual filename)
set "file_to_include=skp2ocli.rb"

rem Get the current directory (where the script is executed)
set "script_dir=%~dp0"

rem Build the zip filename based on directory name and timestamp
set "zip_name=skp2ocli.zip"
if exist "skp2ocli.rbz" (
  del /q "skp2ocli.rbz"
  echo Deleted existing zip file: skp2ocli.rbz
)
PowerShell -ExecutionPolicy Bypass -NoProfile -Command "& { Compress-Archive -Path %dir_to_zip%* -DestinationPath %zip_name%}"echo Created zip file: %zip_name%
rem Rename the temporary zip to the desired name
ren "%zip_name%" "skp2ocli.rbz"

echo renamed zip file: skp2ocli.rbz

pause