import time
import datetime
import arcpy
import sys, string, os
from arcpy import env
from arcpy import *
from arcpy.sa import *
import arcinfo

arcpy.env.overwriteOutput = True

def analyzeBLM():
    try:
        print outGDB
        arcpy.env.workspace = outGDB
        print '- erasing portfolio'
        arcpy.Erase_analysis(blmLands, tncPortfolio, 'blm_min_tnc')

        print '- removing sage grouse core areas'
        arcpy.Erase_analysis('blm_min_tnc', sageGrouse, 'blm_min_tnc_sg')

        print '- remove desert tortoise crit hab'
        arcpy.Erase_analysis('blm_min_tnc_sg', sageGrouse, 'blm_min_tnc_sg_tch')

        print '- remove desert tortoise corridors'
        arcpy.Erase_analysis('blm_min_tnc_sg_tch', sageGrouse, 'blm_min_tnc_sg_tch_tcor')

        print '- intersecting wind power class'
        arcpy.Clip_analysis(wpc, 'blm_min_tnc_sg_tch_tcor', 'wpc_in_blm')
    except:
        print 'ugh. problems'
        print arcpy.GetMessages(2)

outGDB = 'D:/NorthAmerica/NorthAmericaMaps/BLM_wind/BLM_wind.gdb/'
baseConservation = 'd:/NorthAmerica/base_conservation.gdb/'
blmLands = baseConservation+'padus_cbi_v2_blm_d'
tncPortfolio = baseConservation+'TNC_Areas'
sageGrouse = baseConservation+'usfws_blm_sage_grouse_priority_areas_conservation'
tortoiseCritHab = 'D:/NorthAmerica/NorthAmericaMaps/BLM_wind/BLM_wind.gdb/tortoise_critical_habitat'
tortoiseCorridors = 'D:/NorthAmerica/NorthAmericaMaps/BLM_wind/BLM_wind.gdb/tortoise_corridors'
wpc = 'D:/NorthAmerica/ConservationLands/ROI/data/Energy/Wind/NREL_WindEnergyPotential20131216.gdb/All_States01merge'

# Call function
print (sys.version)
analyzeBLM()