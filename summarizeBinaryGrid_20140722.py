# Title:    ZonalStatsNDVI_20140528.py
# Purpose:  Calculates MEAN values of NDVI raster pixels within the Zones of 
#           the Multi-Ring Buffer distances dataset and outputs to a Table.
#           Zonal Stats results get Appended into output Table.
#           Creates individual School NDVI output tables then reads these to
#           and populates a new "NDVI" table that places all MEAN NDVI values into
#           rows, with the School_ID, one row for each School.
# Requires: Spatial Analyst Extension
# Author:   Jan Slaats, GIS Mgr, TNC NACR and Jim Platt, Geographer, TNC NACR.
# Date:     20140528
# Changes:
#
#=================================================================================

# Import system modules
import os
import arcpy
import time
import datetime
from arcpy import env
from arcpy.sa import *

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Set overwrite option
arcpy.env.overwriteOutput = True

# Set workspace variables
# Location of input FeatureClasses
inWSZones = r'C:\Schools\California_Cdrive\CA_SchoolBuildings_MultiBufferErase_ALL.gdb'  # Modify accordingly!
# Location of input NDVI Rasters (.tif Files in a folder)
rasterDir = r'C:\Schools\NDVI'                                                           # Modify accordingly!
# Location for Output Table Data
outTableGDB = r'C:\Schools\NDVI_Extracts.gdb'                                            # Modify accordingly!

# Set local variables
bufferDists = ['0010', '0050', '0100', '0300', '0500', '0750', '1000'] # Fixed buffer distances in each input FC Table
zoneField = "DIST"                              # Text field containing buffer distance values
config_keyword = ""                             # Empty Config Keyword in CreateTable command
schemaType = "NO_TEST"                          # Append command "NO_TEST" Schema_Type option
fieldMappings = ""                              # Append command unused Field Mapping setting option 
subtype = ""                                    # Append command unused subtype option
schoolID = "0000"                               # Initialize schoolID value

# Create variables for the input FCs coming from the inWSZones
arcpy.env.workspace = inWSZones
inFCList = ['School_0485', 'School_1681'] # arcpy.ListFeatureClasses()           # for individual FCs = ['School_0017', 'School_0021']

# Mark Start time of script run
print "Script Started: " , datetime.datetime.now()

# For loop for FeatureClasses from inWSZones
for fc in inFCList:
    try:
        # Set variable for School_ID, reading right-most 4 numbers from FeatureClass name
        print 'Processing: {0}'.format(fc)
        schoolID = format(fc[7:11])
        print '>> SchoolID is: ' + schoolID
        
        # Set input FeatureClasss Name
        inFeatureClass = os.path.join(inWSZones, fc)
        # Set input Raster Name
        inRaster = os.path.join(rasterDir, "{0}_01NDVI.tif".format(fc))

        # Create an output Table to Append output data into
        arcpy.CreateTable_management(outTableGDB, "{0}_all".format(fc), os.path.join(outTableGDB, "appendTemplate"))
        arcpy.MakeTableView_management(os.path.join(outTableGDB, "{0}_all".format(fc)), "appendView")

        # Nested Loop to generate Zonal Statistics for each Buffer Distance Polygon        
        for bufferDist in bufferDists:
            try:
                # Set output Table Name
                outTable = os.path.join(outTableGDB, "{0}_{1}".format(fc, bufferDist))
                print "Buffer Distance is: " + bufferDist
                
                # Make temporary Feature Layer for each Buffer Distance
                try:
                    print "Creating Feature Layer: {0}".format("{0}_LYR".format(fc))
                    arcpy.MakeFeatureLayer_management(fc, "{0}_LYR".format(fc), '"DIST" = \'{0}\''.format(bufferDist.lstrip("0")))
                except arcpy.ExecuteError:
                    print arcpy.GetMessages(2)
                except Exception as e:
                    print e.args[0]
                    
                # Execute ZonalStatisticsAsTable
                try:
                    print "Running Zonal Stats as Table on: {0}".format(os.path.basename(inRaster))
                    outZSaT = ZonalStatisticsAsTable("{0}_LYR".format(fc), zoneField, inRaster, outTable, "NODATA", "MEAN")
                except arcpy.ExecuteError:
                    print arcpy.GetMessages(2)
                except Exception as e:
                    print e.args[0]                
                
                # Append Output ZonalStats Table to OutputTable
                try:
                    print "Appending Zonal Stats to: {0}".format("{0}_all".format(fc))
                    arcpy.Append_management(outTable, "appendView", schemaType, fieldMappings, subtype)
                except arcpy.ExecuteError:
                    print arcpy.GetMessages(2)
                except Exception as e:
                    print e.args[0]
   
                #Pick up your mess
                try:
                    print "Deleting Feature Layer: {0}".format(os.path.basename(outTable))
                    arcpy.Delete_management(outTable)
                except arcpy.ExecuteError:
                    print arcpy.GetMessages(2)
                except Exception as e:
                    print e.args[0]
                    
            except:
                 print e.args[0]
                 print arcpy.GetMessages()
                 
        # Populate School_ID value field in OutputTable
        arcpy.CalculateField_management(os.path.join(outTableGDB,"{0}_all".format(fc)), "SCHOOL_ID", schoolID, "PYTHON", "#")

    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
        
    # Mark Start time of script run
    print "School Processing Ended: " , datetime.datetime.now()
    print "\n"

