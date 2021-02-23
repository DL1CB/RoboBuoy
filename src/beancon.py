import requests
url = "https://hook.ubeac.io/FygzItvW"
querystring = {"foo":["chris","bizz"]}
payload = "{\"zoo\": \"gar\"}"
headers = {
    'cookie': "foo=bar; bar=baz",
    'accept': "application/json",
    'content-type': "application/json",
    'x-pretty-print': "2"
    }
response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
print(response.text)