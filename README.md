# MonitorAmbientLight

Install on Windows:
STEP 1:
    In powershell install:
    py -m pip install monitorcontrol mss numpy


STEP 2: 
    (for now deleted and not needed in case your ambient light is fully rgb (not only capable of displaying a single color at the time))
    Calibrate available monitor presets (one time):
        py omen_ambilight.py --calibrate

STEP 2.5:
    Change the value of the variable "theVictim" = FROM > "omen x 25f" TO > "name of your monitor"
    The name of your monitor you can get using the findYourMonitor.py & don't forget to use only lower case letters!

STEP 3:
    Run Ambilight:
        py ambientLight.py



If you have multiple screens, choose the capture display:
    for example: py ambientLight.py --screen 2

Stop with Ctrl+C.  This uses only observed VCP values, not guessed RGB writes.