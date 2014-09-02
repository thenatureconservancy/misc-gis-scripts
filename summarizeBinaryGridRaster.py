# Import system modules
import os, arcpy, time, datetime
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

def summarizeBinaryGrid(rasterDir, inWSZones, outputTable):
	#arcpy.env.workspace = inWSZones
	#inFCList = ['School_0485', 'School_1681', 'School_0017', 'School_0021', 'School_0213', 'School_0247', 'School_0106', 'School_0261', 'School_0158', 'School_0283'] # arcpy.ListFeatureClasses()           # for individual FCs = ['School_0017', 'School_0021']
	#inFCList = arcpy.ListFeatureClasses()
	arcpy.env.workspace = rasterDir
	#inFCList = ['School_0082.tif', 'School_0261.tif']
	inFCList = arcpy.ListRasters()
	arcpy.env.workspace = inWSZones
	outFile = open(outputTable, 'w', )
	outFile.write('schoolID, 0010, 0050, 0100, 0300, 0500, 0750, 1000 \n')
	for school in inFCList:
		try:
			#fc = os.path.splitext(school)[0]
			fc = school
			outFile.write(fc+',')
			sumRaster = rasterDir + '/' + school
			for bufferDist in bufferDists:
				try:
					zeroCount = 0
					oneCount = 0
					arcpy.MakeFeatureLayer_management (fc, fc+bufferDist,'"DIST" = \'{0}\''.format(bufferDist.lstrip("0")))
					clipGrid = arcpy.gp.ExtractByMask_sa(sumRaster, fc+bufferDist, outTableGDB+fc+'_'+bufferDist)
					try:
						with arcpy.da.SearchCursor(clipGrid, ['COUNT'], '"VALUE" = 0') as cursor:
							for row in cursor:
								zeroCount = (row[0])
					except:
						zeroCount = 0
					try:			
						with arcpy.da.SearchCursor(clipGrid, ['COUNT'], '"VALUE" = 1') as cursor:
							for row in cursor:
								oneCount = (row[0])
					except:
						oneCount = 0
					try:
						if oneCount > 0:
							prcnt = (float(oneCount)/float(zeroCount+oneCount))*100
						else:
							prcnt = 0
					except:
						prcnt = 0
					outFile.write(str(prcnt)+',')
					arcpy.Delete_management(clipGrid)
				except:
					print 'problem in inner loop'
			outFile.write(' \n')
			print fc + ' - '+ str(datetime.datetime.now())
		except:
			print "WARNING. Problem with " +fc
	outFile.close()

# Location of input FeatureClasses
inWSZones = r'D:/NorthAmerica/NorthAmericaMaps/Schools/data/CA_SchoolBuildings_MultiBufferErase_ALL_1.gdb' 
rasterDir = r'D:/NorthAmerica/NorthAmericaMaps/Schools/data/CA_CropsReclassifiedBinary20140729.gdb'                                                           
outTableGDB = r'D:/NorthAmerica/NorthAmericaMaps/Schools/data/temp.gdb/'
outputTable = r'D:/NorthAmerica/NorthAmericaMaps/Schools/data/Crop3.csv'                                           

# Set local variables
bufferDists = ['0010', '0050', '0100', '0300', '0500', '0750', '1000'] # Fixed buffer distances in each input FC Table
zoneField = "DIST"                              # Text field containing buffer distance values

# CALL FUNCTION -------------
summarizeBinaryGrid(rasterDir, inWSZones, outputTable)
