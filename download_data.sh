#!/bin/bash

# Function to download a file only if it does not already exist
download_file() {
    local url=$1
    local output=$2

    if [ -f "$output" ]; then
        echo "File $output already exists, skipping download."
    else
        echo "Downloading from $url..."
        if [ -z "$output" ]; then
            wget --progress=bar:force "$url"
        else
            wget --progress=bar:force "$url" -O "$output"
        fi
    fi
}

# Function to rename directories with spaces to underscores recursively
rename_with_underscores() {
    local target_dir=$1
    find "$target_dir" -depth -name "* *" | while read -r name; do
        newname=$(dirname "$name")/$(basename "$name" | tr ' ' '_')
        if [ "$name" != "$newname" ]; then
            mv "$name" "$newname"
        fi
    done
}

# Function to unzip and recursively handle zip files in subdirectories
unzip_file() {
    local file=$1
    local directory=$2

    if [ -d "$directory" ]; then
        echo "Directory $directory already exists, skipping initial unzip."
    else
        if [ -f "$file" ]; then
            echo "Unzipping $file to $directory..."
            unzip -o "$file" -d "$directory"
            rename_with_underscores "$directory"
        else
            echo "File $file does not exist, skipping unzip."
            return
        fi
    fi

    # Recursively find and unzip zip files in the directory
    find "$directory" -type f -name "*.zip" | while read -r zipfile; do
        subdir="${zipfile%.zip}"  # Create a subdirectory with the zip file name (without .zip)
        if [ -d "$subdir" ]; then
            echo "Directory $subdir already exists, skipping unzip of $zipfile."
        else
            echo "Unzipping $zipfile to $subdir..."
            unzip -o "$zipfile" -d "$subdir"
            rename_with_underscores "$subdir"
        fi
    done
}



# Change to the data directory
cd data

