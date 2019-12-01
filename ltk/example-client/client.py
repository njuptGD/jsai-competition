from ws4py.client.threadedclient import WebSocketClient
from json import dumps, loads
import multiprocessing
from random import choice


class PrintProcess:

    def __init__(self):
        super().__init__()
        self.ap_map = {
            "play": self.play,
            "trigger": self.trigger,
            "respond": self.respond,
            "judge": self.judge,
            "heal": self.heal,
            "discard": self.discard,
            "damage": self.damage,
            "death": self.death,
            "nearDeath": self.neat_death,
            "get": self.get,
            "set": self.set
        }

    def trigger(self, ap):
        print("[ targetPosition: {} ]".format(ap["targetPosition"]))
        try:
            if ap["targetPosition"][1]:
                print("[ {}号位对{}号位发动{} ]".format(ap["userPosition"], ap["targetPosition"], ap["ability"]))
            else:
                print("[ {}号位发动{} ]".format(ap["userPosition"], ap["ability"]))
        except TypeError:
            print(ap)
            raise IndexError

    def judge(self, ap):
        print("[ {}号位判定卡牌:{},判定结果：{} ]".format(ap["userPosition"], ap["cards"], ap["effective"]))

    def get(self, ap):
        try:
            if ap["targetPosition"][1]:
                print("[ {}号位获得{}号位卡牌{} ]".format(ap["userPosition"], ap["targetPosition"], ap["cards"]))
            else:
                print("[ {}号位获得卡牌{} ]".format(ap["userPosition"], ap["cards"]))
        except TypeError:
            print(ap)
            raise IndexError

    def play(self, ap):
        try:
            if ap["cards"]:
                if ap["targetPosition"][1]:
                    print("[ {}号位对{}号位使用卡牌{} ]".format(ap["userPosition"], ap["targetPosition"], ap["cards"]))
                else:
                    print("[ {}号位使用卡牌{} ]".format(ap["userPosition"], ap["cards"]))
        except TypeError:
            print(ap)
            raise IndexError

    def respond(self, ap):
        print("[ {}号位打出卡牌{} ]".format(ap["userPosition"], ap["cards"]))

    def heal(self, ap):
        print("[ {}号位回复{}点体力 ]".format(ap["userPosition"], ap["num"]))

    def damage(self, ap):
        print("[ {}号位受到{}点伤害 ]".format(ap["userPosition"], ap["num"]))

    def death(self, ap):
        print("[ {}号位阵亡-身份为：{} ]".format(ap["userPosition"], ap["identity"]))

    def neat_death(self, ap):
        print("[ {}号位濒死-需要{}颗桃 ]".format(ap["userPosition"], ap["num"]))

    def set(self, ap):
        print("[ {}号位设置卡牌{} ]".format(ap["userPosition"], ap["cards"]))

    def discard(self, ap):
        print("[ {}号位弃置卡牌{} ]".format(ap["userPosition"], ap["cards"]))

    def run(self, msg):
        if len(msg) < 3:
            print(msg)
            return
        if msg["actionPerformed"] != {"gameStart": True}:
            self.ap_map[msg["actionPerformed"]["type"]](msg["actionPerformed"])
        else:
            print("[ 游戏开始 ]")
        print("[ 结算区-{}-{} ]".format(
            msg["state"]["overView"]["playCardHeap"]["settle"],
            msg["state"]["overView"]["playCardHeap"]["cards"]
        ))

        print("[ 弃牌区-{} ]".format(
            msg["state"]["overView"]["disCardHeap"]
        ))

        print("[ 手牌-{} ]".format(msg["state"]["personalInfo"]["handCards"]))
        print("[ 位置{}-身份{} ]\n".format(
            msg["state"]["personalInfo"]["position"],
            msg["state"]["personalInfo"]["identity"])
        )
        print("[ 公共信息 ]\n")
        for i in range(5):
            print("[ 位置{}-{}-血量{}-身份{} ]".format(
                i + 1,
                msg["state"]["overView"]["eachInfo"][i]["heroName"],
                msg["state"]["overView"]["eachInfo"][i]["currentLife"],
                msg["state"]["overView"]["eachInfo"][i]["identity"]
            ))
        print("\n")
        for i in range(5):
            print("[ {}号-体力值上限{}-存活:{}-武器{}-防具{}-防御马{}-进攻马{}-乐不思蜀{}-闪电{}-攻击距离{}-锦囊距离{}-防御距离{} ]"
                  .format(i + 1,
                          msg["state"]["overView"]["eachInfo"][i]["maxLife"],
                          msg["state"]["overView"]["eachInfo"][i]["alive"],
                          msg["state"]["overView"]["eachInfo"][i]["weapon"],
                          msg["state"]["overView"]["eachInfo"][i]["armor"],
                          msg["state"]["overView"]["eachInfo"][i]["defensiveHorse"],
                          msg["state"]["overView"]["eachInfo"][i]["offensiveHorse"],
                          msg["state"]["overView"]["eachInfo"][i]["contentment"],
                          msg["state"]["overView"]["eachInfo"][i]["lightning"],
                          msg["state"]["overView"]["eachInfo"][i]["strikeDistance"],
                          msg["state"]["overView"]["eachInfo"][i]["activeDistance"],
                          msg["state"]["overView"]["eachInfo"][i]["passiveDistance"]
                          ))
        print("[ ---------------------------------------- ]\n")
        if msg["state"]["gameOver"]:
            print("游戏结束")


class ExampleClient(WebSocketClient):

    def __init__(self, url, pipe):
        super().__init__(url)
        self.in_pipe = pipe
        self.pprint = PrintProcess()
        self.time = 1
        self.name = "智能体"

    def opened(self):
        self.send(dumps({'name': self.name}))

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        content = loads(str(message))
        self.pprint.run(content)
        print(content)
        if len(content) > 2 and content["actionList"]:
            action = choice(content["actionList"])
            print("[ ---------------------------------------- ]")
            print("[ 动作空间-{} ]".format(content["actionList"]))
            print("[ 选择动作-{} ]".format(action))
            print("[ ---------------------------------------- ]\n")
            ws.send(dumps({"action": action}))


if __name__ == '__main__':
    out_pipe, in_pipe = multiprocessing.Pipe(True)
    try:
        ws = ExampleClient('ws://127.0.0.1:9998/game', in_pipe)
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
