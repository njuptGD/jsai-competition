import json
import random
from ws4py.client.threadedclient import WebSocketClient


class ExampleClient(WebSocketClient):

    def __init__(self, url):
        super().__init__(url)
        self.name = "Agent1"

    def opened(self):
        pass
        # self.send(json.dumps({"name": self.name}))w

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        content = json.loads(str(message))
        print(content)
        if "action_list" in content and content["action_list"]:
            card_type = random.choice(list(content["action_list"].keys()))
            print("Choose type ", card_type)
            rank = random.choice(list(content["action_list"][card_type].keys()))
            action = random.choice(list(content["action_list"][card_type][rank]))
            print("Choose action:", action)
            self.send(json.dumps({"action": action, "type": card_type, "rank": rank}))


if __name__ == '__main__':
    try:
        ws = ExampleClient('ws://127.0.0.1:23456/game/client3')
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