##### FAF5 Regions ####
## from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-regions
#download_file "https://stg-arcgisazurecdataprod.az.arcgis.com/exportfiles-273-10162/NTAD_Freight_Analysis_Framework_Regions_-8678979836664102029.zip" "FAF5_regions.zip"
#unzip_file "FAF5_regions.zip" "FAF5_regions"
#######################
#
#### FAF5 Network Links ####
# from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links
download_file "https://stg-arcgisazurecdataprod.az.arcgis.com/exportfiles-273-10164/NTAD_Freight_Analysis_Framework_Network_Links_-2286167086800774353.zip" "FAF5_network_links.zip"
unzip_file "FAF5_network_links.zip" "FAF5_network_links"
#############################
#
##### FAF5 Highway Network Assignments ####
## from https://ops.fhwa.dot.gov/freight/freight_analysis/faf/
#mkdir -p FAF5_Highway_Assignment_Results
#cd FAF5_Highway_Assignment_Results
#download_file "https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2017_HighwayAssignmentResults_04_07_2022.zip" "FAF5_2017_HighwayAssignmentResults.zip"
#unzip_file "FAF5_2017_HighwayAssignmentResults.zip" "FAF5_2017_Highway_Assignment_Results"
#
#download_file "https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2022_HighwayAssignmentResults_04_07_2022.zip" "FAF5_2022_HighwayAssignmentResults.zip"
#unzip_file "FAF5_2022_HighwayAssignmentResults.zip" "FAF5_2022_Highway_Assignment_Results"
#
#download_file "https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2050_HighwayAssignmentResults_09_17_2022.zip" "FAF5_2050_HighwayAssignmentResults.zip"
#unzip_file "FAF5_2050_HighwayAssignmentResults.zip" "FAF5_2050_Highway_Assignment_Results"
#cd ..
###########################################
#
##### FAF5 regional database ####
## FAF5 regional database of tonnage and value by origin-destination pair, commodity type, and mode from 2018-2022 (from https://www.bts.gov/faf)
#download_file "https://faf.ornl.gov/faf5/data/download_files/FAF5.5.1_2018-2022.zip" "FAF5_regional_od.zip"
#unzip_file "FAF5_regional_od.zip" "FAF5_regional_flows_origin_destination"
#################################
#
##### Vehicle Inventory and Use Survey (VIUS) data ####
## from https://www.bts.gov/faf
#download_file "https://rosap.ntl.bts.gov/view/dot/42632/dot_42632_DS2.zip" "VIUS_2002.zip"
#unzip_file "VIUS_2002.zip" "VIUS_2002"
#######################################################
#
##### Subregions for eGRID grid intensity data ####
## from https://www.epa.gov/egrid/egrid-mapping-files
#download_file "https://www.epa.gov/system/files/other-files/2024-05/egrid2022_subregions_shapefile.zip" "eGRID2022_subregions_shapefile.zip"
#unzip_file "eGRID2022_subregions_shapefile.zip" "eGRID2022_subregions"
###################################################
#
##### eGRID grid intensity data ####
## from https://www.epa.gov/egrid/download-data
#download_file "https://www.epa.gov/system/files/documents/2024-01/egrid2022_data.xlsx" "egrid2022_data.xlsx"
####################################
#
##### EIA grid emission intensity by state ####
## from https://www.eia.gov/electricity/data/emissions/
#download_file "https://www.eia.gov/electricity/data/emissions/xls/emissions_region2022.xlsx" "emissions_region2022.xlsx"
###############################################
#
##### EIA net summer capacity by state (MW) ####
## from https://www.eia.gov/electricity/data/state/
#download_file "https://www.eia.gov/electricity/data/state/existcapacity_annual.xlsx" "existcapacity_annual.xlsx"
################################################
#
##### EIA proposed additions to net summer capacity by state: 2023-2027 (MW) ####
## from https://www.eia.gov/electricity/data/state/
#download_file "https://www.eia.gov/electricity/data/state/plancapacity_annual.xlsx" "plancapacity_annual.xlsx"
#################################################################################
#
##### EIA net annual generation by state (MWh) ####
## from https://www.eia.gov/electricity/annual/
#download_file "https://www.eia.gov/electricity/data/state/annual_generation_state.xls" "annual_generation_state.xls"
###################################################
#
##### US zip code boundaries ####
## from https://hub.arcgis.com/datasets/d6f7ee6129e241cc9b6f75978e47128b
#download_file "https://opendata.arcgis.com/api/v3/datasets/d6f7ee6129e241cc9b6f75978e47128b_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" "zip_code_regions.zip"
#unzip_file "zip_code_regions.zip" "zip_code_regions"
#################################
#
##### US state boundaries ####
## from https://www.sciencebase.gov/catalog/item/52c78623e4b060b9ebca5be5
#download_file "https://www.sciencebase.gov/catalog/file/get/52c78623e4b060b9ebca5be5?facet=tl_2012_us_state" "state_boundaries.zip"
#unzip_file "state_boundaries.zip" "state_boundaries"
##############################
#
##### Electricity rate data per state ####
## from https://www.eia.gov/electricity/data.php
#mkdir -p electricity_rates
#download_file "https://www.eia.gov/electricity/data/state/sales_annual_a.xlsx" "electricity_rates/sales_annual_a.xlsx"
##########################################
#
##### Electricity rate data per zip code ####
## from https://catalog.data.gov/dataset/u-s-electric-utility-companies-and-rates-look-up-by-zipcode-2020
#download_file "https://data.openei.org/files/5650/iou_zipcodes_2020.csv" "electricity_rates/iou_zipcodes_2020.csv"
#############################################
#
##### Maximum demand charge data (compiled by NREL in 2017) ####
## from https://data.nrel.gov/submissions/74
#download_file "https://data.nrel.gov/system/files/74/Demand%20charge%20rate%20data.xlsm" "Demand_charge_rate_data.xlsm"
################################################################
#
##### Electricity utility boundaries ####
## from https://atlas.eia.gov/datasets/f4cd55044b924fed9bc8b64022966097_0
#download_file "https://opendata.arcgis.com/api/v3/datasets/f4cd55044b924fed9bc8b64022966097_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" "utility_boundaries.zip"
#unzip_file "utility_boundaries.zip" "utility_boundaries"
#########################################
#
##### Electricity balancing authority boundaries ####
## from https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::electric-planning-areas/about
#download_file "https://opendata.arcgis.com/api/v3/datasets/7d35521e3b2c48ab8048330e14a4d2d1_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" "balancing_authority_boundaries.zip"
#unzip_file "balancing_authority_boundaries.zip" "balancing_authority_boundaries"
#####################################################
#
##### Power demand by balancing authority ####
## from https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48
#mkdir -p power_demand_by_balancing_authority
#download_file "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jul_Dec.csv" "power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jul_Dec.csv"
#download_file "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jan_Jun.csv" "power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jan_Jun.csv"
##############################################
#
##### Power demand by state ####
## from https://www.eia.gov/electricity/data/state/
#download_file "https://www.eia.gov/electricity/data/state/existcapacity_annual.xlsx" "existcapacity_annual.xlsx"
################################
#
##### U.S. Primary Roads National Shapefile ####
## from https://catalog.data.gov/dataset/tiger-line-shapefile-2019-nation-u-s-primary-roads-national-shapefile
#download_file "https://www2.census.gov/geo/tiger/TIGER2019/PRIMARYROADS/tl_2019_us_primaryroads.zip" "tl_2019_us_primaryroads.zip"
#unzip_file "tl_2019_us_primaryroads.zip" "tl_2019_us_primaryroads"
################################################
#
##### Bay area county boundaries ####
## from https://geodata.lib.berkeley.edu/catalog/ark28722-s7hs4j
#download_file "https://spatial.lib.berkeley.edu/public/ark28722-s7hs4j/data.zip" "bay_area_counties_data.zip"
#unzip_file "bay_area_counties_data.zip" "bay_area_counties"
#####################################
#
##### Counties in Utah ####
## from https://gis.utah.gov/products/sgid/boundaries/county/
#download_file "https://opendata.arcgis.com/datasets/90431cac2f9f49f4bcf1505419583753_0.zip" "utah_counties.zip"
#unzip_file "utah_counties.zip" "utah_counties"
###########################
#
##### Truck stop parking data ####
## from https://geodata.bts.gov/datasets/usdot::truck-stop-parking
#download_file "https://stg-arcgisazurecdataprod.az.arcgis.com/exportfiles-273-10043/NTAD_Truck_Stop_Parking_-2623767270591943357.zip" "Truck_Stop_Parking.zip"
#unzip_file "Truck_Stop_Parking.zip" "Truck_Stop_Parking"
##################################
#
##### US power industry report for 2017 ####
## from https://www.eia.gov/electricity/data/eia861/
#download_file "https://www.eia.gov/electricity/data/eia861/archive/zip/f8612017.zip" "US_Power_Industry_Report_2017.zip"
#unzip_file "US_Power_Industry_Report_2017.zip" "US_Power_Industry_Report_2017"
#mv US_Power_Industry_Report_2017/Utility_Data_2017.xlsx .
############################################
#
##### Diesel price by state, averaged over the last 5 years ####
## from https://github.com/mcsc-impact-climate/Green_Trucking_Analysis
#download_file "https://raw.githubusercontent.com/mcsc-impact-climate/Green_Trucking_Analysis/main/tables/average_diesel_price_by_state.csv" "average_diesel_price_by_state.csv"
################################################################
#
##### 2023-24 hourly load data for the Texas grid (ERCOT) ####
## from https://www.ercot.com/gridinfo/load/load_hist
#download_file "https://www.ercot.com/files/docs/2023/02/09/Native_Load_2023.zip" "Native_Load_2023.zip"
#unzip_file "Native_Load_2023.zip" "Native_Load_2023"
#download_file "https://www.ercot.com/files/docs/2024/02/06/Native_Load_2024.zip" "Native_Load_2024.zip"
#unzip_file "Native_Load_2024.zip" "Native_Load_2024"
##############################################################
#
##### geojson file with the geospatial regions covered by ElectricityMaps ####
## Open Database License (https://opendatacommons.org/licenses/odbl/)
## Attribution: ElectricityMaps (website: https://www.electricitymaps.com/data-portal. GitHub: https://github.com/electricitymaps/electricitymaps-contrib)
#download_file https://raw.githubusercontent.com/electricitymaps/electricitymaps-contrib/master/web/geo/world.geojson

#download_file https://driveelectric.gov/files/zef-gis-files.zip
#unzip_file zef-gis-files.zip zef-gis-files

# Change back to the original directory
cd ..


