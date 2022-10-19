'''
Geog777 Project 1, Fall 2022
Cherie Bryant
runAnalysis.py - arcpy analysis to implement tKinter interface
'''

import arcpy

##################################
# SET WORKSPACE & OTHER NEEDED PATHS
##################################
# set workspace
arcpy.env.workspace = r"C:\Users\cheri\Documents\ArcGIS\Projects\Geog777_Project1\Geog777_Project1.gdb"

# set directory for png's of layouts
resultsFolder = r"C:\Users\cheri\Documents\geog777\Project1\Project1Files\images"

# create object for ArcGIS Pro project to access & update maps & layouts 
# with new data. Have to state the full path as the mp method doesn't 
# recognize the workspace
projectPath = r"C:\Users\cheri\Documents\ArcGIS\Projects\Geog777_Project1\Geog777_Project1.aprx"
aprx = arcpy.mp.ArcGISProject(projectPath)

# tell python it's OK to overwrite previous versions of layers & feature classes
arcpy.env.overwriteOutput = True


##################################
# FUNCTIONS
##################################
def idw(wells, counties, k):
    '''Interpolate Nitrate Data using Inverse Distance Weighting to get a surface'''
    # SET VARIABLES TO HOLD TOOL PARAMETERS
    inFC = wells
    z_field = "nitr_ran"
    power = k
    idwFCpath = f'idwWellNit_{str(k).replace(".", "_")}'

    # RUN IDW tool WITH COUNTIES SET AS MASK IN THE ENVIRONMENT
    with arcpy.EnvManager(extent=counties, mask=counties, overwriteOutput=True):
        output = arcpy.sa.Idw(inFC, z_field, power=power)
        output.save(idwFCpath)

    # UPDATE THE DATASOURCE FOR THE MAP IN THE PRO PROJECT
    # create map object
    idwMap = aprx.listMaps("IDW")[0] 
    # create layer object
    idwLayer = idwMap.listLayers("IDW_Well_Nitrates")[0] 
    # examine old datasource
    print("old datasource =" + str(idwLayer.dataSource)) 
    # access connection properties
    idwCP = idwLayer.connectionProperties 
    # update path for new data
    idwCP['dataset'] = idwFCpath 
    # set new connection properties
    idwLayer.updateConnectionProperties(idwLayer.connectionProperties, idwCP) 
    # examine to verify it was changed
    print("new datasource =" + str(idwLayer.dataSource)) 

    # UPDATE THE TITLE ON THE IDW LAYOUT
    # create layout object
    idw_LO = aprx.listLayouts("idwWellNit_LO")[0]
    # create title object
    idwTitle = idw_LO.listElements('TEXT_ELEMENT', 'idwTitle')[0]
    # check old title
    print("old title=" + idwTitle.text)
    # set new title 
    idwTitle.text = f"Inverse Distance Weighting for a K value of {str(k)}" 
    # test to see if it changed
    print("new title=" + idwTitle.text) 

    # SAVE LAYOUT FOR DISPLAY & DOWNLOAD
    idw_LO.exportToPNG(f"{resultsFolder}\IDW_{k}.png")

    # SAVE THE OVERALL MAP & LAYOUT CHANGES TO THE PROJECT
    aprx.save()

    # VERIFY IN TERMINAL THE PROCESS RAN
    print('The idw function ran correctly with a k-value of: ' + str(k) +'.')

    return idwFCpath

