import requests
import json

resp = requests.get("https://etherchain.org/api/statistics/price")
robj = json.loads(resp.text)

nrOfDays = 200
shortDays = 50
data = robj["data"][-nrOfDays*24:] #Get the last nrOfDays elements in list

nrOfElements = len(data)

longEma=[]
shortEma=[]

for i in range(nrOfElements):
	element = data[i]
	#print("Time:",element["time"],"Price:",element["usd"])
	longEma.append(element["usd"])
	if(i>=1200):
		shortEma.append(element["usd"])


print(longEma)

#twoh_ema = clac_ema(200)
#fifty_ema = calc_ema(50)

