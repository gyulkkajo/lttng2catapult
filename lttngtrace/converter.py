try:
    import babeltrace
except ImportError as e:
    print('Babeltrace is not found', e)
    exit(1)

import json
from lttngtrace.view import *


class Converter:

    def __init__(self, trace_path, out_file):
        self.col = babeltrace.TraceCollection()
        self.add_trace_path(trace_path)

        self.views = [CPUView(0)]

        self.loopEachView()
        
        json_sum = []
        for i in self.views:
            json_sum += i.dump()

        with open(out_file, 'w') as fp:
            json.dump(json_sum, fp, indent='  ')
            
    def add_trace_path(self, trace_path, fmt='ctf'):
        return self.col.add_traces_recursive(trace_path, fmt)

    def loopEachView(self):

        for i in self.col.events:
            for view in self.views:
                view.add_event(i)
