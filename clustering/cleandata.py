import csv
import time
import datetime

#fileNames = ['./month0_test.csv']

fileNames = [
'./201710-hubway-tripdata.csv',
'./201711-hubway-tripdata.csv',
'./201712-hubway-tripdata.csv', 
'./201801_hubway_tripdata.csv', 
'./201802_hubway_tripdata.csv',
'./201803_hubway_tripdata.csv',
'./201804-hubway-tripdata.csv',
'./201805-bluebikes-tripdata.csv',
'./201806-bluebikes-tripdata.csv',
'./201807-bluebikes-tripdata.csv',
'./201808-bluebikes-tripdata.csv',
'./201809-bluebikes-tripdata.csv',
'./201810-bluebikes-tripdata.csv']


def timeInRange(start, end,x):
    return start <= x and x <= end

month = 0
for fn in fileNames:
    print(month,fn)
    fnM = open('Month' + str(month) + '-cleaned-morning.csv', mode='w')
    fnE = open('Month' + str(month) + '-cleaned-evening.csv', mode='w')
    with open(str(fn)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                for element in row:
                    fnE.write(element + ",")
                    fnM.write(element + ",")
                fnE.write("\n")
                fnM.write("\n")
            elif (row[12] == 'Subscriber'):
                #'2017-10-01 00:03:43'
                #print(row[1])
                dt = datetime.datetime.utcnow()
                try:
                    dt =datetime.datetime.strptime(row[1], "%Y-%m-%j %H:%M:%S")
                except:
                    dt = datetime.datetime.strptime(row[1], "%Y-%m-%j %H:%M:%S.%f")
                t = dt.time()
                #narrow for commute window only
                mStart = datetime.time(7, 0 , 0)
                mEnd = datetime.time(11, 0, 0)
                eStart = datetime.time(15, 0, 0)
                eEnd = datetime.time(19, 0, 0)
                if timeInRange(mStart,mEnd,t):
                    #print('morning')
                    for element in row:
                        fnM.write(element + ",")
                    fnM.write("\n")
                elif timeInRange(eStart,eEnd,t):
                    #print('evening')
                    for element in row:
                        fnE.write(element + ",")
                    fnE.write("\n")

            line_count += 1
        print('Lines = ' + str(line_count))
    fnE.close()
    fnM.close()
    month +=1 