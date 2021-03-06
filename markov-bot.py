import random
import pickle
import sys
import irc
import os

# Ник, сервер, канал
nickname = "markov"
server = "irc.freenode.net"
channel = "#chlor"

# Прегенерированные цепи в формате «ключевое слово — имя файла»
files = {
     'порно а в попку лучше': 'a-v-popku-luchshe',
     'порно бисексуалы': 'biseksualy',
     'порно ваши рассказы': 'vashi-rasskazy',
     'порно гетеросексуалы': 'geteroseksualy',
     'порно жено-мужчины': 'zheno-muzhchiny',
     'порно зоофилы': 'zoofily',
     'порно измена': 'izmena',
     'порно классика': 'klassika',
     'порно клизма': 'klizma',
     'порно лесбиянки': 'lesbiyanki',
     'порно миньет': 'minet',
     'порно наблюдатели': 'nablyudateli',
     'порно пи-пи': 'pi-pi',
     'порно по принуждению': 'po-prinuzhdeniyu',
     'порно потеря девственности': 'poterya-devstvennosti',
     'порно поэзия': 'poeziya',
     'порно пушистики': 'pushistiki',
     'порно романтика': 'romantika',
     'порно свингеры': 'svingery',
     'порно служебный роман': 'sluzhebnyj-roman',
     'порно случай': 'sluchaj',
     'порно странности': 'strannosti',
     'порно студенты': 'studenty',
     'порно фантазии': 'fantazii',
     'порно фетиш': 'fetish',
     'порно фрагменты из запредельного': 'fragmenty-iz-zapredelnogo',
     'порно эксклюзив': 'eksklyuziv',
     'порно эротика': 'erotika',
     'порно эротическая сказка': 'eroticheskaya-skazka',
     'порно юмор': 'yumor',
     'default': 'chlor'
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

irc = irc.IRC()
irc.connect(server, channel, nickname)

while True:
    text = irc.get().strip()
    if len(text) <= 0: continue

    print(text)

    if "PRIVMSG" in text and channel in text and nickname in text:
        try:
            msg = text.split("PRIVMSG " + channel)[1]
            irc.send(channel, gen(select_chain(msg), msg))
        except IndexError:
            pass
