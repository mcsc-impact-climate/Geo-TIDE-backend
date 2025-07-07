from shapely.geometry import shape, mapping
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString
from shapely.ops import unary_union
import geopandas as gpd
import json
import os
from CommonTools import get_top_dir
import InfoObjects
from sklearn.cluster import DBSCAN
import numpy as np

top_dir = get_top_dir()

def simplify(shapefiles, columns_keep, coordinate=3857, tolerance=1000):
    """
    Converts input shapefiles to geojson, and reduces their granularity (and size) for quick visualization.
    If a shapefile results in more than 60,000 features, it merges geometries to reduce the count.

    Parameters
    ----------
    shapefiles: dict
        Dictionary mapping names to shapefile paths relative to the data directory.
    columns_keep: dict
        Dictionary of lists of column names to retain for specific shapefiles.
    coordinate: int, optional
        EPSG code for target CRS. Default is 3857.
    tolerance: float, optional
        Simplification tolerance for geometry vertex reduction. Default is 1000.

    Returns
    -------
    None
    """

    MAX_FEATURES = 60000

    geojson_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"{top_dir}/geojsons_simplified")
    )
    os.makedirs(geojson_directory, exist_ok=True)

    def simplify_features(features, tol):
        simplified = []
        for feature in features:
            if feature["geometry"] is None:
                continue
            geometry = shape(feature["geometry"])
            if isinstance(geometry, (Polygon, LineString)):
                simplified_geometry = geometry.simplify(tol)
            elif isinstance(geometry, (MultiPolygon, MultiLineString)):
                simplified_geometry = geometry.__class__([g.simplify(tol) for g in geometry.geoms])
            else:
                simplified_geometry = geometry
            feature["geometry"] = mapping(simplified_geometry)
            simplified.append(feature)
        return simplified

    for shapefile in shapefiles:
        print(f"Processing shapefile: {shapefile}")
        shapefile_path = f"{top_dir}/data/{shapefiles[shapefile]}"
        geojson_filename = os.path.join(
            geojson_directory,
            os.path.splitext(os.path.basename(shapefile_path))[0] + ".geojson",
        )

        if not os.path.exists(shapefile_path):
            print(f"  WARNING: path {shapefile_path} does not exist.")
            continue

        try:
            gdf = gpd.read_file(shapefile_path)
        except Exception as e:
            print(f"  ERROR reading shapefile {shapefile_path}: {e}")
            continue

        if shapefile in columns_keep:
            gdf = gdf[columns_keep[shapefile]]

        gdf = gdf.to_crs(coordinate)
        gdf = gdf.set_crs(coordinate)

        # Simplify geometries
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: geom.simplify(tolerance) if geom else None)

        # Merge features if count is too high
        if len(gdf) > MAX_FEATURES:
            print(f"  Clustering and merging {len(gdf)} features to reduce count...")

            try:
                # Use centroids to cluster features spatially
                coords = np.array([[geom.centroid.x, geom.centroid.y] for geom in gdf.geometry])
                db = DBSCAN(eps=150, min_samples=1).fit(coords)  # eps in projected units (e.g. meters)
                gdf["cluster"] = db.labels_

                # Dissolve by cluster
                gdf = gdf.dissolve(by="cluster").reset_index(drop=True)

                print(f"  Resulting feature count after spatial clustering and dissolve: {len(gdf)}")

            except Exception as e:
                print(f"  WARNING: Clustering and dissolve failed: {e}")

        geojson_data = json.loads(gdf.to_json())

        with open(geojson_filename, "w") as geojson_file:
            json.dump(geojson_data, geojson_file)
        print(f"  Saved simplified geojson: {geojson_filename} ({len(geojson_data['features'])} features)\n")



if __name__ == "__main__":
    shapefiles = {}
    columns_keep = {}  # Keeps track of specific columns to keep in the output geojson, if needed

#    # Total domestic Imports and Exports
#    shapefiles["Truck Imports and Exports"] = (
#        "Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp"
#    )
#    for commodity in InfoObjects.faf5_commodities_list:
#        shapefiles[commodity] = os.path.join(
#            "Point2Point_outputs/",
#            f"mode_truck_commodity_{commodity}_origin_all_dest_all.shp".replace(
#                " ", "_"
#            ).replace("/", "_"),
#        )
#
#    # Grid emission intensity
#    shapefiles["Grid Emission Intensity by Balancing Authority"] = (
#        "egrid2022_subregions_merged/egrid2022_subregions_merged.shp"
#    )
#    shapefiles["Grid Emission Intensity by State"] = (
#        "eia2022_state_merged/eia2022_state_merged.shp"
#    )
#
#    for hour in range(24):
#        shapefiles[f"Daily Grid Emission Profile Hour {hour}"] = (
#            f"daily_grid_emission_profiles/daily_grid_emission_profile_hour{hour}.shp"
#        )
#
#    # Grid generation and capacity
#    shapefiles["Grid Capacity and Generation by State"] = (
#        "eia2022_state_merged/gen_cap_2022_state_merged.shp"
#    )
#
#    # Electricity demand from electrified trucking
#    shapefiles["Energy Demand from Electrified Trucking"] = (
#        "trucking_energy_demand/trucking_energy_demand.shp"
#    )
#
#    # Commercial electricity price by state
#    shapefiles["Commercial Electricity Price"] = (
#        "electricity_rates_merged/electricity_rates_by_state_merged.shp"
#    )
#
#    # Diesel price by state
#    shapefiles["Diesel Price"] = "diesel_price_by_state/diesel_price_by_state.shp"
#
#    # Maximum demand charges from NREL
#    shapefiles["Maximum Demand Charge"] = (
#        "electricity_rates_merged/demand_charges_merged.shp"
#    )
#    shapefiles["Demand Charge by State"] = (
#        "electricity_rates_merged/demand_charges_by_state.shp"
#    )
    # Highway flows
    shapefiles["Highway Flows (Interstate)"] = (
        "highway_assignment_links/highway_assignment_links_interstate.shp"
    )
