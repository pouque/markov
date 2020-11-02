import random
import pickle
import sys
import irc

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

irc = irc.IRC()
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