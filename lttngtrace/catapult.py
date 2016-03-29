class EventBase(object):

    def to_dict(self):
        raise NotImplementedError


class EventDurationBegin(EventBase):

    def __init__(self, name, cat, pid, tid, ts, tts=None, **args):
        super().__init__()

        self.ph = 'B'
        self.name = name
        self.cat = cat
        self.pid = pid
        self.tid = tid
        self.ts = ts
        self.tts = tts if tts else self.ts
        self.args = dict(args)

    def to_dict(self):
        d = {
            'name': self.name,
            'cat': self.cat,
            'ph': self.ph,
            'pid': self.pid,
            'tid': self.tid,
            'ts': self.ts,
            'tts': self.tts,
            'args': self.args
        }
        return d


class EventDurationEnd(EventBase):

    def __init__(self, pid, tid, ts, tts=None, **args):
        super().__init__()

        self.ph = 'E'
        self.pid = pid
        self.tid = tid
        self.ts = ts
        self.tts = tts if tts else self.ts
        self.args = dict(args)

    def to_dict(self):
        d = {
            'ph': self.ph,
            'pid': self.pid,
            'tid': self.tid,
            'ts': self.ts,
            'tts': self.tts,
            'args': self.args
        }
        return d


class EventMeta(EventBase):

    def __init__(self, meta_type, pid, tid, **args):
        super().__init__()

        self.ph = 'M'
        self.meta_type = meta_type
        self.pid = pid
        self.tid = tid
        self.args = dict(args)

    def to_dict(self):
        d = {
            'name': self.meta_type,
            'ph': self.ph,
            'pid': self.pid,
            'tid': self.tid,
            'args': self.args
        }
        return d
