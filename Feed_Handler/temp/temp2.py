import websocket
import thread
import time
import json
import base64
import hashlib
from collections import OrderedDict
import random

#hearbeat  = json.dumps({"action": "/api/v1/public/ping"})
key = "M7UPSXUFxxnM"
secreat = "QGLTLJKX2AWLNHU2OBVGGIGHTOE3363W"

def generate_signature(action, data):
    tstamp = int(time.time() * 1000)
    signature_data = {
        '_': tstamp,
        '_ackey': key,
        '_acsec': secreat,
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



data = json.dumps(

    {
        "id": random.randint(999, 99999),
        "action": "/api/v1/private/account",
        "arguments": {},
        "sig": generate_signature("/api/v1/private/account", {})

    }

)

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print "### open ###"
    def run(*args):
        while True:
            time.sleep(1)
            ws.send(data)
        time.sleep(1)
        ws.close()
    thread.start_new_thread(run, ())




if __name__ == "__main__":
    websocket.enableTrace(False)

    ws = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open=on_open)


    ws.run_forever()

