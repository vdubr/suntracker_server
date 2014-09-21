## python python/inport.py
#python python/libs/inport.py -p aprica

import sys,getopt
import grass.script as grass

def main(argv):
  try:
    opts, args = getopt.getopt(argv,"p:h:")
  except getopt.GetoptError:
    print 'python/libs/inport.py -p [name of folder in processingSettings (project)]'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
       print 'python python/libs/inport.py -p aprica'
       sys.exit()
    elif opt in ("-p"):
       project = arg

  outputRaster = 'inputDEMraster'
  inputRaster = "dem.tif"
  inputJSONextentMask = "extent.geojson"
  path = "processingSettings/"+project+"/"

  ##Inport geojson defining resort extent
  ##v.external dns='"GeoJSON:'+inputJSONextentMask+'"' --o output='projectMask'
  #grass.run_command("v.external",dsn = '"GeoJSON:'+inputJSONextentMask+'"',output = 'projectMask',overwrite=True)
  grass.run_command("v.external",flags='', dsn = path+inputJSONextentMask, layer="OGRGeoJSON",overwrite=True)
  grass.run_command("g.rename",vect='OGRGeoJSON,inputJSONextentMask',overwrite=True)

  ##transforn vector to raster to be able use it as mask
  ##grass.run_command("v.to.rast",input='inputJSONextentMask',type='area',output='inputJSONextentMask',use="cat",overwrite=True)

  grass.run_command("r.in.gdal",input = path + inputRaster ,output = outputRaster,overwrite=True)

  grass.run_command("g.region",rast=outputRaster)

if __name__ == "__main__":
   main(sys.argv[1:])
