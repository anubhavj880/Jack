import time, hashlib, requests, base64
from collections import OrderedDict





key = "M7UPSXUFxxnM"
secret = "QGLTLJKX2AWLNHU2OBVGGIGHTOE3363W"
url = "https://www.deribit.com"
session = requests.Session()

def request(action, data):
    response = None

    if action.startswith("/api/v1/private/"):
        if key is None or secret is None:
            raise Exception("Key or secret empty")

        signature = generate_signature(action, data)
        response = session.post(url + action, data=data, headers={'x-deribit-sig': signature}, verify=True)
    else:
        response = session.get(url + action, params=data, verify=True)

    if response.status_code != 200:
        raise Exception("Wrong response code: {0}".format(response.status_code))

    json = response.json()
    print(response.text)

    if json["success"] == False:
        raise Exception("Failed: " + json["message"])

    if "result" in json:
        return json["result"]
    elif "message" in json:
        return json["message"]
    else:
        return "Ok"


def generate_signature(action, data):
    tstamp = int(time.time() * 1000)
    signature_data = {
        '_': tstamp,
        '_ackey': key,
        '_acsec': secret,
        '_action': action
    }
    signature_data.update(data)
    sorted_signature_data = OrderedDict(sorted(signature_data.items(), key=lambda t: t[0]))

    def converter(data):
        key = data[0]
        value = data[1]
        if isinstance(value, list):
            return '='.join([str(key), ''.join(value)])
        else:
            return '='.join([str(key), str(value)])

    items = map(converter, sorted_signature_data.items())

    signature_string = '&'.join(items)

    sha256 = hashlib.sha256()
    sha256.update(signature_string.encode("utf-8"))
    sig = key + "." + str(tstamp) + "."
    sig += base64.b64encode(sha256.digest()).decode("utf-8")
    return sig

def account():
    return request("/api/v1/private/account", {})

print(account())
