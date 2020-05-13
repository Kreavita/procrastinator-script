@echo off
setlocal EnableDelayedExpansion

title JumpcutterContainer

set "fps=60"
:restart
set "ipath=0"
set "opath=0"

SET /P "ipath=Please paste the input file path:"
SET /P "opath=Please paste the output file path:"
SET /P "fps=Please enter the Frame Rate of the Video (Default is 60):"

IF /i %ipath%==0 goto Error
IF /i %opath%==0 goto Error

set "startTime=%time: =0%"

cd modules/util/
del /q TEMP
rmdir TEMP

move %ipath% i.mp4

py jumpcutter.py --input_file i.mp4 --output_file o.mp4 --silent_speed 999999 --sounded_speed 1 --frame_rate %fps% --frame_quality 1 --frame_margin 2

move o.mp4 %opath%
move i.mp4 %ipath% 
set "endTime=%time: =0%"

rem Get elapsed time:
set "end=!endTime:%time:~8,1%=%%100)*100+1!"  &  set "start=!startTime:%time:~8,1%=%%100)*100+1!"
set /A "elap=((((10!end:%time:~2,1%=%%100)*60+1!%%100)-((((10!start:%time:~2,1%=%%100)*60+1!%%100)"

rem Convert elapsed time to HH:MM:SS:CC format:
set /A "cc=elap%%100+100,elap/=100,ss=elap%%60+100,elap/=60,mm=elap%%60+100,hh=elap/60+100"

echo ------------------------------------------------
echo Start:    %startTime%
echo End:      %endTime%
echo Elapsed:  %hh:~1%%time:~2,1%%mm:~1%%time:~2,1%%ss:~1%%time:~8,1%%cc:~1%
echo ------------------------------------------------

%opath%
goto End
:Error
echo You did not enter any path, please try again
goto restart
:End
pause