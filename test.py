data = {
	"model": {
		"number" : 1,
		"type": "Off",
	},
	"Tofs": {
		"On": True,
		0: 1,
		1: 2,
		2: 3,
		3: 4,
		"K": 0.67,
		"B": 4,
		},
	"A2AOb": {
		"ActiveRange": 30,
		"IgnoreRange": 30,
		"NumOfDist" : 4,
		"LifeTime" : 3,
	},
	"Border" : {
		"0": [60,95],
		"1": [40,85],
	},
	"Position" : {
		"ErrorRange": 20,
		"Width": 180,
		"Height": 240,
		"Home": [0,-70],
	},
	"Advanced": {
		"Cover2Start": False,
	}
}

for i in data:
	for d in data[i]:
		for c in data[i].keys():
			print(i,c)