#    shapefiles["Highway Flows (SU)"] = (
#        "highway_assignment_links/highway_assignment_links_single_unit.shp"
#    )
#    shapefiles["Highway Flows (CU)"] = (
#        "highway_assignment_links/highway_assignment_links_combined_unit.shp"
#    )
#
#    # Alternative fueling stations along highway corridors
#    shapefiles["DCFC Chargers"] = "Fuel_Corridors/US_elec/US_elec.shp"
#    columns_keep["DCFC Chargers"] = ["geometry"]
#    shapefiles["Hydrogen Stations"] = "Fuel_Corridors/US_hy/US_hy.shp"
#    columns_keep["Hydrogen Stations"] = ["geometry"]
#    shapefiles["LNG Stations"] = "Fuel_Corridors/US_lng/US_lng.shp"
#    columns_keep["LNG Stations"] = ["geometry"]
#    shapefiles["CNG Stations"] = "Fuel_Corridors/US_cng/US_cng.shp"
#    columns_keep["CNG Stations"] = ["geometry"]
#    shapefiles["LPG Stations"] = "Fuel_Corridors/US_lpg/US_lpg.shp"
#    columns_keep["LPG Stations"] = ["geometry"]
#
#    # Hydrogen hubs
#    shapefiles["Operational Electrolyzers"] = (
#        "hydrogen_hubs/shapefiles/electrolyzer_operational.shp"
#    )
#    shapefiles["Installed Electrolyzers"] = (
#        "hydrogen_hubs/shapefiles/electrolyzer_installed.shp"
#    )
#    shapefiles["Planned Electrolyzers"] = (
#        "hydrogen_hubs/shapefiles/electrolyzer_planned_under_construction.shp"
#    )
#    shapefiles["Hydrogen from Refineries"] = "hydrogen_hubs/shapefiles/refinery.shp"
#
#    # DOE-funded heavy duty vehicle infrastructure projects
#    shapefiles["East Coast ZEV Corridor"] = "hd_zev_corridors/eastcoast.shp"
#    shapefiles["Midwest ZEV Corridor"] = "hd_zev_corridors/midwest.shp"
#    shapefiles["Houston to LA H2 Corridor"] = "hd_zev_corridors/h2la.shp"
#    shapefiles["I-710 EV Corridor"] = "hd_zev_corridors/la_i710.shp"
#    shapefiles["Northeast EV Corridor"] = "hd_zev_corridors/northeast.shp"
#    shapefiles["Bay Area EV Roadmap"] = "hd_zev_corridors/bayarea.shp"
#    shapefiles["Salt Lake City Region EV Plan"] = "hd_zev_corridors/saltlake.shp"
#
#    # Truck stop parking locations
#    shapefiles["Truck Stop Locations"] = "Truck_Stop_Parking/Truck_Stop_Parking.shp"
#
#    # Principal ports
#    shapefiles["Principal Ports"] = "Principal_Ports/Principal_Port.shp"
#
#    # Truck charger infrastructure savings (reference: https://dspace.mit.edu/handle/1721.1/153617)
#    truck_ranges = ["400.0", "300.0", "200.0", "100.0"]
#    max_wait_times = ["0.25", "0.5", "1.0", "2.0"]
#    charging_times = ["0.5", "1.0", "2.0", "4.0"]
#    for truck_range in truck_ranges:
#        for max_wait_time in max_wait_times:
#            for charging_time in charging_times:
#                shapefiles[
#                    "Truck charging (%s_%s_%s)"
#                    % (truck_range, charging_time, max_wait_time)
#                ] = (
#                    "Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_%s_chargingtime_%s_maxwait_%s.shp"
#                    % (truck_range, charging_time, max_wait_time)
#                )
#
#    # State-level support
#    support_types = ["incentives_and_regulations", "incentives", "regulations"]
#    support_targets = [
#        "all",
#        "emissions",
#        "fuel_use",
#        "infrastructure",
#        "vehicle_purchase",
#    ]
#    for support_type in support_types:
#        for support_target in support_targets:
#            shapefiles[
#                "State-Level Support (%s_%s)" % (support_target, support_type)
#            ] = f"incentives_and_regulations_merged/{support_target}_{support_type}.shp"
#
#    # Zero emission freight corridor strategy from the joint office
#    for phase in range(1,5):
#        shapefiles[f"ZEF Corridor Strategy Phase {phase} Corridors"] = f"zef-gis-files/GIS_Files_for_Publication/Phase_{phase}/ZEF_Corridor_Strategy_Phase{phase}_Corridors/ZEF_Corridor_Strategy_Phase{phase}_Corridors.shp"
#
#    for phase, phase_read in zip(["1", "3", "4"], ["Phase1_Phase2", "Phase3", "Phase4"]):
#        for infra in ["Facilities", "Hubs"]:
#            shapefiles[f"ZEF Corridor Strategy Phase {phase} {infra}"] = f"zef-gis-files/GIS_Files_for_Publication/Phase_{phase}/ZEF_Corridor_Strategy_{phase_read}_{infra}/ZEF_Corridor_Strategy_{phase_read}_{infra}.shp"

    simplify(shapefiles, columns_keep, coordinate=3857)
