import requests
with requests.Session() as session:
    session.timeout = 10
urls = ['https://api.github.com/users/tiangolo','https://api.github.com/users/encode']
for url in urls:
    response = session.get(url)
    if response.ok:
        print("Success:" + str(response.status_code))
    else:
        print("Failed:" + str(response.status_code))
  