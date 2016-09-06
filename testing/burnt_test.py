import sys
import randtest
import time
from multiprocessing import Pool
import glob
import sqlite3 as lite


DB_LOCATION = "results.db"
#FILENAME, TYPE,
INSERT_PRELIM = """INSERT OR REPLACE into Prelim VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                                                         ?, ?, ?, ?, ?, ?, ?, ?,
                                                         ?, ?, ?, ?, ?, ?, ?, ?,
                                                         ?, ?, ?, ?, ?, ?, ?, ?,
                                                         ?, ?, ?, ?, ?, ?, ?, ?,
                                                         ?, ?)"""
CREATE_TABLE_SQL = """CREATE TABLE if NOT EXISTS Prelim (filename TEXT, monobit REAL, blockfreq REAL, runs REAL,
                      longestrun REAL, binarymatrank REAL, spectral REAL, notm  REAL, otm REAL, maurer  REAL, cumsum REAL,
                      cumsumrev REAL, randexcur1 REAL, randexcur2 REAL, randexcur3 REAL, randexcur4 REAL,
                      randexcur5 REAL, randexcur6 REAL, randexcur7 REAL, randexcur8 REAL, randexcurvar1 REAL,
                      randexcurvar2 REAL, randexcurvar3 REAL, randexcurvar4 REAL, randexcurvar5 REAL,
                      randexcurvar6 REAL, randexcurvar7 REAL, randexcurvar8 REAL, randexcurvar9 REAL, randexcurvar10 REAL,
                      randexcurvar11 REAL, randexcurvar12 REAL, randexcurvar13 REAL, randexcurvar14 REAL, randexcurvar15 REAL,
                      randexcurvar16 REAL, randexcurvar17 REAL, randexcurvar18 REAL, linearcomp REAL, serial1 REAL,
                      serial2 REAL, aproxent REAL)"""
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
         12: 'randomexcursionstest',
         13: 'randomexcursionsvarianttest',
         14: 'linearcomplexitytest',
         15: 'serialtest',
         16: 'aproximateentropytest'
         #not in use: 17: 'lempelzivcompressiontest',
      }

def proc_randtest(filename):
    bytes_str = file_to_bstr(filename)
    if bytes_str == -1:
        print "'%s' is too small to process" % filename
        return
    return performrndtest(filename, bytes_str, range(1, 17))

def file_to_bstr(filename, maxlen=32768):
    randin=""
    with open(filename, "r") as f:
        bytes_read = f.read()
        if len(bytes_read) * 8 < maxlen:
            return -1
        for b in bytes_read:
            n = ord(b)
            bstr = ""
            for x in xrange(8):
                bstr=str(n%2) + bstr
                n = n >> 1
            randin += bstr

    return randin[0:maxlen]


def performrndtest(filename, inputbits, testlist):
    out_vals = list()
    out_vals.append(filename)
    for i in testlist:
        try:
            out = eval("randtest." + tests[i])(inputbits)
            if type(out) is list:
                out_vals.extend(out)
            else:
                out_vals.append(out)
        except Exception as e:
            print e
            print out_vals
            print inputbits
            print filename
    return out_vals


def write_results(results):
    if results is None:
        return
    with lite.connect(DB_LOCATION) as conn:
        cur = conn.cursor()
        cur.execute(INSERT_PRELIM, tuple(results))
    print "Wrote results for %s" % results[0]

def run_small_randtest_async(samples_dir="samples/benign_testing/[0-9]*/*"):
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