try:
    print ("Creating table: {0}".format("NDVI"))
    arcpy.env.workspace = outTableGDB
    arcpy.CreateTable_management(outTableGDB, "NDVI")
    arcpy.AddField_management("NDVI", "Unique_School_ID", "TEXT", "", "", 20)
    arcpy.AddField_management("NDVI", "NDVI_10m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_50m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_100m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_300m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_500m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_750m", "DOUBLE")
    arcpy.AddField_management("NDVI", "NDVI_1000m", "DOUBLE")
except arcpy.ExecuteError:
    print arcpy.GetMessages(2)
except Exception as e:
    print e.args[0]

try:
    print "Creating list of schools to summarize..."
    schoolList = arcpy.ListTables(wild_card="School*", table_type="ALL")
except arcpy.ExecuteError:
    print arcpy.GetMessages(2)
except Exception as e:
    print e.args[0]

try:
    for school in schoolList:
        schoolID = school[7:11]
        print "Summarizing school {0}".format(schoolID)
        schoolCursor = arcpy.SearchCursor(school, "", "", "DIST; MEAN")
        theDict = {}
        for row in schoolCursor:
            theDict[row.DIST.zfill(4)] = row.MEAN
        del row
        del schoolCursor
        
        rowsNDVI = arcpy.InsertCursor("NDVI")
        rowNDVI = rowsNDVI.newRow()
        rowNDVI.setValue("Unique_School_ID", schoolID)
        rowNDVI.setValue("NDVI_10m", theDict["0010"])
        rowNDVI.setValue("NDVI_50m", theDict["0050"])
        rowNDVI.setValue("NDVI_100m", theDict["0100"])
        rowNDVI.setValue("NDVI_300m", theDict["0300"])
        rowNDVI.setValue("NDVI_500m", theDict["0500"])
        rowNDVI.setValue("NDVI_750m", theDict["0750"])
        rowNDVI.setValue("NDVI_1000m", theDict["1000"])
        rowsNDVI.insertRow(rowNDVI)
        del rowNDVI
        del rowsNDVI
        
except arcpy.ExecuteError:
    print arcpy.GetMessages(2)
except Exception as e:
    print e.args[0]

arcpy.CheckInExtension("Spatial")

# Mark Start time of script run
print "\n"
print "NDVI Table Finished: " , datetime.datetime.now()

print "Finished"

