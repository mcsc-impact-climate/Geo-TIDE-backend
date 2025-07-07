#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Apr 8 22:08:00 2023

@author: danikam
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from CommonTools import get_top_dir, saveShapefile

METERS_PER_MILE = 1609.34


def mergeShapefile(dest, shapefile_path, min_tonnage=None, road_class=None):
    """
    Reads in the shapefile containing the highway links, and merges it with the highway flux assignments

    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing the highway links

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    min_tonnage (float or None): Minimum annual tons per link required to save the link to the output shapefile (if None, no filter applied)

    road_class (string or None): Road class to filter for (if None, no filter applied)

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    """

    print("Reading in shapefile")

    shapefile = gpd.read_file(
        shapefile_path, columns=["ID", "geometry", "Class", "STATE", "LENGTH", "Road_Name"]
    )
    print(shapefile.columns)
    print("Shapefile has been read in")

    cClass = np.ones(len(shapefile), dtype=bool)
    if road_class is not None:
        cClass = (
            cClass & (~(shapefile["Class"].isna())) & (shapefile["Class"] == road_class)
        )
    shapefile = shapefile[cClass]

    # Evaluate the length in miles. Original units are meters
    shapefile["len_miles"] = shapefile["LENGTH"]

    # Capitalize the ID column to ensure compatibility with the highway assignments
    # shapefile = shapefile.rename(columns={'id': 'ID'})

    # Merge the shapefile with the highway assignments
    print("Merging the shapefile")
    merged_dataframe = shapefile.merge(dest, on="ID", how="left")

    #    # Convert to tons per mile
    #    merged_dataframe['TOT Tons_22 All'] = merged_dataframe['TOT Tons_22 All'] / merged_dataframe['ShapeSTLen']

    # Filter for links above a given tonnage and/or on a given road class
    cFilter = np.ones(len(merged_dataframe), dtype=bool)
    if min_tonnage is not None:
        cFilter = (
            cFilter
            & (~(merged_dataframe["Tot Tons"].isna()))
            & (merged_dataframe["Tot Tons"] > min_tonnage)
        )
    merged_dataframe = merged_dataframe[cFilter].drop(columns=["ID", "Class", "LENGTH"])

    return merged_dataframe


def read_highway_assignments(top_dir, unit_type="All", include_trips=True):
    """
    Reads in the FAF5 highway assignments as a dataframe, and gets the columns of interest

    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    unit_type (string): Type of truck unit. SU: Single unit. CU: Combined unit.
    include_trips (boolean): Indicates whether or not to include total trips in addition to tons

    Returns
    -------
    highway_assignments_filtered_df (pd.DataFrame): Dataframe containing the highway link IDs and any other columns of interest
    """

    highway_assignment_modifier = ""
    if unit_type == "SU":
        highway_assignment_modifier = "SU "
    elif unit_type == "CU":
        highway_assignment_modifier = "CU "

    highway_assignments_df = pd.read_csv(
        f"{top_dir}/data/FAF5_Highway_Assignment_Results/FAF5_2022_Highway_Assignment_Results/Assignment_Flow_Tables/CSV_Format/FAF5_Total_{highway_assignment_modifier}Truck_Flows_by_Commodity_2022.csv"
    )

    # Filter for the columns we're interested in
    columns = ["ID", f"TOT Tons_22 {unit_type}"]
    if include_trips:
        columns += [f"TOT Trips_22 {unit_type}"]
    highway_assignments_filtered_df = highway_assignments_df.filter(columns, axis=1)
    highway_assignments_filtered_df = highway_assignments_filtered_df.rename(
        columns={
            f"TOT Tons_22 {unit_type}": "Tot Tons",
            f"TOT Trips_22 {unit_type}": "Tot Trips",
        }
    )

    return highway_assignments_filtered_df


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the highway flow assignments for each link
#    df_highway_assignments_all = read_highway_assignments(top_dir, unit_type="All")
#    df_highway_assignments_su = read_highway_assignments(top_dir, unit_type="SU")
#    df_highway_assignments_cu = read_highway_assignments(top_dir, unit_type="CU")
    df_highway_assignments_interstate = read_highway_assignments(
        top_dir, unit_type="All", include_trips=True
    )
    # start_time = time.time()

    # Merge the highway flow assignments in with the shapefile containing the highway links
#    merged_dataframe_all_nomin = mergeShapefile(
#        df_highway_assignments_all,
#        f"{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp",
#        min_tonnage=0,
#    )
#    merged_dataframe_su = mergeShapefile(
#        df_highway_assignments_su,
#        f"{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp",
#        min_tonnage=10000,
#    )
#    merged_dataframe_cu = mergeShapefile(
#        df_highway_assignments_cu,
#        f"{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp",
#        min_tonnage=10000,
#    )
    merged_dataframe_interstate = mergeShapefile(
        df_highway_assignments_interstate,
        f"{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp",
        min_tonnage=0,
        road_class=11,
    )

    # print(f'Merging took {time.time() - start_time} seconds')

    # Save the merged shapefile
#    saveShapefile(
#        merged_dataframe_all_nomin,
#        f"{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin.shp",
#    )
#    saveShapefile(
#        merged_dataframe_su,
#        f"{top_dir}/data/highway_assignment_links/highway_assignment_links_single_unit.shp",
#    )
#    saveShapefile(
#        merged_dataframe_cu,
#        f"{top_dir}/data/highway_assignment_links/highway_assignment_links_combined_unit.shp",
#    )
    saveShapefile(
        merged_dataframe_interstate,
        f"{top_dir}/data/highway_assignment_links/highway_assignment_links_interstate.shp",
    )


main()
