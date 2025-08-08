"""
Created on Thu Aug 31 14:52:00 2023

Author: danikae
"""

# Import needed modules
import pandas as pd
import geopandas as gpd
from CommonTools import get_top_dir, saveShapefile, state_names_to_abbr
import glob
import os


def read_state_data(top_dir):
    """
    Reads in the data files for state-level regulations and incentives

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repo

    Returns
    -------
    data_dict (dict): A dictionary of pandas dataframe containing state-level incentives and regulations, divided into vehicle purchase, fuel use, emissions, and infrastructure

    NOTE: None.
    """

    # Dictionary to contain the dataframes with csv info for state-level incentives and regulations
    data_dict = {}

    # Loop through the csv files in the data directory and collect the info in each in a dataframe
    dataPath = f"{top_dir}/data/incentives_and_regulations/state_level/*.csv"

    for fpath in glob.glob(dataPath):
        # Read in the data as a dataframe
        data_df = pd.read_csv(fpath)

        # Update the state name to its associated abbreviation
        data_df = state_names_to_abbr(data_df, "State")

        # Rename the state header to match the shapefile
        data_df = data_df.rename(columns={"State": "STUSPS"})

        # Get the filename without extension for the associated name in the data dictionary
        fname_noext = os.path.splitext(fpath.split("/")[-1])[0]

        data_dict[fname_noext] = data_df

    return data_dict


def add_aggregated_data(data_dict):
    """
    Combines rows in dataframes to aggregate into: all incentives, all regulations, and all regulations and incentives

    Parameters
    ----------
    data_dict (dict): A dictionary of pandas dataframe containing state-level incentives and regulations, divided into vehicle purchase, fuel use, emissions, and infrastructure

    Returns
    -------
    data_dict (pd.DataFrame): Dictionary with additional aggregated dataframes

    NOTE: None.
    """

    # Combine rows separately for incentives and regulations
    for support_type in ["incentives", "regulations"]:
        # Initialize a dataframe to contain the aggregated incentives or regulations
        aggregated_df = pd.DataFrame()

        for key in data_dict:
            # Concatenate all rows, except for emissions (those will be handled separately)
            if support_type in key and "emissions" not in key:
                aggregated_df = pd.concat(
                    [aggregated_df, data_dict[key]], ignore_index=True
                )

                # Remove duplicate rows for each state
                aggregated_df = aggregated_df.drop_duplicates(subset=["STUSPS", "Name"])

        # Add the emissions info to the aggregated dataframe as a Type
        emissions_df = data_dict[f"emissions_{support_type}"]

        # Loop through the emissions rows and add them to the aggregated dataframe
        for index, row in emissions_df.iterrows():
            row_state = row["STUSPS"]
            row_name = row["Name"]

            aggregated_df_row = aggregated_df.loc[
                (aggregated_df["STUSPS"] == row_state)
                & (aggregated_df["Name"] == row_name)
            ]

            # If there is a row matching the state and incentive/regulation name, just add 'Emissions' to the list of Types
            if len(aggregated_df_row) == 1:
                # Get the current list of Types
                types = aggregated_df[
                    (aggregated_df["STUSPS"] == row_state)
                    & (aggregated_df["Name"] == row_name)
                ]["Types"].values[0]

                # Add ', Emissions' to the list of Types
                aggregated_df.loc[
                    (aggregated_df["STUSPS"] == row_state)
                    & (aggregated_df["Name"] == row_name),
                    "Types",
                ] = types + ", Emissions"

            # Otherwise, just add a new fow with 'Emissions' as Types
            elif len(aggregated_df_row) == 0:
                row["Types"] = "Emissions"
                aggregated_df = pd.concat(
                    [aggregated_df, row.to_frame().T], ignore_index=True
                )

            else:
                print(
                    f"ERROR: Emissions {support_type[:-1]} '{aggregated_df['Name'].values[0]}' appears more than once."
                )

        data_dict[f"all_{support_type}"] = aggregated_df

    # Now, make a dataframe containing both incentives and regulations
    data_dict["all_incentives_and_regulations"] = pd.concat(
        [data_dict["all_incentives"], data_dict["all_regulations"]], ignore_index=True
    )
    data_dict["fuel_use_incentives_and_regulations"] = pd.concat(
        [data_dict["fuel_use_incentives"], data_dict["fuel_use_regulations"]],
        ignore_index=True,
    )
    data_dict["infrastructure_incentives_and_regulations"] = pd.concat(
        [
            data_dict["infrastructure_incentives"],
            data_dict["infrastructure_regulations"],
        ],
        ignore_index=True,
    )
    data_dict["vehicle_purchase_incentives_and_regulations"] = pd.concat(
        [
            data_dict["vehicle_purchase_incentives"],
            data_dict["vehicle_purchase_regulations"],
        ],
        ignore_index=True,
    )
    data_dict["emissions_incentives_and_regulations"] = pd.concat(
        [data_dict["emissions_incentives"], data_dict["emissions_regulations"]],
        ignore_index=True,
    )

    return data_dict


