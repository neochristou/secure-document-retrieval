import csv
import sys

import matplotlib
import matplotlib.pyplot as plt

if __name__ == "__main__":
    datafile = open(sys.argv[1], 'r')
    reader = csv.reader(datafile)
    titles = next(reader)
    data = next(reader)
    #data = [float(x)/1024 for x in data]
    data = [float(x) for x in data]

    xcoords = range(len(titles))
    # xcoords = [2*x for x in xcoords]

    plt.bar(xcoords, data, width=0.5, bottom=1)
    plt.xlabel("Scheme")
    plt.ylabel("End-to-end latency (in seconds)")
    # plt.yscale("log")
    plt.title("End-to-end latency for PIR schemes")

    plt.xticks(xcoords, titles, rotation=45, ha='right')
    # plt.show()
    plt.tight_layout()
    # f, ax = plt.subplots(1)
    # ax.set_ylim(bottom=10000)
    plt.savefig('latency_pir.eps', format='eps')
