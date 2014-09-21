##time python python/libs/api.py -p "aprica" -n "Aprica"

import sys,getopt,datetime
import json
import os
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from json import JSONDecoder
from subprocess import call
import grass.script as grass


def main(argv):
  try:
    opts, args = getopt.getopt(argv,"p:n:h")
  except getopt.GetoptError:
    print 'api.py -p [name of existing project]'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
       print 'test.py -i <inputfile> -o <outputfile>'
       sys.exit()
    elif opt in ("-p"):
       project = arg
    elif opt in ("-n"):
       name = arg


  ## region definition
  with open(project+'/region/region.json', 'r') as f:
      regionData = json.load(f)
      ##print souht coord
      ##print data['s']

  corineStatistics = computeCorineStatistics(project)

  call(["rm", "-rf",project+"/api"])
  call(["mkdir", project+"/api"])
  file = open(project+"/api/api.json", "w")

  config = JSONDecoder().decode('{}')
  ##'{"region":' + json.dumps(regionData) + ',"statistics":' + corineStatistics +"}")

  config["name"]=name
  config["tag"]=project
  config["region"]=regionData
  config["statistics"]=corineStatistics

  print config
  strConfig = json.dumps(config,encoding="utf-8")

  file.write(strConfig)
  file.close()

  grass.run_command("v.out.ogr",input="slope", type="line" ,format="GeoJSON", dsn=project+"/api/slopes.json",overwrite=True)


def computeCorineStatistics(project):
  ##region statistics
  with open(project+'/region/corineStats.txt', 'r') as f:
    data = f.readlines()

    valueCount = 0
    forest = 0
    bareLand = 0

    for line in data:
        words = line.split(',')
        print words[0]
        corClass = int(words[0])
        value = int(words[1])
        if corClass in (23,24,25):
          forest = forest+value
        elif corClass in(31,32,33,34):
          bareLand = bareLand + value

        valueCount = valueCount + value


    ##rounded percents
    if valueCount == 0:
      forestPercent=0
      bareLandPercent=0
    else:
      forestPercent = int(round(forest/(valueCount/100),-1))
      bareLandPercent = int(round(bareLand/(valueCount/100),-1))
    #return object vith indexes
    return JSONDecoder().decode('{"forest":'+str(forestPercent)+',"bareLand":'+ str(bareLandPercent)+'}')


def computeSlopeShadowStats(project,noontype):
  days = os.listdir(project+"/shade/")
  for day in days:
    path = project+"/shade/"+day+"/"
    pathStatAfternoon = path + "slopeShedeStatistics"+noontype+".txt"

    with open(pathStatAfternoon, 'r') as f:
      data = f.readlines()

      numberOfMeasure = 0
      totalCount = 0
      tmpCount = 0
      categories = []

      for line in data:
        print(line)
        words = line.split(',')

        measureCount = int(words[0])
        value = int(words[1])
        if measureCount == 0:
          totalCount = totalCount+value
        else:
          totalCount = totalCount+value
          tmpCount = tmpCount + (value*measureCount)
          #categories.push(value)

      lastIndex = int(data[-1].split(',')[0])
      print(totalCount,lastIndex,tmpCount)
      percentage = 100/float((float(totalCount*lastIndex)/float(tmpCount)))
      #100/((2173*36)/53964)

      print("soucet:",totalCount)
      print("tmpCount:",tmpCount)
      print("percentage:",percentage,"%")





if __name__ == "__main__":
   main(sys.argv[1:])
