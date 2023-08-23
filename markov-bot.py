import random
import pickle
import sys
import irc
import os

# Ник, сервер, порт, канал
nickname = "markov"
server   = "irc.quakenet.org"
port     = 6667
channel  = "#azaza"

# Прегенерированные цепи в формате «ключевое слово — имя файла»
files = {
     'default': 'lor'
}

# Минимальный и максимальный размер (в словах) текста,
# который будет генерировать робот
size = (10, 30)

# Разделитель слов для робота
sep = ' '

def lookup(name, postfix):
    filename = name + postfix

    for root, dirs, files in os.walk("."):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(filename)

chains = {}
for keyword, name in files.items():
    with open(lookup(name, ".pickle"), 'rb') as fin:
        chains[keyword] = pickle.load(fin)

def select_chain(question):
    question = question.lower()
    for keyword, kv in chains.items():
        if keyword in question:
            return kv
    return chains['default']

def words(question):
    return question.lower().split()

def find_start(kv, question):
    for word in words(question):
        valid = filter(lambda key: word in key, kv.keys())
        valid = list(valid)

        if len(valid) > 0:
            return random.choice(valid)

    return random.choice(list(kv.keys()))

def gen(kv, answer):
    length = random.randint(*size)

    curr = find_start(kv, answer)
    res = curr + sep

    for idx in range(length):
        if curr not in kv: break

        variants = list(kv[curr].keys())
        probs    = list(kv[curr].values())

        (curr,) = random.choices(variants, weights=probs)
        res += curr + sep

    return res

irc = irc.IRC(ipv6 = False)
irc.connect(server, channel, nickname, port = port)

detector = "Welcome to the QuakeNet IRC Network"
while True:
    text = irc.get().strip()
    if len(text) <= 0: continue

    print(text)

    if detector in text:
        irc.join(channel)

    if "PRIVMSG" in text and channel in text and nickname in text:
        try:
            msg = text.split("PRIVMSG " + channel)[1]
            irc.send(channel, gen(select_chain(msg), msg))
        except IndexError:
            pass
