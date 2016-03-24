#!/usr/bin/env python3

import logging
import argparse
# from lttngtrace.trace import *
# from lttngtrace.cpu_view import *
import lttngtrace.converter


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--input', action='store',
                           help='Load a LTTng output converted by babeltrace')
    argParser.add_argument('-o', '--output', action='store',
                           help='Output file name')
    
    args = argParser.parse_args()
    
    conv = lttngtrace.converter.Converter(args.input, args.output)
#     ee = loadLttngFile(args.input, args.output)

    print ("Done")
