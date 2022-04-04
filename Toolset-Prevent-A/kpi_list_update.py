import json
import requests

kpis = []
for ii in range(1, 1721):

    timestamp = "1522751098000"
    resource = "a"
    metric = str(ii)
    value = 0

    kpis.append({
        'timestamp': timestamp,
        'resource': {
            'name': resource,
        },
        'metric': {
            'name': metric,
        },
        'value': value,
    })

data = {"kpis": kpis}
data = json.dumps(data)

url = 'http://localhost:5000/update_kpi'
headers = {"Content-Type": "application/json"}
r = requests.post(url, data=data, headers=headers)
print(r.content)