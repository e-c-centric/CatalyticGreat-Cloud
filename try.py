import requests,json
url = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
post_fields = {'format': 'json', 'data':'2T1BURHE8FC468221'}
r = requests.post(url, data=post_fields)

varX = r.text

info = json.loads(varX)
print(info['Results'][0]["ModelYear"])