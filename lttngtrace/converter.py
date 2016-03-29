try:
    import babeltrace
except ImportError as e:
    print('Babeltrace is not found', e)
    exit(1)

import json
from lttngtrace.view import *


class Converter:

    def __init__(self, trace_path):
        self.col = babeltrace.TraceCollection()
        self.add_trace_path(trace_path)

        self.views = [CPUView(-1), ProcessView()]

        for i in self.col.events:
            for view in self.views:
                view.add_event(i)

        self.ctp_obj = {
            'traceEvents': [],
            'displayTimeUnit': 'ms',
            'otherData': {
                'version': 'This version'
            }}
        
        ctp_evnts = self.ctp_obj['traceEvents']
        for i in self.views:
            ctp_evnts += i.to_ctp()


    def add_trace_path(self, trace_path, fmt='ctf'):
        return self.col.add_traces_recursive(trace_path, fmt)

    def export(self, ofile):
        logging.info('Export: %s' % ofile)
        with open(ofile, 'w') as fp:
            json.dump(self.ctp_obj, fp, indent='  ')