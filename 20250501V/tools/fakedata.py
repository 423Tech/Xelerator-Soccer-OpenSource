import math

fullx = 240
fully = 120

p = [0,0]
π = 3.1415926

out = [[],[]]

for i in range(0,360,1):
    out[0].append(i)
    out[1].append((p[0]-fully)*int(math.cos(i*π/180)**-1))

print(out)