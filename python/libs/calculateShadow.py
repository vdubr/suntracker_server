##time python python/libs/calculateShadow.py -s "2,1" -t "2,2" -p aprica

import sys,getopt,datetime
import grass.script as grass
from subprocess import call

project = "outputRR"

##year
year = 2014

#hours = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
hours = [7,8,9,10,11,12,13,14,15,16,17,18,19]
#hours = [12,13,14,15]


minutes = ["0000","1666","3333","5000","6666","8333"]
minutesIndex = ["00","10","20","30","40","50"]
#minutes = ["1666"]


def main(argv):
  ##compute slope and aspect to future computing
  grass.run_command("r.slope.aspect",elevation="inputDEMraster",slope = "edu_raster_slope",aspect = "edu_raster_aspect",overwrite=True)

  start = ''
  stop = ''
  sun = 'n'
  shade = 'y'

  try:
    opts, args = getopt.getopt(argv,"s:t:p:h:")
  except getopt.GetoptError:
    print 'calculateShadow.py -s [start date - month,day] -t [stop date - month,day] -p [output directory name try same as project name]'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
       print 'python python/calculateShadow.py -s "2,1" -t "2,2" -p aprica'
       sys.exit()
    elif opt in ("-s"):
       start = arg
    elif opt in ("-t"):
       stop = arg
    elif opt in ("-p"):
       project = arg


  ##define dates
  startDate = datetime.date(year,int(start.split(",")[0]),int(start.split(",")[1]))
  stopDate = datetime.date(year,int(stop.split(",")[0]),int(stop.split(",")[1]))

  delta = stopDate - startDate

  startDay = startDate.timetuple().tm_yday
  numberDays = delta.days


  #prepare folders
  call(["rm", "-rf", project])
  call(["mkdir", project])
  call(["mkdir", project+"/sun"])
  call(["mkdir", project+"/shade"])


  createRegionDefinition(project)


  # i is the day of year (DOY) to use for running r.sun
  for d in range(startDay, startDay + numberDays):
    strDay = str(d).zfill(3) + "/"
    call(["mkdir", project+"/sun/" + strDay ])
    call(["mkdir", project+"/shade/" + strDay])
    ##delete shadeCumulation on start of every day
    grass.run_command("r.mapcalc",expression="shadeCumulation = 0",overwrite=True)

    for h in hours:
      strHour = str(h).zfill(2) + "/"
      call(["mkdir", project+"/sun/" + strDay + strHour])
      call(["mkdir", project+"/shade/" + strDay + strHour])
      for n in minutes:

        ##want to get insolation time, global radiation
        #insolname = "insolDAY_" + str(d) + "_HOUR_" + str(h) + "_MINUTES_" + str(minutes.index(str(n)))
        insolname = "insolation"

        computeInsolation(n,h,d,insolname,project)

        computeSunShade(n,h,d,insolname,project)

        ##FIXME
        ##cleane grass location for insolname,

    ##if last calculated value -> export shade cumulation
    if h==hours[-1]:
      print(999999996666666)
      exportShadeCumulation(project,d,h)



def createRegionDefinition(project):
  ##start of write extent
  call(["mkdir", project+"/region"])

  ##regionInfo = grass.run_command("g.region",flags="g")
  ## create extent with boundary as [project]/extent.geojson and save it under resortExtent
  grass.run_command("g.region",save="resortExtent",n=grass.vector_info('inputJSONextentMask').north,s=grass.vector_info('inputJSONextentMask').south,w=grass.vector_info('inputJSONextentMask').west,e=grass.vector_info('inputJSONextentMask').east)
  reg = grass.region()

  f = open(project+'/region/region.json', 'w+')
  print >>f, '{"n":'+str(reg.n) + ',"s":'+str(reg.s)+',"w":'+str(reg.w) + ',"e":'+str(reg.e)+'}'
  f.close()

  grass.run_command("g.region",rast='inputDEMraster')
  ##end of write extent


