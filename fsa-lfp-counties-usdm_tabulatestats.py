# ---------------------------------------------------------------------------
# usdm_tabulatestats.py
# Created on: 2013-09-10
# Description: Lookup the comparision dates for a given USDM date
# ---------------------------------------------------------------------------
import arcpy
import datetime
import sys

version = '1.0'

#def stats(the_work_gdb,regions,climdiv,usace,urban,wfo,rfc,huc8,huc6,huc4,huc2,counties):
def county(the_work_gdb,counties, log_dir, log_file):
    
    #log = open(log_dir + log_file,'a')

    try:
        ### Tabular clip of areas
        ###     Counties
        arcpy.TabulateIntersection_analysis(counties,
                                            "CountyFIPS;StateAbbr;StateFIPS;County_Pop_2010;County_Pop_Density_2010;County_Area_Mi;State_Pop_2010;Conus_Pop_2010;TotalUs_Pop_2010;State_Area_Mi;Conus_Area_Mi;TotalUs_Area_Mi;ISCONUS;ISTOTAL;FemaRgnId;FemaRgn_Area_Mi;FemaRgn_Pop_2010"
                                            , "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_county_ndmc" % the_work_gdb
                                            , "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(counties,
                                            "CountyFIPS;StateAbbr;StateFIPS;County_Pop_2010;County_Pop_Density_2010;County_Area_Mi;State_Pop_2010;Conus_Pop_2010;TotalUs_Pop_2010;State_Area_Mi;Conus_Area_Mi;TotalUs_Area_Mi;ISCONUS;ISTOTAL;FemaRgnId;FemaRgn_Area_Mi;FemaRgn_Pop_2010"
                                            , "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_county_nidis" % the_work_gdb
                                            , "DM", "", "", "SQUARE_MILES")
        # Process: Add Field State Area and Population
        arcpy.AddField_management("%s\\stats_county_ndmc" % the_work_gdb, "Cnty_P", "DOUBLE", "3", "3", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_county_nidis" % the_work_gdb, "Cnty_P", "DOUBLE", "3", "3", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_county_ndmc" % the_work_gdb, "Cnty_PP", "DOUBLE", "3", "3", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_county_nidis" % the_work_gdb, "Cnty_PP", "DOUBLE", "3", "3", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field State Area and Population
        arcpy.CalculateField_management("%s\\stats_county_ndmc" % the_work_gdb, "Cnty_P", "!County_Pop_Density_2010!* !AREA!", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_county_nidis" % the_work_gdb, "Cnty_P", "!County_Pop_Density_2010!* !AREA!", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_county_ndmc" % the_work_gdb, "Cnty_PP", "(!Cnty_P!/ !County_Pop_2010!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_county_nidis" % the_work_gdb, "Cnty_PP", "(!Cnty_P!/ !County_Pop_2010!)*100", "PYTHON", "")
        print "County statistics tabulated"
        #log.write("County statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("County statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    try:    
        #################### State Processing
        # Process: Summary State
        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_state_ndmc" % the_work_gdb, "AREA SUM;State_Area_Mi MAX;Cnty_P SUM;State_Pop_2010 MAX", "DM;StateFIPS")
        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_state_nidis" % the_work_gdb, "AREA SUM;State_Area_Mi MAX;Cnty_P SUM;State_Pop_2010 MAX", "DM;StateFIPS")
        # Process: Add Field State Area and Population
        arcpy.AddField_management("%s\\stats_state_ndmc" % the_work_gdb, "ST_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_state_nidis" % the_work_gdb, "ST_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_state_ndmc" % the_work_gdb, "ST_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_state_nidis" % the_work_gdb, "ST_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field State Area and Population
        arcpy.CalculateField_management("%s\\stats_state_ndmc" % the_work_gdb, "ST_A_prct", "(!SUM_AREA!/ !MAX_State_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_state_nidis" % the_work_gdb, "ST_A_prct", "(!SUM_AREA!/ !MAX_State_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_state_ndmc" % the_work_gdb, "ST_P_prct", "(!SUM_Cnty_P!/ !MAX_State_Pop_2010!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_state_nidis" % the_work_gdb, "ST_P_prct", "(!SUM_Cnty_P!/ !MAX_State_Pop_2010!)*100", "PYTHON", "")
        print "State statistics tabulated"
        #log.write("State statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("State statistics taubuation error: " + e.message +"\n")
        #log_e.close()
        
    try:    
        #################### FEMA Processing
        # Process: Summary FEMA Regions
        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_fema_ndmc" % the_work_gdb, "AREA SUM;Cnty_P SUM;FemaRgn_Area_Mi MAX;FemaRgn_Pop_2010 MAX", "DM;FemaRgnId")
        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_fema_nidis" % the_work_gdb, "AREA SUM;Cnty_P SUM;FemaRgn_Area_Mi MAX;FemaRgn_Pop_2010 MAX", "DM;FemaRgnId")
        # Process: Add Field FEMA Area and Population
        arcpy.AddField_management("%s\\stats_fema_ndmc" % the_work_gdb, "F_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_fema_nidis" % the_work_gdb, "F_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_fema_ndmc" % the_work_gdb, "F_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_fema_nidis" % the_work_gdb, "F_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field FEMA Area and Population
        arcpy.CalculateField_management("%s\\stats_fema_ndmc" % the_work_gdb, "F_A_Prct", "( !SUM_AREA!/ !MAX_FemaRgn_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_fema_nidis" % the_work_gdb, "F_A_Prct", "( !SUM_AREA!/ !MAX_FemaRgn_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_fema_ndmc" % the_work_gdb, "F_P_Prct", "( !SUM_Cnty_P!/ !MAX_FemaRgn_Pop_2010!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_fema_nidis" % the_work_gdb, "F_P_Prct", "( !SUM_Cnty_P!/ !MAX_FemaRgn_Pop_2010!)*100", "PYTHON", "")
        print "FEMA regions statistics tabulated"
        #log.write("FEMA regions statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("FEMA regions statistics taubuation error: " + e.message +"\n")
        #log_e.close()
        
##    try:
##        #################### RCC Processing
##        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_rcc_ndmc" % the_work_gdb, "AREA SUM;Cnty_P SUM;A_RCC MAX;P_RCC MAX", "DM;RCC_ID")
##        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_rcc_nidis" % the_work_gdb, "AREA SUM;Cnty_P SUM;A_RCC MAX;P_RCC MAX", "DM;RCC_ID")
##        # Process: Add Field RCC Area and Population
##        arcpy.AddField_management("%s\\stats_rcc_ndmc" % the_work_gdb, "R_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_rcc_nidis" % the_work_gdb, "R_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_rcc_ndmc" % the_work_gdb, "R_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_rcc_nidis" % the_work_gdb, "R_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        # Process: Calculate Field RCC Area and Population
##        arcpy.CalculateField_management("%s\\stats_rcc_ndmc" % the_work_gdb, "R_A_Prct", "( !SUM_AREA!/ !MAX_A_RCC!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_rcc_nidis" % the_work_gdb, "R_A_Prct", "( !SUM_AREA!/ !MAX_A_RCC!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_rcc_ndmc" % the_work_gdb, "R_P_Prct", "( !SUM_Cnty_P!/ !MAX_P_RCC!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_rcc_nidis" % the_work_gdb, "R_P_Prct", "( !SUM_Cnty_P!/ !MAX_P_RCC!)*100", "PYTHON", "")
##        print "RCC statistics tabulated"
##        #################### Display Region Processing
##        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_disp_rgn_ndmc" % the_work_gdb, "AREA SUM;Cnty_P SUM;A_DIS_RGN MAX;P_DIS_RGN MAX", "DM;DISP_RGN_ID")
##        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_disp_rgn_nidis" % the_work_gdb, "AREA SUM;Cnty_P SUM;A_DIS_RGN MAX;P_DIS_RGN MAX", "DM;DISP_RGN_ID")
##        # Process: Add Field RCC Area and Population
##        arcpy.AddField_management("%s\\stats_disp_rgn_ndmc" % the_work_gdb, "D_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_disp_rgn_nidis" % the_work_gdb, "D_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_disp_rgn_ndmc" % the_work_gdb, "D_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        arcpy.AddField_management("%s\\stats_disp_rgn_nidis" % the_work_gdb, "D_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
##        # Process: Calculate Field RCC Area and Population
##        arcpy.CalculateField_management("%s\\stats_disp_rgn_ndmc" % the_work_gdb, "D_A_Prct", "( !SUM_AREA!/ !MAX_A_DIS_RGN!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_disp_rgn_nidis" % the_work_gdb, "D_A_Prct", "( !SUM_AREA!/ !MAX_A_DIS_RGN!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_disp_rgn_ndmc" % the_work_gdb, "D_P_Prct", "( !SUM_Cnty_P!/ !MAX_P_DIS_RGN!)*100", "PYTHON", "")
##        arcpy.CalculateField_management("%s\\stats_disp_rgn_nidis" % the_work_gdb, "D_P_Prct", "( !SUM_Cnty_P!/ !MAX_P_DIS_RGN!)*100", "PYTHON", "")
##        print "Display Region statistics tabulated"
##        log.write("Display regions statistics tabulated\n")
##        
##    except Exception as e:
##        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
##        print e.message
##        log_e = open(log_dir + "StatsErrors.log",'a')
##        log_e.write("Display regions statistics taubuation error: " + e.message +"\n")
##        log_e.close()

    try:    
        #################### CONUS Processing
        # Process: Summary Conus
        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_US_c_ndmc" % the_work_gdb, "AREA SUM;Cnty_P SUM;Conus_Area_Mi MAX;Conus_Pop_2010 MAX", "DM;ISCONUS")
        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_US_c_nidis" % the_work_gdb, "AREA SUM;Cnty_P SUM;Conus_Area_Mi MAX;Conus_Pop_2010 MAX", "DM;ISCONUS")
        # Process: Add Field CONUS Area and Population
        arcpy.AddField_management("%s\\stats_US_c_ndmc" % the_work_gdb, "C_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_c_nidis" % the_work_gdb, "C_A_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_c_ndmc" % the_work_gdb, "C_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_c_nidis" % the_work_gdb, "C_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field CONUS Area and Population
        arcpy.CalculateField_management("%s\\stats_US_c_ndmc" % the_work_gdb, "C_A_Prct", "( !SUM_AREA!/ !MAX_Conus_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_c_nidis" % the_work_gdb, "C_A_Prct", "( !SUM_AREA!/ !MAX_Conus_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_c_ndmc" % the_work_gdb, "C_P_Prct", "( !SUM_Cnty_P!/ !MAX_Conus_Pop_2010!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_c_nidis" % the_work_gdb, "C_P_Prct", "( !SUM_Cnty_P!/ !MAX_Conus_Pop_2010!)*100", "PYTHON", "")
        print "CONUS statistics tabulated"
        #log.write("CONUS statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("CONUS statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    try:        
        #################### Total US Processing
        # Process: Summary Total
        arcpy.Statistics_analysis("%s\\stats_county_ndmc" % the_work_gdb, "%s\\stats_US_t_ndmc" % the_work_gdb, "AREA SUM;TotalUs_Area_Mi MAX;Cnty_P SUM;TotalUs_Pop_2010 MAX", "DM;ISTOTAL")
        arcpy.Statistics_analysis("%s\\stats_county_nidis" % the_work_gdb, "%s\\stats_US_t_nidis" % the_work_gdb, "AREA SUM;TotalUs_Area_Mi MAX;Cnty_P SUM;TotalUs_Pop_2010 MAX", "DM;ISTOTAL")
        # Process: Add Field Total Area and Population
        arcpy.AddField_management("%s\\stats_US_t_ndmc" % the_work_gdb, "T_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_t_nidis" % the_work_gdb, "T_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_t_ndmc" % the_work_gdb, "T_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_US_t_nidis" % the_work_gdb, "T_P_prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field Total Area and Population
        arcpy.CalculateField_management("%s\\stats_US_t_ndmc" % the_work_gdb, "T_A_Prct", "(!SUM_AREA!/ !MAX_TotalUs_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_t_nidis" % the_work_gdb, "T_A_Prct", "(!SUM_AREA!/ !MAX_TotalUs_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_t_ndmc" % the_work_gdb, "T_P_Prct", "(!SUM_Cnty_P!/ !MAX_TotalUs_Pop_2010!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_US_t_nidis" % the_work_gdb, "T_P_Prct", "(!SUM_Cnty_P!/ !MAX_TotalUs_Pop_2010!)*100", "PYTHON", "")
        print "Total US statistics tabulated"
        #log.write("Total US statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Total US statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def regions(the_work_gdb,regions, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        ###     Regions
        arcpy.TabulateIntersection_analysis(regions,"Region_Area_Mi;RgnId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_region_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(regions,"Region_Area_Mi;RgnId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_region_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Custom Regions statistics tabulated"
        #log.write("Custom Regions statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Custom Regions statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()
    
def climdiv(the_work_gdb,climdiv, log_dir, log_file):

    #log = open(log_dir + log_file,'a')

    try:
        ###     Climate Divisions
        arcpy.TabulateIntersection_analysis(climdiv,"Climdiv_Area_Mi;ClimDivId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_climdiv_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(climdiv,"Climdiv_Area_Mi;ClimDivId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_climdiv_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Climate Division statistics tabulated"
        #log.write("Climate Division statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Climate Division statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()
    
def urban(the_work_gdb,urban, log_dir, log_file):

    #log = open(log_dir + log_file,'a')

    try:
        ###     Urban
        arcpy.TabulateIntersection_analysis(urban,"GEOID10;Urban_Area_Mi", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_urban_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(urban,"GEOID10;Urban_Area_Mi", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_urban_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Urban Areas statistics tabulated"
        #log.write("Urban Areas statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Urban Areas statistics taubuation error: " + e.message +"\n")
        #log_e.close()    

    #log.close()

def wfo(the_work_gdb,wfo, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        ###     NWS WFO's
        arcpy.TabulateIntersection_analysis(wfo,"wfo;Nws_Wfo_Area_Mi;NWS_rgn;Nws_Rgn_Area_Mi", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_wfo_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(wfo,"wfo;Nws_Wfo_Area_Mi;NWS_rgn;Nws_Rgn_Area_Mi", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_wfo_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        #################### WFO Processing
        # Process: Summary NWS Regions
        arcpy.Statistics_analysis("%s\\stats_wfo_ndmc" % the_work_gdb, "%s\\stats_nws_ndmc" % the_work_gdb, "AREA SUM;Nws_Rgn_Area_Mi MAX", "DM;NWS_rgn")
        arcpy.Statistics_analysis("%s\\stats_wfo_nidis" % the_work_gdb, "%s\\stats_nws_nidis" % the_work_gdb, "AREA SUM;Nws_Rgn_Area_Mi MAX", "DM;NWS_rgn")
        # Process: Add Field NWS Area and Population
        arcpy.AddField_management("%s\\stats_nws_ndmc" % the_work_gdb, "N_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_nws_nidis" % the_work_gdb, "N_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field NWS Area and Population
        arcpy.CalculateField_management("%s\\stats_nws_ndmc" % the_work_gdb, "N_A_Prct", "(!SUM_AREA!/ !MAX_Nws_Rgn_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_nws_nidis" % the_work_gdb, "N_A_Prct", "(!SUM_AREA!/ !MAX_Nws_Rgn_Area_Mi!)*100", "PYTHON", "")
        print "Weather Forecast Office statistics tabulated"
        #log.write("Weather Forecast Office statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Weather Forecast Office statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def usace(the_work_gdb,usace, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        ###     USACE
        arcpy.TabulateIntersection_analysis(usace,"SYMBOL;DIV_SYM;Usace_Dist_Area_Mi;Usace_Div_Area_Mi", "%s\\usdm_NDMC_M" % the_work_gdb
                                            , "%s\\stats_district_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(usace,"SYMBOL;DIV_SYM;Usace_Dist_Area_Mi;Usace_Div_Area_Mi", "%s\\usdm_NIDIS_M" % the_work_gdb
                                            , "%s\\stats_district_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        ###################### USACE Processing
        # Process: Summary USACE Division
        arcpy.Statistics_analysis("%s\\stats_district_ndmc" % the_work_gdb, "%s\\stats_division_ndmc" % the_work_gdb, "AREA SUM;Usace_Div_Area_Mi MAX", "DM;DIV_SYM")
        arcpy.Statistics_analysis("%s\\stats_district_nidis" % the_work_gdb, "%s\\stats_division_nidis" % the_work_gdb, "AREA SUM;Usace_Div_Area_Mi MAX", "DM;DIV_SYM")
        # Process: Add Field USACE Division
        arcpy.AddField_management("%s\\stats_division_ndmc" % the_work_gdb, "DV_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("%s\\stats_division_nidis" % the_work_gdb, "DV_A_Prct", "DOUBLE", "3", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "USACE District statistics tabulated"
        #log.write("USACE District statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("USACE District statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    try:        
        # Process: Calculate Field USACE Division
        arcpy.CalculateField_management("%s\\stats_division_ndmc" % the_work_gdb, "DV_A_Prct", "(!SUM_AREA!/ !MAX_Usace_Div_Area_Mi!)*100", "PYTHON", "")
        arcpy.CalculateField_management("%s\\stats_division_nidis" % the_work_gdb, "DV_A_Prct", "(!SUM_AREA!/ !MAX_Usace_Div_Area_Mi!)*100", "PYTHON", "")
        print "USACE Division statistics tabulated"
        #log.write("USACE Division statistics tabulated\n")
        
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("USACE Division statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def huc2(the_work_gdb,huc2, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        arcpy.TabulateIntersection_analysis(huc2,"HUC2", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_huc2_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(huc2,"HUC2", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_huc2_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "HUC 2 statistics tabulated"
        #log.write("HUC 2 statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("HUC 2 statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()
    
def huc4(the_work_gdb,huc4, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        arcpy.TabulateIntersection_analysis(huc4,"HUC4", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_huc4_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(huc4,"HUC4", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_huc4_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "HUC 4 statistics tabulated"
        #log.write("HUC 4 statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("HUC 4 statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def huc6(the_work_gdb,huc6, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        now = datetime.datetime.now()
        print "HUC6 begin: %s" % str(now)
        arcpy.TabulateIntersection_analysis(huc6,"HUC6", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_huc6_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(huc6,"HUC6", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_huc6_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "HUC 6 statistics tabulated"
        now = datetime.datetime.now()
        print "HUC 6 end: %s" % str(now)
        #log.write("HUC 6 statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("HUC 6 statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def huc8(the_work_gdb,huc8, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        now = datetime.datetime.now()
        print "HUC8 begin: %s" % str(now)
        arcpy.TabulateIntersection_analysis(huc8, "HUC8", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_huc8_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(huc8, "HUC8", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_huc8_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "HUC 8 statistics tabulated"
        now = datetime.datetime.now()
        print "HUC 8 end: %s" % str(now)
        #log.write("HUC 8 statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("HUC 8 statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def rfc(the_work_gdb,rfc, log_dir, log_file):

    #log = open(log_dir + log_file,'a')

    try:    
        # Process: Summary RFC
        arcpy.TabulateIntersection_analysis(rfc,"RfcId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_rfc_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(rfc,"RfcId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_rfc_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "River Forecast Centers statistics tabulated"
        #log.write("River Forecast Centers statistics tabulated\n")        

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("River Forecast Centers statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def rdews(the_work_gdb,rdews, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
        # Process: Summary RDEWS
        arcpy.TabulateIntersection_analysis(rdews,"rdewsID", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_rdews_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(rdews,"rdewsID", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_rdews_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "RDEWS statistics tabulated"
        #log.write("RDEWS statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("RDEWS statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()    

def chubs(the_work_gdb,chubs, log_dir, log_file):

    #log = open(log_dir + log_file,'a')

    try:

        arcpy.TabulateIntersection_analysis(chubs,"HubId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_chubs_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(chubs,"HubId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_chubs_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Climate Hubs statistics tabulated"
        #log.write("Climate Hubs statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Climate Hubs statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()     

def substate(the_work_gdb,substate, log_dir, log_file):

    #log = open(log_dir + log_file,'a')

    try:
    
        arcpy.TabulateIntersection_analysis(substate,"SubStateId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_substate_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(substate,"SubStateId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_substate_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Sub State statistics tabulated"
        #log.write("Sub State statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Sub State statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def tribal(the_work_gdb, tribal, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
    
        arcpy.TabulateIntersection_analysis(tribal,"GEOID", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_tribal_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(tribal,"GEOID", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_tribal_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Tribal statistics tabulated"
        #log.write("Tribal statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Tribal statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()

def dregion(the_work_gdb, dregion, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
    
        arcpy.TabulateIntersection_analysis(dregion,"DispRgnId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_disp_rgn_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(dregion,"DispRgnId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_disp_rgn_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "Geographic region statistics tabulated"
        #log.write("Geographic region statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("Geographic region statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()
    
def rcc(the_work_gdb, rcc, log_dir, log_file):

    #log = open(log_dir + log_file,'a')
    
    try:
    
        arcpy.TabulateIntersection_analysis(rcc,"RccId", "%s\\usdm_NDMC_M" % the_work_gdb, "%s\\stats_rcc_ndmc" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        arcpy.TabulateIntersection_analysis(rcc,"RccId", "%s\\usdm_NIDIS_M" % the_work_gdb, "%s\\stats_rcc_nidis" % the_work_gdb, "DM", "", "", "SQUARE_MILES")
        print "RCC statistics tabulated"
        #log.write("RCC statistics tabulated\n")

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        print e.message
        #log_e = open(log_dir + "StatsErrors.log",'a')
        #log_e.write("RCC statistics taubuation error: " + e.message +"\n")
        #log_e.close()

    #log.close()
