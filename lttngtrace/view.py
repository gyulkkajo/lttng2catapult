import logging
import enum
from lttngtrace.catapult import *


class ViewBase(object):
    name = 'ViewBase THIS'

    def __init__(self):
        self.events = []

    def __len__(self):
        return len(self.events)

    def add_event(self, e):
        raise NotImplementedError

    def meta_to_ctp(self):
        raise NotImplementedError

    def to_ctp(self):
        ctp_evnts = []
        for i in self.events:
            ctp_evnts.append(i.to_dict())

        ctp_evnts += self.meta_to_ctp()
        return ctp_evnts


class CPUView(ViewBase):
    CATEGORY_NAME = 'cpuview'

    def __init__(self, idx):
        super().__init__()

        self.table_idx = idx
        self.cpu_ids = set()

    def add_event(self, e):
        ts = e.timestamp / 1000

        if e.name == 'sched_switch':
            self.cpu_ids.add(e['cpu_id'])
            self.events.append(
                EventDurationEnd(
                    self.table_idx,
                    e['cpu_id'],
                    ts,
                    endState=state_nr_to_str(e['prev_state'])))

            if not e['next_comm'].startswith('swapper/'):
                self.events.append(
                    EventDurationBegin(
                        e['next_comm'],
                        CPUView.CATEGORY_NAME,
                        self.table_idx,
                        e['cpu_id'],
                        ts,
                        prio=e['next_prio']))

    def meta_to_ctp(self):
        ctp_evnts = []

        ctp_evnts.append(
            EventMeta('process_name', self.table_idx, None, name='CPU usage').to_dict())
        ctp_evnts.append(
            EventMeta('process_labels', self.table_idx, None, labels='..?').to_dict())
        ctp_evnts.append(
            EventMeta('process_sort_index', self.table_idx, None, sort_index=self.table_idx).to_dict())

        for i in self.cpu_ids:
            ctp_evnts.append(
                EventMeta('thread_name', self.table_idx, i, name='CPU%d' % i).to_dict())
            ctp_evnts.append(
                EventMeta('thread_sort_index', self.table_idx, i, sort_index=i).to_dict())

        return ctp_evnts


class ProcessState(enum.Enum):
    idle = 0
    waiting = 1
    running = 2


class ProcessView(ViewBase):
    CATEGORY_NAME = 'procview'

    class ThreadInfo(object):
        state_logger = logging.getLogger('Thread state')
        state_logger.setLevel(logging.DEBUG)

        def __init__(self, comm=None, tid=None, pid=None):
            self.comm = comm
            self.tid = tid
            self.pid = pid if pid else self.tid
            self.total_running = 0
            self.total_waiting = 0

            self.state = ProcessState.idle
            self.last_wait_ts = 0
            self.last_run_ts = 0

        def set_waiting(self, ts):
            if self.state is not ProcessState.idle:
                self.state_logger.warning(
                    'State transit: Cannot transit to waiting state from %s' % self.state)

            self.last_wait_ts = ts
            self.state = ProcessState.waiting

        def set_running(self, ts):
            if self.state is ProcessState.running:
                self.state_logger.warning('State transit: running -> running')

            if self.state is ProcessState.waiting:
                self.total_waiting += ts - self.last_wait_ts

            self.last_run_ts = ts
            self.state = ProcessState.running

        def set_idle(self, ts):
            if self.state is ProcessState.idle:
                self.state_logger.warning('State transit: idle -> idle')

            self.total_running += ts - self.last_run_ts
            self.last_wait_ts = self.last_run_ts = 0
            self.state = ProcessState.idle

    def __init__(self):
        super().__init__()

        self.thd_map = dict()

    def add_event(self, e):

        ts = e.timestamp / 1000

        if e.name == 'sched_switch':
            prev_tid = e['prev_tid']
            prev_ti = self.get_thread_info(prev_tid)
            if not prev_ti:
                prev_ti = self.new_thread_info(prev_tid, e['prev_comm'])

            self.events.append(
                EventDurationEnd(
                    prev_ti.pid,
                    prev_ti.tid,
                    ts,
                    endState=state_nr_to_str(e['prev_state'])))
            prev_ti.set_idle(ts)

            next_tid = e['next_tid']
            next_ti = self.get_thread_info(next_tid)
            if not next_ti:
                next_ti = self.new_thread_info(next_tid, e['next_comm'])

            if next_ti.state is ProcessState.waiting:
                self.events.append(
                    EventDurationBegin(
                        next_ti.comm,
                        ProcessView.CATEGORY_NAME,
                        next_ti.pid,
                        next_ti.tid,
                        next_ti.last_wait_ts,
                        ts,
                        prio=e['next_prio']))
            elif not e['next_comm'].startswith('swapper/'):
                self.events.append(
                    EventDurationBegin(
                        next_ti.comm,
                        ProcessView.CATEGORY_NAME,
                        next_ti.pid,
                        next_ti.tid,
                        ts,
                        prio=e['next_prio']))
            next_ti.set_running(ts)

        elif e.name == 'sched_wakeup' or e.name == 'sched_wakeup_new':
            tid = e['tid']
            ti = self.get_thread_info(tid)
            if not ti:
                ti = self.new_thread_info(tid, e['comm'])

            ti.set_waiting(ts)

        elif e.name == 'sched_process_fork':
            c_ti = self.new_thread_info(e['child_tid'], e['child_comm'])
            c_ti.pid = e['parent_pid']

        elif e.name == 'sched_process_exec':
            pass
        elif e.name == 'sched_process_wait':
            pass
        elif e.name == 'sched_process_exit':
            pass
        elif e.name == 'sched_process_free':
            pass
        elif e.name == 'sched_migration':
            pass

    def meta_to_ctp(self):
        ctp_evnts = []

        for ti in self.thd_map.values():
            if ti.comm.startswith('swapper/'):
                continue

            if ti.pid == ti.tid:    # Parent process
                ctp_evnts.append(
                    EventMeta('process_name', ti.pid, ti.tid, name=ti.comm).to_dict())
                ctp_evnts.append(
                    EventMeta('process_sort_index', ti.pid, ti.tid, sort_index=ti.pid).to_dict())

            ctp_evnts.append(
                EventMeta('thread_name', ti.pid, ti.tid, name=ti.comm).to_dict())
            ctp_evnts.append(
                EventMeta('thread_sort_index', ti.pid, ti.tid, sort_index=ti.tid).to_dict())

        return ctp_evnts

    def get_thread_info(self, tid):
        return self.thd_map.get(tid)

    def new_thread_info(self, tid, comm):
        self.thd_map[tid] = self.ThreadInfo(comm, tid)

        return self.get_thread_info(tid)


def state_nr_to_str(state_nr):
    '''Helper function for process state
    See <linux source>/include/trace/events/sched.h
    '''

    if state_nr == 0:
        return 'Running'
    elif state_nr == 1:
        return 'Interruptible sleep'
    elif state_nr == 2:
        return 'Uninterruptible sleep'
    elif state_nr == 4:
        return 'Stopped'
    elif state_nr == 16:
        return 'Exit dead'
    elif state_nr == 32:
        return 'Exit zombie'
    elif state_nr == 64:
        return 'Dead'
    elif state_nr == 128:
        return 'Wakekill'
    elif state_nr == 256:
        return 'Waking'
    elif state_nr == 512:
        return 'Parked'
    elif state_nr == 1024:
        return 'Noload'
    else:
        logging.debug('Unknown state(%d)' % (state_nr))
        return 'Unknown'