def computeInsolation(n,h,d,insolname,project):
  strDay = str(d).zfill(3) + "/"
  strHour = str(h).zfill(2) + "/"

  # run the solar model
  # r.sun elev=inputDEMraster asp_in=edu_raster_slope slope_in=edu_raster_aspect day=32 time=12.50 incidout=insolname --o
  grass.run_command("r.sun", elev = "inputDEMraster",asp_in = "edu_raster_slope",slope_in="edu_raster_aspect" ,day=d, time=str(h)+'.'+str(n) ,incidout=insolname,overwrite=True)

  # export the outputs to GTiff files
  # r.out.gdal -c -f --o output=compSun.tiff type=Byte input=insolname createopt="COMPRESS=DEFLATE,PREDICTOR=2,ZLEVEL=9"

  #grass.run_command("g.region",region="resortExtent")

  grass.run_command("g.region",n=grass.vector_info('inputJSONextentMask').north,s=grass.vector_info('inputJSONextentMask').south,w=grass.vector_info('inputJSONextentMask').west,e=grass.vector_info('inputJSONextentMask').east)

  insolPath = project+"/sun/" + strDay + strHour + minutesIndex[minutes.index(str(n))]
  grass.run_command("r.out.gdal",flags="cf",input = insolname, output = insolPath +".tiff", type="Byte", createopt="COMPRESS=DEFLATE,PREDICTOR=2,ZLEVEL=9",overwrite=True)
  call(["gdal_translate", '-ot', "Byte", '-of', "PNG", insolPath + '.tiff',  insolPath + '.png'])
  call(["rm", insolPath + '.tiff'])
  call(["rm", insolPath + '.png.aux.xml'])

  grass.run_command("g.region",rast='inputDEMraster')
  #grass.run_command("r.out.png", input = insolname, output = project+"/sun/" + strDay  + strHour + minutesIndex[minutes.index(str(n))] +".png",overwrite=True,flags="t")




def computeSunShade(n,h,d,insolname,project):
  strDay = str(d).zfill(3) + "/"
  strHour = str(h).zfill(2) + "/"

  ##fill null values
  #r.null map=insolMONTH_0_DAY_2_HOUR_13_MINUTES_40 null=-1
  grass.run_command("r.null",map = insolname, null = -1)

  ##reclass sun to null and shade to 1
  # r.mapcalc expression='shade = if(insolMONTH_0_DAY_2_HOUR_13_MINUTES_40 == -1,1,null())' --o
  grass.run_command("r.mapcalc",expression = 'shade = if(' + insolname + ' == -1,1 ,null() )', overwrite=True)

  ##set shade color map
  #r.colors map=shade rules=python/colorrules
  grass.run_command("r.colors",map="shade",rules="python/libs/colorrules")


  ##export to png


  ##pokud je dopoledne secist
  #pokud je poledne vyexportovat a vymazat
  #secist
  #r.mapcalc expression='shadeCumulation = shadeCumulation + shade' --o

  if h==12 and n==minutes[0]:
    print(1111666668888)
    exportShadeCumulation(project,d,h)
    grass.run_command("r.mapcalc",expression="shadeCumulation = 0",overwrite=True)



  grass.run_command("r.mapcalc",expression="shadeCumulation = if(isnull(shade),shadeCumulation,shadeCumulation+shade)",overwrite=True)
  #grass.run_command("r.mapcalc",expression="shadeCumulation = if(shadeCumulation)",overwrite=True)
  #grass.run_command("r.info",map='shadeCumulation')
  print("cumul:")
  grass.run_command("r.stats",input = 'shadeCumulation',flags="c")
  print("shade:")
  grass.run_command("r.stats",input = 'shade',flags="c")


  shadePath = project+"/shade/" + strDay + strHour + minutesIndex[minutes.index(str(n))]
  #grass.run_command("r.out.gdal",flags="cf",input="shade", output = shadePath + '.tiff', type="Byte",createopt="COMPRESS=DEFLATE,PREDICTOR=2,ZLEVEL=9",overwrite=True)

  #grass.run_command("g.region",region="resortExtent")
  grass.run_command("g.region",n=grass.vector_info('inputJSONextentMask').north,s=grass.vector_info('inputJSONextentMask').south,w=grass.vector_info('inputJSONextentMask').west,e=grass.vector_info('inputJSONextentMask').east)

  grass.run_command("r.out.png",flags="t", input="shade", output = project+"/shade/" + strDay + strHour + minutesIndex[minutes.index(str(n))] + '.png', overwrite=True)
  #gdal_translate -ot Byte -of PNG C:\Users\Loukotka\Dropbox\ESA-2014\vojta\40.tiff C:/Users/Loukotka/Dropbox/ESA-2014/vojta/40png.png
  #gdal_translate -ot "Byte" -of "PNG" spindl3/shade/003/12/10.tiff spindl3/shade/003/12/10.png


  grass.run_command("g.region",rast='inputDEMraster', overwrite=True)


def exportShadeCumulation(project,d,h):
  strDay = str(d).zfill(3)

  noontype = "afternoon"

  if h <= 12:
    noontype = "morning"

  #grass.run_command("r.out.ascii",input = "shadeCumulation", output = project + "/shade/" + strDay  + noontype + ".asc", overwrite=True)
  grass.run_command("g.rename",rast="shadeCumulation,"+project+"."+strDay+"."+noontype, overwrite=True)

if __name__ == "__main__":
   main(sys.argv[1:])
