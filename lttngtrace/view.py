from lttngtrace.catapult import *


class ViewBase(object):
    name = 'ViewBase THIS'

    def __init__(self):
        self.events = []

    def __len__(self):
        return len(self.events)

    def add_event(self, e):
        raise NotImplementedError

    def dump(self):
        ctp_evnts = []
        for i in self.events:
            ctp_evnts.append(i.to_dict())

        return ctp_evnts


class CPUView(ViewBase):

    def __init__(self, idx):
        super().__init__()

        self.table_idx = idx
        self.cpu_ids = set()
        
    def add_event(self, e):
        if e.name == 'sched_switch':
            self.cpu_ids.add(e['cpu_id'])
            self.events.append(EventDurationEnd(e, self.table_idx, e['cpu_id']))

            if not e['next_comm'].startswith('swapper/'):
                self.events.append(EventDurationBegin(
                    e, e['next_comm'], 'cpuview', self.table_idx, e['cpu_id']))
        elif e.name == 'sched_migration':
            pass

    def dump(self):
        ctp_evnts = super().dump()
        
        ctp_evnts.append(EventMetaBase('process_name', self.table_idx, None, name='CPU usage').to_dict())
        ctp_evnts.append(EventMetaBase('process_labels', self.table_idx, None, labels='..?').to_dict())
        for i in self.cpu_ids:
            ctp_evnts.append(EventMetaBase('thread_name', self.table_idx, i, name='CPU%d'%i).to_dict())
            ctp_evnts.append(EventMetaBase('thread_sort_index', self.table_idx, i, sort_index=i).to_dict())
        
        return ctp_evnts