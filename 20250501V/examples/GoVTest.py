from Level5 import GoV
import key

while(key.read() == 0):
    pass

while True:
    for i in range(-90, 90):
        GoV(0,i,100)