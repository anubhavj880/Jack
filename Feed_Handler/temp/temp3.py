import websocket
import thread
import time
import json
import random

data = json.dumps(

    {
        "id": random.randint(999, 99999),
        "action": "/api/v1/public/getorderbook",
        "arguments": {

            "instrument": "BTC-29JUN18"
        }

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