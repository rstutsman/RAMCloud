#!/usr/bin/env python

import os
import sys
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser(description=
            'Run clusterperf.py N times, for colocation and no colocation read'
            'throughput tests respectively, from clients fetching 1 objects to'
            'N objects at a time. N equals the number of servers specified.',
            usage='%prog [options]',
            conflict_handler='resolve')
    parser.add_option('--clients', type=int,
            metavar='N', dest='num_clients',
            help='Number of clients to generate read requests.')
    parser.add_option('--servers', type=int,
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

    # Start "no colocation" tests.
    # Create file used to store results of "no colocation" tests.
    results_path = os.path.join(colocation_test_dir, "".join(["no_colocation_clients_",
                                                              str(ops.num_clients),
                                                              "_servers_",
                                                              str(ops.num_servers),
                                                              "_size_",
                                                              str(ops.size)]))
    results = open(results_path, "w")

    # Run clusterperf.py from 1 objects to num_servers objects.
    for i in range(1, ops.num_servers + 1):
        cmd = " ".join([clusterperf_path, "multiRead_noColocation", args, "--numObjects", str(i)])
        print cmd
        fp = os.popen(cmd)
        total = 0
        count = 0
        for line in fp.readlines():
            count = count + 1
            total = total + int(line.split(" ")[2])
        average = total/count
        results.write("".join([str(average), "\n"]))

    results.close()

    # Start "colocation" tests.
    # Create file used to store results of "colocation" tests.
    results_path = os.path.join(colocation_test_dir, "".join(["colocation_clients_",
                                                              str(ops.num_clients),
                                                              "_servers_",
                                                              str(ops.num_servers),
                                                              "_size_",
                                                              str(ops.size)]))
    results = open(results_path, "w")

    # Run clusterperf.py from 1 objects to num_servers objects.
    for i in range(1, ops.num_servers + 1):
        cmd = " ".join([clusterperf_path, "multiRead_Colocation", args, "--numObjects", str(i)])
        print cmd
        fp = os.popen(cmd)
        total = 0
        count = 0
        for line in fp.readlines():
            count = count + 1
            total = total + int(line.split(" ")[2])
        average = total/count
        results.write("".join([str(average), "\n"]))

    results.close()
