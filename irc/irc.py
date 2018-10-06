import socket
import time
import threading
import datetime
from irc.event import Message


class Irc:
    def __init__(self, nickname, oauth_key, channel, host='irc.chat.twitch.tv', port=6667):
        self.socket = None
        self.buffer = b''
        self.messages = []
        self.host = host
        self.oauth_key = oauth_key
        self.port = port
        self.nickname = nickname
        self.channel = channel.lower()
        self.last_ping = 300
        self.message = []
        self.started = False

        thread = threading.Thread(target=self.main_thread, args=())
        thread.daemon = True
        thread.start()

        ping_thread = threading.Thread(target=self.ping_thread, args=())
        ping_thread.daemon = True
        ping_thread.start()

        print("Bot in %s starting. 3.." % self.channel, end='')
        time.sleep(1)
        print('2..', end='')
        time.sleep(1)
        print('1..')
        time.sleep(1)
        print('Bot started')

    def open_socket(self, nickname, oauth_key, channel, host='irc.chat.twitch.tv', port=6667):
        self.started = False
        s = socket.socket()
        s.connect((host, port))
        s.send(("PASS " + oauth_key + "\r\n").encode("utf-8"))
        s.send(("NICK " + nickname + "\r\n").encode("utf-8"))
        s.send(("JOIN #" + channel + "\r\n").encode("utf-8"))
        s.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
        self.last_ping = 300
        return s

    def init_room(self):
        loading = True
        while loading:
            self.buffer = self.buffer + self.socket.recv(1024)
            temp = self.buffer.split(b'\r\n')
            self.buffer = temp.pop()
            for line in temp:
                loading = self.loading_complete(str(line))
                if not loading:
                    break

    def loading_complete(self, packet):
        if 'End of /NAMES list' in packet:
            self.started = True
            return False
        else:
            return True

    def send_message(self, message):
        message_temp = 'PRIVMSG #' + self.channel + ' :' + message
        self.socket.send((message_temp + "\r\n").encode("utf-8"))
        print("sent: %s" % message_temp)

    def receive_data(self):
        self.buffer = self.buffer + self.socket.recv(1024)
        temp = self.buffer.split(b'\r\n')
        self.buffer = temp.pop()
        for message in temp:
            if message.decode('UTF-8') == 'PING :tmi.twitch.tv':
                self.socket.send('PONG :tmi.twitch.tv\r\n'.encode("UTF-8"))
                print(str(datetime.datetime.now()) + ': PING received. Pong sent.')
                self.last_ping = 300
            elif self.started:
                self.messages.append(Message(message.decode('UTF-8'), self.channel))

    def switch_channel(self, channel):
        self.socket.send(("PART #" + self.channel + "\r\n").encode("utf-8"))
        self.socket.send(("JOIN #" + channel + "\r\n").encode("utf-8"))
        self.channel = channel

    def get_message(self):
        messages = self.messages
        self.messages = []
        return messages

    def connect_bot(self):
        while True:
                try:
                    self.socket = self.open_socket(self.nickname, self.oauth_key, self.channel, self.host, self.port)
                    self.socket.settimeout(300)
                    self.init_room()
                    return
                except (socket.timeout, socket.gaierror):
                    print('Could not reconnect.. Retrying in 5 seconds..')
                    time.sleep(4)

    def main_thread(self):
        self.connect_bot()
        while True:
            time.sleep(0.05)
            try:
                self.receive_data()
            except:
                self.connect_bot()



    def ping_thread(self):
        while True:
            self.last_ping = 300
            while self.last_ping >= 0:
                time.sleep(1)
                if self.last_ping <= 0:
                    print('Did not received ping since a long time .. ? ')
                    self.socket = None
                self.last_ping -= 1
