import socket

size     = lambda s: len(s.encode('utf-8'))
nonempty = lambda xs: len(xs) > 0

pop  = lambda xs: xs.pop(0)
push = lambda xs, v: xs.insert(0, v)

class IRC:
    irc = socket.socket()
  
    def __init__(self, ipv6 = False):
        self.family = socket.AF_INET6 if ipv6 else socket.AF_INET
        self.irc    = socket.socket(self.family, socket.SOCK_STREAM)
        self.alive  = False

    def raw(self, msg):
        print("+ " + msg)
        self.irc.send("{}\n".format(msg).encode('utf-8'))

    def join(self, channel):
        self.raw("JOIN {}".format(channel))

    def prefix(self, chan):
        return "PRIVMSG {} :".format(chan)

    def split(self, msg, length):
        buff, res, src = "", [], list(msg)

        while nonempty(src):
            while nonempty(src):
                ch = pop(src)
                if size(buff) + size(ch) < length:
                    buff += ch
                else:
                    push(src, ch)
                    break

            res.append(buff)
            buff = ""

        return res

    def send(self, chan, msg):
        prefix = self.prefix(chan)
        for part in self.split(msg, 510 - len(prefix)):
            self.raw(self.prefix(chan) + part)

    def connect(self, server, channel, botnick, port = 6667):
        addrs = socket.getaddrinfo(server, port, self.family, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
        for _, _, _, _, addr in addrs:
            print("Connecting to: " + str(addr))

            try:
                self.irc.connect(addr)
                self.alive = True
                break
            except socket.error as err:
                print(f"FAIL: {err}")
                continue

        if not self.alive:
            print("Unable to connect.")
            return False

        else:
            self.raw("USER {nick} {nick} {nick} :Markov".format(nick=botnick))
            self.raw("NICK {}".format(botnick))

            return True

    def get(self):
        try:
            text = self.irc.recv(2040).decode('utf-8')

            if text.find('PING') != -1:
                server = text.split()[1]
                self.raw("PONG {}".format(server))

            return text
        except UnicodeDecodeError:
            return ""
