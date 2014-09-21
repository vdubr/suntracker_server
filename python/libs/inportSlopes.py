##time python python/libs/inportSlopes.py -p "spindl"

import sys,getopt,datetime
import grass.script as grass
from subprocess import call


def main(argv):
  try:
    opts, args = getopt.getopt(argv,"p:h")
  except getopt.GetoptError:
    print 'inportSlopes.py -p [name of project]'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
       print 'test.py -i <inputfile> -o <outputfile>'
       sys.exit()
    elif opt in ("-p"):
       project = arg

  grass.run_command("v.in.ogr",flags='', dsn = "processingSettings/"+project+"/slope.shp", layer="slope",overwrite=True)

  grass.run_command("v.external",flags='', dsn = "processingSettings/"+project+"/outline.shp", layer="outline",overwrite=True)

  grass.run_command("g.region", vect="outline")

  #grass.run_command("v.to.rast", input="slopes", output="slopes", use="val",overwrite=True)


if __name__ == "__main__":
   main(sys.argv[1:])
