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

size     = lambda s: len(s.encode('utf-8'))
nonempty = lambda xs: len(xs) > 0

pop  = lambda xs: xs.pop(0)
push = lambda xs, v: xs.insert(0, v)

class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def raw(self, msg):
        print("+ " + msg)
        self.irc.send("{}\n".format(msg).encode('utf-8'))

    def prefix(self, chan):
        return "PRIVMSG {} :".format(chan)

    def split(self, msg, length):
        buff, res, src = "", [], list(msg)

        while nonempty(src):
            while nonempty(src):
                ch = pop(src)
                if size(buff) + size(ch) <= length:
                    buff += ch
                else:
                    push(src, ch)
                    break

            res.append(buff)
            buff = ""

        return res

    def send(self, chan, msg):
        prefix = self.prefix(chan)
        for part in self.split(msg, 512 - len(prefix)):
            self.raw(self.prefix(chan) + part)

    def connect(self, server, channel, botnick):
        print("Connecting to: " + server)
        self.irc.connect((server, 6667))

        self.raw("USER {nick} {nick} {nick} :Markov".format(nick=botnick))
        self.raw("NICK {}".format(botnick))
        self.raw("JOIN {}".format(channel))

    def get(self):
        try:
            text = self.irc.recv(2040).decode('utf-8')

            if text.find('PING') != -1:
                server = text.split()[1]
                self.raw("PONG {}".format(server))

            return text
        except UnicodeDecodeError:
            return ""

kv = {}
with open(db, 'rb') as fin:
    kv = pickle.load(fin)

def find_start(answer):
    words = answer.lower().split()

    for word in words:
        valid = filter(lambda key: word in key, kv.keys())
        valid = list(valid)

        if len(valid) > 0:
            return random.choice(valid)

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