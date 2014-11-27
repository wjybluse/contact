__author__ = 'wan'


class Message():
    @classmethod
    def find_all_message(cls, db):
        messages = db.find_all()
        return parser_message(messages)

    @classmethod
    def find_message(cls, db, **kwargs):
        messages = db.find(**kwargs)
        if messages is None or len(messages):
            return []
        return parser_message(messages)


def covert_message(obj, message):
    for key, val in message.items():
        setattr(obj, key, val)


def parser_message(messages):
    data = []
    for m in messages:
        obj = Message()
        covert_message(obj, m)
        data.append(obj)
    return data
