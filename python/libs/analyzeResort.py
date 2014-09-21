#!/usr/bin/python

##I have bug, my python cant find r.mask command, so I have to call it directly
## please change it

pathToRmask="/Applications/GRASS-7.0.app/Contents/MacOS/scripts/r.mask"
vdbdropcolumn="/Applications/GRASS-7.0.app/Contents/MacOS/scripts/v.db.dropcolumn"
vdbaddcolumn="/Applications/GRASS-7.0.app/Contents/MacOS/scripts/v.db.addcolumn"
vdbupdate="/Applications/GRASS-7.0.app/Contents/MacOS/scripts/v.db.update"

##time python python/libs/analyzeResort.py -p "aprica"

import sys,getopt,datetime
import grass.script as grass
import os
import json
from json import JSONDecoder
from json import JSONEncoder
from subprocess import call


def main(argv):
  try:
    opts, args = getopt.getopt(argv,"p:e:")
  except getopt.GetoptError:
    print 'analyzeResort.py -p [name of existing project]'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit()
    elif opt in ("-p"):
      project = arg


  analyzeSlopes(project)

  #grass.run_command("v.to.rast", input="slopes", output="slopes", use="val",overwrite=True)


  ##g.region vect=out

  print( "r.mask vector=outline")
  print( "r.stats input=corine output=" + project + "/region/corineStats.txt separator=comma -c -n --o")
  print( "r.mask -r")


  call([pathToRmask,'vector=outline'])
  ##grass.run_command("r.mask", vector="outline")
  ##r.stats input=corine output=statsCorine.txt -c --o -n separator=comma
  grass.run_command("r.stats", input="corine", separator="comma",output= project + "/region/corineStats.txt", flags="cn",overwrite=True)
  ##r.mask -r
  ##grass.run_command("r.mask", flags="r")
  call([pathToRmask,'-r'])


def analyzeSlopes(project):
  #for dirname, dirnames, filenames in os.walk(project+"/shade/"):
  #  print (dirname, dirnames, filenames)
  days = os.listdir(project+"/shade/")

  #clean db from columns
  call([vdbdropcolumn,'map=slope','columns=morning'])
  call([vdbdropcolumn,'map=slope','columns=afternoon'])
  #grass.run_command("v.db.dropcolumn", map="slope", column="morning")
  #grass.run_command("v.db.dropcolumn", map="slope", column="afternoon")
  call([vdbaddcolumn,'map=slope','columns=morning'])
  call([vdbaddcolumn,'map=slope','columns=afternoon'])
  #grass.run_command("v.db.addcolumn", map='slope', columns="morning")
  #grass.run_command("v.db.addcolumn", map='slope', columns="afternoon")
  call([vdbupdate,'map=slope','column=morning','value={}'])
  call([vdbupdate,'map=slope','column=afternoon','value={}'])

  for day in days:
    #r.external input=aprica/shade/032/afternoon.tiff output=afternoon
    ##grass.run_command("r.in.ascii", input=project+"/shade/"+day+"/afternoon.asc",output= "afternoon",overwrite=True)
    #grass.run_command("r.info",map="afternoon")
    #grass.run_command("r.mapcalc",expression="afternoonA = afternoon")
    ##v.buffer input=slope output=slopeBuffer distance=10

    slopesdb = grass.vector_db_select('slope',columns='cat')['values']
    print slopesdb
    #slopesdb=[10]
    for id in slopesdb:
      grass.run_command("v.buffer", where="cat="+str(id),input="slope",output="slopeBuffer",distance=0.0008333333333333334,overwrite=True)

      call([pathToRmask,'vector=slopeBuffer'])

      #print ("ids:",slopesdb,id)
      #a=grass.run_command("v.db.select", flags="vc",map='slope', where='cat=1', columns='morning')
      config = JSONDecoder().decode('{}')
      morningObject=JSONDecoder().decode(grass.vector_db_select('slope',columns='morning')['values'][id][0])
      afternoonObject=JSONDecoder().decode(grass.vector_db_select('slope',columns='afternoon')['values'][id][0])

      morningObject[day]=str(computeSlopeShadowStats(project,day,"morning"))
      afternoonObject[day]=str(computeSlopeShadowStats(project,day,"afternoon"))

      call([vdbupdate,'map=slope','column=morning','where=cat='+str(id),'value='+JSONEncoder().encode(morningObject)])
      call([vdbupdate,'map=slope','column=afternoon','where=cat='+str(id),'value='+JSONEncoder().encode(afternoonObject)])
      #grass.run_command("v.db.update", map='slope', columns="afternoon",where="cat="+str(id),value=4)

      #print grass.run_command("r.stats", input= project+"." + day + ".morning", separator="comma", flags="cn",overwrite=True)
      call([pathToRmask,'-r'])


def computeSlopeShadowStats(project,day,noontype):
  print(project,day,noontype)
  path = project+"/shade/"+day+"/"
  pathStat = path + "slopeShedeStatistics"+noontype+".txt"
  grass.run_command("r.stats", input= project+"." + day + "." + noontype, separator="comma",output=pathStat , flags="cn",overwrite=True)

  with open(pathStat, 'r') as f:
    data = f.readlines()

    numberOfMeasure = 0
    totalCount = 0
    tmpCount = 0
    categories = []

    for line in data:

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
  if tmpCount ==0:
    percentage = 0
  else:
    percentage = 100/float((float(totalCount*lastIndex)/float(tmpCount)))
  #100/((2173*36)/53964)

  print("percentage:",percentage,"%")
  return int(percentage)


if __name__ == "__main__":
   main(sys.argv[1:])
