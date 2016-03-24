import json


class EventBase(object):

    def __init__(self, e):
        self.ts = e.timestamp

    def to_dict(self):
        raise NotImplementedError


class EventDurationBegin(EventBase):

    def __init__(self, e, name, cat, pid, tid, **args):
        super().__init__(e)
        self.ph = 'B'
        self.name = name
        self.cat = cat
        self.pid = pid
        self.tid = tid
        self.args = dict(args)

    def to_dict(self):
        d = {
            'name': self.name,
            'cat': self.cat,
            'ph': self.ph,
            'ts': self.ts,
            'pid': self.pid,
            'tid': self.tid,
            'args': self.args
        }
        return d


class EventDurationEnd(EventBase):

    def __init__(self, e, pid, tid, **args):
        super().__init__(e)
        self.ph = 'E'
        self.pid = pid
        self.tid = tid
        self.args = dict(args)

    def to_dict(self):
        d = {
            'ph': self.ph,
            'ts': self.ts,
            'pid': self.pid,
            'tid': self.tid,
            'args': self.args
        }
        return d


class EventMetaBase(EventBase):

    def __init__(self, meta_type, pid, tid, **args):
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


class EventMetaProcess(EventMetaBase):

    def __init__(self, pid, tid, name, label, idx):
        super().__init__('process')