def zonalStats(tracts, idwResults, k):
    '''Find mean nitrates per census tracts'''
    # SET VARIABLES FOR TOOL PARAMETERS
    in_zone_data = tracts
    zone_field = "GEOID10"
    in_value_raster = idwResults
    statsTable = f"statsTable_{str(k).replace('.', '_')}"

    # RUN TOOL
    arcpy.sa.ZonalStatisticsAsTable(in_zone_data, zone_field, in_value_raster, statsTable, statistics_type="MEAN")

    print('The zonalStats function ran correctly for a k-value of: ' + str(k) +'.')

    """ join statsTable to tracts so the Mean Nitrate field & calculate new fields for Mean & FID so Mean can easily be used in the OLS regression as a dependent variable; FIDint is copied from FID but as an integer as that's the imput type required by OLS"""

    # SET VARIABLES FOR PROCESS PARAMETERS    
    inFC = tracts
    tempLyr = "tempTractLayer"
    newField1 = "meanNit"
    joinTable = statsTable
    joinField = "GEOID10"
    dropField = f"meanNit{str(k).replace('.', '_')}"
    tracts_MeanNit = f"tractsMeanNit_{str(k).replace('.', '_')}"
    calcExpression1 = f"!{joinTable}.MEAN!"

    # MAKE JOIN, CALCULATE FIELDS, & REMOVE JOIN
    # Add a new field: meanNit
    arcpy.management.AddField(inFC, newField1, "DOUBLE")
    # make an in memory layer 
    arcpy.management.MakeFeatureLayer(inFC, tempLyr)                 
    # Join the feature layer to a table
    arcpy.management.AddJoin(tempLyr, joinField, joinTable, joinField)     
    # Populate the newly created field with values from the joined table
    arcpy.management.CalculateField(tempLyr, newField1, calcExpression1, "PYTHON")     
    # Remove the join
    arcpy.management.RemoveJoin(tempLyr, statsTable)
    # Save the in memory layer to a permanent feature class 
    arcpy.management.CopyFeatures(tempLyr, tracts_MeanNit)
    # Drop the newly created meanNit field from the original tract data
    arcpy.management.DeleteField(inFC, dropField)

    print('The join & new fields ran correctly.')

    return tracts_MeanNit

def ols(tracts_MeanNit, k):
    '''Run Ordinary Least Squares linear regression to see if there is a relationship'''
    # SET VARIABLES FOR TOOL PARAMETERS
    input_fc = tracts_MeanNit
    unique_id_field = "FIDint"
    olsFCpath = f"ols_{str(k).replace('.', '_')}"
    depend_var = "canrate"
    explan_var = "meanNit"
    olsReport = f"{resultsFolder}/olsReport_{k}.pdf"

    # RUN TOOL
    arcpy.stats.OrdinaryLeastSquares(input_fc, unique_id_field, olsFCpath, depend_var, explan_var, Output_Report_File=olsReport)

    # UPDATE THE DATASOURCE FOR THE MAP IN THE PRO PROJECT
    # create map object
    olsMap = aprx.listMaps("OLS")[0] 
    # create layer object
    olsLayer = olsMap.listLayers("OrdinaryLeastSquares")[0] 
    # examine old datasource
    print("old datasource =" + str(olsLayer.dataSource))
    # access connection properties
    olsCP = olsLayer.connectionProperties 
    # update path for new data
    olsCP['dataset'] = olsFCpath 
    # update datasource
    olsLayer.updateConnectionProperties(olsLayer.connectionProperties, olsCP) 
    
    print("new datasource =" + str(olsLayer.dataSource))

    # UPDATE THE TITLE ON THE IDW LAYOUT
    #create layout object
    ols_LO = aprx.listLayouts("OLS_LO")[0] 
    #create title object
    olsTitle = ols_LO.listElements('TEXT_ELEMENT', 'olsTitle')[0] 
    # examine old text
    print("old title=" + olsTitle.text)
    #set new text
    olsTitle.text = f"Ordinary Least Squares for a k-value of {str(k)}"
    # examine to verify it was changed
    print("new title=" + olsTitle.text)

    # SAVE LAYOUT FOR DISPLAY & DOWNLOAD
    ols_LO.exportToPNG(f"{resultsFolder}\OLS_{k}.png")

    # SAVE THE OVERALL MAP & LAYOUT CHANGES TO THE PROJECT
    aprx.save()

    print('The ols function ran correctly k-value of: ' + str(k) +'.')

    return olsFCpath

def morans (olsFC, k):
    '''Use Moran's I Autocorrelation to validate the linear regression'''
    # SET VARIABLES FOR TOOL PARAMETERS
    input_fc2 = olsFC
    input_field = "StdResid"

    # RUN TOOL
    morans = arcpy.stats.SpatialAutocorrelation(input_fc2, input_field, 'GENERATE_REPORT', 'INVERSE_DISTANCE', 'EUCLIDEAN_DISTANCE', 'ROW')

    # SET VARIABLE TO HOLD HTML REPORT PATH
    moranReport = morans.getOutput(3)

    print('The morans function ran correctly with a k-value of: ' + str(k) +'.')

    return moranReport