def restructure_state_data(data_df, df_name):
    """
    Restructures a dataframe containing state-level incentives to list, for each state, the number of incentives for each fuel type

    Parameters
    ----------
    data_df (pd.DataFrame): Dataframe containing state-level incentives or regulations in a given category (eg. emissions incentives, fuel use regulations, etc.)
    df_name (string): Name of the dataframe in the dictionary

    Returns
    -------
    data_df_restructured (pd.DataFrame): Restructured dataframe

    NOTE: None.
    """
    states = sorted(list(set(data_df["STUSPS"])))
    data_df_restructured = pd.DataFrame()

    for state in states:
        data_df_state = data_df[data_df["STUSPS"] == state]

        # If the data relates to emissions, no need to disaggregate by fuel type
        if "emissions" in df_name:
            info_for_df = {"STUSPS": state, "all": len(data_df_state)}
            data_df_restructured = pd.concat(
                [data_df_restructured, pd.DataFrame([info_for_df])], ignore_index=True
            )

        # Otherwise, disaggregate by fuel type or emissions
        else:
            # If the data is aggregated over all regulations or incentives, need to include 'Emissions' in the list of types
            if "all" in df_name:
                types = [
                    "Biodiesel",
                    "Ethanol",
                    "Electricity",
                    "Hydrogen",
                    "Natural Gas",
                    "Propane",
                    "Renewable Diesel",
                    "Emissions",
                ]
            else:
                types = [
                    "Biodiesel",
                    "Ethanol",
                    "Electricity",
                    "Hydrogen",
                    "Natural Gas",
                    "Propane",
                    "Renewable Diesel",
                ]
            info_for_df = {
                "STUSPS": state,
                "all": len(data_df_state),
            }

            for types in types:
                info_for_df[types] = len(
                    data_df_state[data_df_state["Types"].str.contains(types)]
                )
            data_df_restructured = pd.concat(
                [data_df_restructured, pd.DataFrame([info_for_df])], ignore_index=True
            )

    return data_df_restructured


def merge_state_shapefile(data_df, shapefile_path):
    """
    Merges the shapefile containing state boundaries with the dataframe containing the state-level incentives and regulations

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the subregion names and emissions data for each subregion

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    """
    shapefile = gpd.read_file(shapefile_path)
    shapefile = shapefile.filter(["STUSPS", "geometry"], axis=1)

    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on="STUSPS", how="left")

    # Replace all NaNs with 0
    merged_dataframe = merged_dataframe.fillna(0)

    return merged_dataframe


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the regulations and incentives data
    data_dict = read_state_data(top_dir)

    # Add aggregated dataframes containing incentives, regulations, and all regulations and incentives
    data_dict = add_aggregated_data(data_dict)

    # Restructure the dataframes so they can be merged with a shapefile of state boundaries
    for key in data_dict:
        data_dict[key] = restructure_state_data(data_dict[key], key)

    # Merge the dataframes with the state boundaries shapefile and save the result to a shapefile
    for key in data_dict:
        merged_state_data = merge_state_shapefile(
            data_dict[key], f"{top_dir}/data/state_boundaries/tl_2012_us_state.shp"
        )
        saveShapefile(
            merged_state_data,
            f"{top_dir}/data/incentives_and_regulations_merged/{key}.shp",
        )


main()
