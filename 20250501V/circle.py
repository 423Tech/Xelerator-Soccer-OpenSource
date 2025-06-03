from level5 import *

while(Cover2Start()):
    AutoFetch(True)
    if Move2Path(0,[[-60,0],[-50,55]]):
        RailGun()
