from irc.irc import Irc
from config import PASS, NICKNAME, CHANNEL
import time


message_number = 0
bot = Irc(NICKNAME, PASS, CHANNEL)


while True:
    for event in bot.get_message():
        if event.type == 'PRIVMSG':
            message_number += 1
            print('%s-%s - %s: %s'
                  % (message_number,
                     bot.channel,
                     event.tags['display-name'],
                     event.content))
    time.sleep(0.05)
