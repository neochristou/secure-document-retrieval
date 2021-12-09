import glob

for filename in glob.glob('*.txt'):
    with open(filename, 'r') as f:
        stats = f.read().strip().split(',')[:-1]
        stats = [float(x) for x in stats]
        average = sum(stats) / len(stats)
        print(filename.split('.')[0], average)
