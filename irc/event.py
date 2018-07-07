class Message:
    def __init__(self, message, channel):
        self.message_raw = message
        self.channel = '#' + channel
        self.type = self.get_type()
        if self.type in ['PRIVMSG', 'CLEARCHAT', 'USERNOTICE']:
            self.tags = self.parse_tags(self.get_tags())
        else:
            self.tags = {}
        if self.type in [':twitch.tv/']:
            self.parse_cap_ack()
        elif self.type in ['WHISPER']:
            self.channel = channel
        else:
            self.content = self.get_content()

    def get_type(self):
        msg_type = self.message_raw.split(' #')[0].split(' ')[-1]
        return msg_type

    def get_tags(self):
        msg_tags = self.message_raw.split(' ')[0]
        return msg_tags

    def parse_tags(self, tags_raw):
        tags_dict = {}
        tags = tags_raw.split(';')
        for attribute in tags:
            temp = attribute.split('=')
            if temp[0] == '@badges':
                temp[1] = self.parse_badge(temp[1])
            tags_dict[temp[0]] = temp[1]
        return tags_dict

    def get_channel(self):
        channel = self.message_raw.split(self.type + ' ')[1].split(' ')[0]
        return channel

    def get_content(self):
        content = self.message_raw.split(self.channel + ' :')
        if len(content) == 1:
            content = self.message_raw.split(self.channel + ' ')
            if len(content) == 1:
                return None
        del content[0]
        content = (self.channel + ' ').join(content)
        return content

    def parse_badge(self, badge_raw):
        badge_dict = {}
        if len(badge_raw) > 0:
            badges = badge_raw.split(',')
            for values in badges:
                temp = values.split('/')
                badge_dict[temp[0]] = temp[1]
        return badge_dict

    def parse_cap_ack(self):
        self.type = 'CAP * ACK'
        self.tags = None
        self.content = self.message_raw.split(' ')[-1]
