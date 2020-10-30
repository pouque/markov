import socket
import random
import pickle
import sys

# Ник, сервер, канал
nickname = "markov"
server = "irc.freenode.net"
channel = "#chlor"

# .pickle-файл с прегенированными цепями
db = 'chlor.pickle'

# Минимальный и максимальный размер (в словах) текста,
# который будет генерировать робот
size = (10, 30)

# Разделитель слов для робота
sep = ' '

class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def raw(self, msg):
        print("+ " + msg)
        self.irc.send("{}\n".format(msg).encode('utf-8'))

    def send(self, chan, msg):
        self.raw("PRIVMSG {} :{}".format(chan, msg))

    def connect(self, server, channel, botnick):
        print("Connecting to: " + server)
        self.irc.connect((server, 6667))

        self.raw("USER {nick} {nick} {nick} :Markov".format(nick=botnick))
        self.raw("NICK {}".format(botnick))
        self.raw("JOIN {}".format(channel))

    def get(self):
        text = self.irc.recv(2040).decode('utf-8')

        if text.find('PING') != -1:                      
            server = text.split()[1]
            self.raw("PONG {}".format(server))

        return text

kv = {}
with open(db, 'rb') as fin:
    kv = pickle.load(fin)

def find_start(answer):
    for word in answer.lower().split():
        if word in kv:
            return word

    return random.choice(list(kv.keys()))

def gen(answer):
    length = random.randint(*size)

    curr = find_start(answer)
    res = curr + sep

    for idx in range(length):
        if curr not in kv: break

        variants = list(kv[curr].keys())
        probs    = list(kv[curr].values())

        (curr,) = random.choices(variants, weights=probs)
        res += curr + sep

    return res

irc = IRC()
irc.connect(server, channel, nickname)

while True:
    text = irc.get().strip()
    if len(text) <= 0: continue

    print(text)

    if "PRIVMSG" in text and channel in text and nickname in text:
        try:
            msg = text.split("PRIVMSG " + channel)[1]
            irc.send(channel, gen(msg))
        except IndexError:
            pass
