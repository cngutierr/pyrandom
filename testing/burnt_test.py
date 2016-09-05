import argparse
import sys
import randtest
import time
from multiprocessing import Pool
import glob
import sqlite3 as lite


DB_LOCATION = "results.db"
#FILENAME, TYPE,
INSERT_PRELIM = "INSERT OR REPLACE into Prelim VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
CREATE_TABLE_SQL = """CREATE TABLE if NOT EXISTS Prelim (filename TEXT, monobit REAL, blockfreq REAL, runs REAL,
                      longestrun REAL, binarymatrank REAL, spectral REAL, notm  REAL, otm REAL, maurer  REAL, cumsum REAL,
                      cumsumrev REAL)"""
tests = {1: 'monobitfrequencytest',
         2: 'blockfrequencytest',
         3: 'runstest',
         4: 'longestrunones8',
         5: 'binarymatrixranktest',
         6: 'spectraltest',
         7: 'nonoverlappingtemplatematchingtest',
         8: 'overlappingtemplatematchingtest',
         9: 'maurersuniversalstatistictest',
         10: 'cumultativesumstest',
         11: 'cumultativesumstestreverse',
         12: 'lempelzivcompressiontest',
         13: 'randomexcursionstest',
         14: 'randomexcursionsvarianttest',
         15: 'linearcomplexitytest',
         16: 'serialtest',
         17: 'aproximateentropytest',
      }

def proc_randtest(filename):
    bytes_str = file_to_bstr(filename)
    return performrndtest(filename, bytes_str, range(1, 12))

def file_to_bstr(filename):
    randin=""
    with open(filename, "r") as f:
        bytes_read = f.read()
        for b in bytes_read:
            n = ord(b)
            bstr = ""
            for x in xrange(8):
                bstr=str(n%2) + bstr
                n = n >> 1
            randin += bstr
    return randin


def performrndtest(filename, inputbits, testlist):
    out_vals = list()
    out_vals.append(filename)
    for i in testlist:
        out_vals.append(round(eval("randtest." + tests[i])(inputbits), 4))
    return out_vals


def write_results(results):
    with lite.connect(DB_LOCATION) as conn:
        cur = conn.cursor()
        cur.execute(INSERT_PRELIM, tuple(results))
    print "Wrote results for %s" % results[0]

def run_small_randtest_async(samples_dir="samples/*"):
    # get all the file names in samples_dir
    files = glob.glob(samples_dir)
    print files
    pool = Pool()
    for filename in files:
        pool.apply_async(proc_randtest, args=(filename,), callback=write_results)
    pool.close()
    pool.join()

if __name__ == '__main__':
    #create table if it does not exist
    with lite.connect(DB_LOCATION) as conn:
        conn.execute(CREATE_TABLE_SQL)

    #init stuff here
    start_time = time.time()
    #run main test func here
    run_small_randtest_async()

    end_time = time.time() - start_time
    print "Finished %s in %i ms" % ("rand test", (int(end_time * 1000)))