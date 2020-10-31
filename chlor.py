import csv

def messages(filename):
    fin = open(filename, 'r', encoding='utf-8')
    fcsv = csv.reader(fin, delimiter=',')

    for row in fcsv:
        id, date, server, channel, nick, host, message_type, message = row
        if not id.isdigit():
            continue

        yield message.strip()

    fin.close()