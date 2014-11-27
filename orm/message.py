__author__ = 'wan'


class Message(object):
    @classmethod
    def find_all_message(cls, db):
        messages = db.find_all()
        data = dict(data=[])
        ret = parser_message(messages)
        data['data'] = ret
        return data

    @classmethod
    def find_message(cls, db, **kwargs):
        messages = db.find(**kwargs)
        data = dict(data=[])
        if messages is None or len(messages):
            return data
        ret = parser_message(messages)
        data['data'] = ret
        return data


def covert_message(obj, message):
    for key, val in message.items():
        setattr(obj, key, val)


def parser_message(messages):
    data = []
    for m in messages:
        obj = Message()
        covert_message(obj, m)
        data.append(obj.__dict__)
    return data
