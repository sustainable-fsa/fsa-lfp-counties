# ---------------------------------------------------------------------------
# usdm_data.py
# Created on: 2013-07-16
# Description: Process the shapes to the FGDB
# ---------------------------------------------------------------------------
import arcpy
import os
import sys

version = '2.0'

def process(the_work_gdb,base_data_dir,usdm_none,data_clip,web_clip,log_dir,log_file):
    #log = open(log_dir + log_file,'a')
    try:
        # Merge the layers to eliminate any underlying issues
        #theIMGDB = "in_memory"
        arcpy.Merge_management(["%s\\usdm_D0_P" % the_work_gdb, "%s\\usdm_D1_P" % the_work_gdb], "%s\\usdm_D0_M" % the_work_gdb)
        arcpy.Merge_management(["%s\\usdm_D1_P" % the_work_gdb, "%s\\usdm_D2_P" % the_work_gdb], "%s\\usdm_D1_M" % the_work_gdb)
        arcpy.Merge_management(["%s\\usdm_D2_P" % the_work_gdb, "%s\\usdm_D3_P" % the_work_gdb], "%s\\usdm_D2_M" % the_work_gdb)
        arcpy.Merge_management(["%s\\usdm_D3_P" % the_work_gdb, "%s\\usdm_D4_P" % the_work_gdb], "%s\\usdm_D3_M" % the_work_gdb)
        print "Merge QA\QC completed"
        # Dissolve the resulting feature for a homogenous dataset
        arcpy.Dissolve_management("%s\\usdm_D0_M" % the_work_gdb, "%s\\usdm_D0_D" % the_work_gdb, "", "", "MULTI_PART", "DISSOLVE_LINES")
        arcpy.Dissolve_management("%s\\usdm_D1_M" % the_work_gdb, "%s\\usdm_D1_D" % the_work_gdb, "", "", "MULTI_PART", "DISSOLVE_LINES")
        arcpy.Dissolve_management("%s\\usdm_D2_M" % the_work_gdb, "%s\\usdm_D2_D" % the_work_gdb, "", "", "MULTI_PART", "DISSOLVE_LINES")
        arcpy.Dissolve_management("%s\\usdm_D3_M" % the_work_gdb, "%s\\usdm_D3_D" % the_work_gdb, "", "", "MULTI_PART", "DISSOLVE_LINES")
        # Disolve D4
        arcpy.Dissolve_management(the_work_gdb+"\\usdm_D4_P", the_work_gdb+"\\usdm_D4_D", "", "", "MULTI_PART", "DISSOLVE_LINES")
        print "Dataset dissolved"
        # # Clean up the merged files when done
        arcpy.Delete_management("%s\\usdm_D0_P" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D1_P" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D2_P" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D3_P" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D4_P" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D0_M" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D1_M" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D2_M" % the_work_gdb)
        arcpy.Delete_management("%s\\usdm_D3_M" % the_work_gdb)
        #arcpy.Delete_management("in_memory")
        print "Working datasets that are no longer needed have been deleted."
        # Add the DM Level field
        arcpy.AddField_management ("%s\\usdm_D0_D" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        arcpy.AddField_management ("%s\\usdm_D1_D" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        arcpy.AddField_management ("%s\\usdm_D2_D" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        arcpy.AddField_management ("%s\\usdm_D3_D" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        arcpy.AddField_management ("%s\\usdm_D4_D" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        print "USDM Drought Level field added to data."
        # Calculate the DM Level field
        arcpy.CalculateField_management("%s\\usdm_D0_D" % the_work_gdb, "DM", "0", "PYTHON", "")
        arcpy.CalculateField_management("%s\\usdm_D1_D" % the_work_gdb, "DM", "1", "PYTHON", "")
        arcpy.CalculateField_management("%s\\usdm_D2_D" % the_work_gdb, "DM", "2", "PYTHON", "")
        arcpy.CalculateField_management("%s\\usdm_D3_D" % the_work_gdb, "DM", "3", "PYTHON", "")
        arcpy.CalculateField_management("%s\\usdm_D4_D" % the_work_gdb, "DM", "4", "PYTHON", "")
        print "USDM Drought Level field values calculated."
        # Erase the overlapping areas
        arcpy.Erase_analysis (usdm_none, the_work_gdb+"\\usdm_D0_D", the_work_gdb+"\\usdm_None_E", '#')
        arcpy.Erase_analysis ("%s\\usdm_D0_D" % the_work_gdb, "%s\\usdm_D1_D" % the_work_gdb, "%s\\usdm_D0_E" % the_work_gdb, '#')
        arcpy.Erase_analysis ("%s\\usdm_D1_D" % the_work_gdb, "%s\\usdm_D2_D" % the_work_gdb, "%s\\usdm_D1_E" % the_work_gdb, '#')
        arcpy.Erase_analysis ("%s\\usdm_D2_D" % the_work_gdb, "%s\\usdm_D3_D" % the_work_gdb, "%s\\usdm_D2_E" % the_work_gdb, '#')
        arcpy.Erase_analysis ("%s\\usdm_D3_D" % the_work_gdb, "%s\\usdm_D4_D" % the_work_gdb, "%s\\usdm_D3_E" % the_work_gdb, '#')
        print "Overlaping areas erased."
        # Add the DM Level field to the None feature
        arcpy.AddField_management ("%s\\usdm_None_E" % the_work_gdb, "DM", "SHORT", "", "", "", "USDM Drought Level", "", "", "")
        # Calculate the DM Level field
        arcpy.CalculateField_management("%s\\usdm_None_E" % the_work_gdb, "DM", "-1", "PYTHON", "")
        # Merge erased shapes into a single feature
        arcpy.Merge_management(["%s\\usdm_D0_E" % the_work_gdb,"%s\\usdm_D1_E" % the_work_gdb,"%s\\usdm_D2_E" % the_work_gdb,
                                "%s\\usdm_D3_E" % the_work_gdb,"%s\\usdm_D4_D" % the_work_gdb], "%s\\usdm_RAW_M" % the_work_gdb)
        print "Raw merged dataset created."
        # Merge for NDIS Style statistics
        arcpy.Merge_management(["%s\\usdm_RAW_M" % the_work_gdb,"%s\\usdm_None_E" % the_work_gdb], "%s\\usdm_NIDIS_M" % the_work_gdb)
        print "Nested merged dataset created."
        # Merge for NDMC Style statistics
        arcpy.Merge_management(["%s\\usdm_D0_D" % the_work_gdb,"%s\\usdm_D1_D" % the_work_gdb,"%s\\usdm_D2_D" % the_work_gdb,
                                "%s\\usdm_D3_D" % the_work_gdb,"%s\\usdm_D4_D" % the_work_gdb,"%s\\usdm_None_E" % the_work_gdb], "%s\\usdm_NDMC_M" % the_work_gdb)
        # Clip to the Web boundary
        arcpy.Clip_analysis("%s\\usdm_RAW_M" % the_work_gdb, web_clip, "%s\\usdm_M_WMS" % the_work_gdb)
        # Clip to the detailed county boundary
        arcpy.Clip_analysis("%s\\usdm_RAW_M" % the_work_gdb, data_clip, "%s\\usdm_detailed_MC" % the_work_gdb)
        arcpy.FeatureClassToShapefile_conversion("%s\\usdm_detailed_MC" % the_work_gdb,base_data_dir)
        
        print "Clipped datasets produced."
        print "Data processing completed."
        #log.write("Clipped datasets produced\n")
        #log.write("Data processing completed\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "FileExportErrors.log",'a')
        #log_e.write("RMA grid file error: " + e.message +"\n")
        #log_e.close()

    #log.close()         

