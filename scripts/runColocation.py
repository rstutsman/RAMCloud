#!/usr/bin/env python

import os
import sys
from optparse import OptionParser
import time
import glob
import re

def merge_results(outpath, files):
    first = True
    with open(outpath, 'w') as out:
        for f in files:
            with open(f, 'r') as inp:
                lines = inp.readlines()
                lines = [l.strip() for l in lines]
                lines = [l for l in lines if re.match(r'[0-9]+\.[0-9]+ ', l) is None]
                if first:
                    first = False
                else:
                    lines = lines[1:]
                out.write('\n'.join(lines) + '\n')

def main():
    parser = OptionParser(description=
            'Run clusterperf.py N times, for colocation and no colocation read'
            'throughput tests respectively, from clients fetching 1 objects to'
            'N objects at a time. N equals the number of servers specified.',
            usage='%prog [options]',
            conflict_handler='resolve')
    parser.add_option('--clients', type=int, default=40,
            metavar='N', dest='num_clients',
            help='Number of clients to generate read requests.')
    parser.add_option('--servers', type=int, default=10,
            metavar='N', dest='num_servers',
            help='Number of servers.')
    parser.add_option('--size', type=int, default=100,
            metavar='N', dest='size',
            help='Object size in bytes. Optional.')
    (ops, args) = parser.parse_args()

    if ops.num_clients == None or ops.num_servers == None:
        parser.error("must specify the number of clients and servers.")


    # The directory to store test results.
    colocation_test_dir = os.path.join(os.path.dirname(sys.argv[0]),
                                       "colocation_test")

    if not os.path.exists(colocation_test_dir):
        os.makedirs(colocation_test_dir)

    # The path of "clusterperf.py".
    clusterperf_path = os.path.join(os.path.dirname(sys.argv[0]), "clusterperf.py")

    # Because client[0] won't generate requests, so if we want N clients to
    # generate requests, we need to specify N + 1 clients. 
    ops.num_clients += 1

    # Make arguments for clusterperf.py.
    # The number of tables equals the number of servers, because we want to
    # have one table on each server.
    args = " ".join(["--clients", str(ops.num_clients),
                     "--servers", str(ops.num_servers),
                     "--numTables", str(ops.num_servers),
                     "--size", str(ops.size)])

    # Start "colocation" tests.
    # Create file used to store results of "colocation" tests.
    results_path = os.path.join(colocation_test_dir, "".join(["colocation_clients_",
                                                              str(ops.num_clients),
                                                              "_servers_",
                                                              str(ops.num_servers),
                                                              "_size_",
                                                              str(ops.size)]))

    results_files = []
    for ops in range(1, ops.num_servers + 1):
        for span in range(0, ops):
            cmd = " ".join([clusterperf_path,
                            "multiRead_colocation", args,
                            "--numObjects", str(ops),
                            '--spannedOps', str(span)])
            print cmd
            fp = os.popen(cmd)
            fp.readlines()
            result = os.readlink('logs/latest')
            result = glob.glob('logs/%s/client1.*.log' % result)[0]
            print(result)
            results_files.append(result)

    print(results_files)
    merge_results(results_path, results_files)
    print('Wrote results to %s' % results_path)

if __name__ == '__main__':
    main()
