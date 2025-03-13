[![DOI](https://zenodo.org/badge/749951605.svg)](https://zenodo.org/doi/10.5281/zenodo.13205855)

# Backend to produce layers for the Geo-TIDE tool

This repo contains code to produce and synthesize visualize publicly available geospatial data to support trucking fleets in navigating the transition to alternative energy carriers. The tool uses data from the "freight analysis framework" (FAF5) database and other public data sources.

The layers can be interactively visualized using the Geo-TIDE tool ([link to the Geo-TIDE code repo](https://github.com/mcsc-impact-climate/Geo-TIDE)).

## Pre-requisites
* python3

## Setup

```bash
git clone git@github.com:mcsc-impact-climate/FAF5-Analysis.git
```

Install python requirements
```bash
pip install -r requirements.txt
```

## Downloading the data

The script [`download_data.sh`](./download_data.sh) downloads all the data needed to run this code into the `data` directory. Note that it will only download a file if it doesn't already exist in the `data` directory. To run:

```bash
bash download_data.sh
```

## Processing highway assignments

The script [ProcessFAFHighwayData.py](./source/ProcessFAFHighwayData.py) reads in both the FAF5 network links for the entire US and the associated highway network assignments for total trucking flows, and joins the total flows for 2022 (all commodities combined) with the FAF5 network links via their common link IDs to produce a combined shapefile.

To run:

```bash
python processFAFHighwayData.py 
```

This should produce a shapefile in `data/highway_assignment_links`.

## Processing eGRID emission intensity data

The script [ProcessGridData.py](./source/ProcessGridData.py) reads in the shapefile containing the borders of subregions within which eGRIDs reports grid emissions data, along with the associated eGRIDs data, and joins the shapefile with the eGRIDs data via the subregion ID to produce a combined shapefile.

To run:

```bash
python source/ProcessGridData.py 
```

This should produce shapefiles in `data/egrid2020_subregions_merged` and `data/eia2020_subregions_merged`.

## Processing electricity prices and demand charges

The script [ProcessPrices.py](./source/ProcessPrices.py) reads in the shapefile containing borders of zip codes and states, along with the associated electricity price data and demand charges, and joins the shapefiles with the electricity price data via the subregion ID to produce combined shapefiles. It also evaluates electricity price, demand charge and diesel price by state. 

To run:

```bash
python source/ProcessPrices.py 
```

## Processing State-level Incentives and Regulations

The script [ProcessStateSupport.py](./source/ProcessStateSupport.py) reads in the shapefile containing borders of US states, along with CSV files containing state-level incentives relevant to trucking from the [AFDC website](https://afdc.energy.gov/laws/state), and joins the CSV files with the shapefile to produce a set of shapefiles with the number of incentives of each type (fuel, vehicle purchase, emissions and infrastructure) and fuel target (electrification, hydrogen, ethanol, etc.) for each state. 

To run:

```bash
python source/ProcessStateSupport.py
```

## Processing planned infrastructure corridors for heavy duty vehicles

The script [PrepareInfrastructureCorridors.py](./source/PrepareInfrastructureCorridors.py) reads in either a shapefile with the US highway system, or shapefiles with specific regions of planned heavy duty vehicle infrastructure corridors [announced by the Biden-Harris administration](https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle). For corridors represented as subsets of the national highway system, the code produces shapefiles for each highway segment with a planned infrastructure project. For corridors represented as regions of the US, the code produces shapefiles showing the region(s) where the planned infrastructure project will take place. 

To run:

```bash
python source/PrepareInfrastructureCorridors.py
```

This should produce shapefiles for zipcode-level and state-level electricity prices in `data/electricity_rates_merged`

## Analyzing VIUS data

The script [AnalyzeVius.py](./source/AnalyzeVius.py) produces distributions of GREET vehicle class, fuel type, age, and payload from the VIUS data. To run:

```bash
python source/AnalyzeVius.py
```

## Processing VIUS data to evaluate average product of fuel efficiency and payload

Run the script [ViusTools.py](./source/ViusTools.py) to produce an output file tabulating the product of fuel efficiency (mpg) times payload for each commodity, along with the associated standard deviation:

```bash
python source/ViusTools.py
```

This should produce the following output file: `data/VIUS_Results/mpg_times_payload.csv`. 

## Producing shapefiles to visualize freight flows and emission intensities

The script [Point2PointFAF.py](./source/Point2PointFAF.py) combines outputs from VIUS, GREET and FAF5 and merges it with geospatial shapefiles with the contours of FAF5 regions to associate each region with tons, ton-miles, and associated emissions of imports to and exports from each region, along with areal densities of these three quantities (i.e. divided by the surface area of the associated region). There is also functionality to evaluate these quantities for a user-specified mode, commodity, origin region, or destination region. 

Before running this code, you'll need to have first run the following:

```bash
python source/ViusTools.py
```

To run:

```bash
python source/Point2PointFAF.py -m user_specified_mode -c "user_specified_commodity" -o user_specified_origin_ID -d user_specified_destination_ID
```

This should produce a csv and shapefile in `data/Point2Point_outputs/mode_truck_commodity_Logs_origin_11_dest_all.[extension]`. 

NOTE: The "" around the commodity option is important because some commodities contain spaces, and python does NOT like command line arguments with spaces...

where each argument defaults to 'all' if left unspecified. The mode is one of {all, truck, water, rail}. The available commodities can be found in the 'Commodity (SCTG2)' sheet in `data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx` ('Description' column). The origin and destination region IDs can be found in the 'FAF Zone (Domestic)' sheet of the same excel file ('Numeric Label' column'). 

For example, to filter for logs carried by trucks from FAF5 region 11 to FAF5 region 139:

```bash
python source/Point2PointFAF.py -m truck -c Logs -o 11 -d 139
```

There's also a bash script in `source/run_all_Point2Point.sh` that can be executed to produce merged shapefiles for all combinations of modes, commodities, origins and destinations. 

To run:

```bash
bash source/run_all_Point2Point.sh
```

WARNING: This may take several hours to run in full, and the shapefiles and csv files produced will take up ~100 GB. To reduce this, you can comment out items that you don't want in the COMMODITIES, REGIONS and MODES variables.

## Creating shapefiles for hydrogen production facilities

The script [PrepareHydrogenHubs.py](./source/PrepareHydrogenHubs.py) combines locations and information about operating and planned hydrogen production facilities and the U.S. and Canada into shapefiles located in `data/hydrogen_hubs/shapefiles`. To run:

```bash
python source/PrepareHydrogenHubs.py
```

## Identifying truck stops and hydrogen production facilities within a given radius

The script [IdentifyFacilitiesInRadius.py](./source/IdentifyFacilitiesInRadius.py) identifies truck stops and hydrogen production facilities within a user-provided radius and central location - (33N, 97W) and 600 miles by default.

## Analyze potential infrastructure investment savings from collective investment in truck stop charging

The script [AnalyzeTruckStopCharging.py](./source/AnalyzeTruckStopCharging.py) is designed to quantify the charging demand at truck stops along U.S. interstates that are sparsified to support the specified truck range, and estimate the potential difference in infrastructure costs needed if the entire electrified trucking fleet were to electrify and either:
* The full electrified fleet shared the investment and usage of charging infrastructure, or
* The fleet was divided in half, and each half invested in and used their respective charging infrastructure separately. 

The idea of this exercise is to understand the potential infrastructure savings from trucking fleets pooling infrastructure investments in charging infrastructure based on real-world freight flow data. 

The methodology is detailed in [MacDonell and Borrero, 2024](https://dspace.mit.edu/handle/1721.1/153617).

To run with a specified set of options:

```bash
python source/AnalyzeTruckStopCharging.py -c [charging time (hours)] -m [max allowable wait time (hours)] -r [truck range (miles)]
```

To run over all options visualized in the geospatial mapping tool:

```bash
bash source/run_all_AnalyzeTruckStopCharging.sh
```

## Evaluating state-level electricity demand if trucking is fully electrified

The script [EvaluateTruckingEnergyDemand.py](./source/EvaluateTruckingEnergyDemand.py) aggregates highway-level FAF5 commodity flows and trips to evaluate the approximate annual energy demand (in MWh) that would be placed on the grid for each state if all trucking operations were to be fully electrified. The energy demand is calculated assuming that the flows are carried by the Tesla Semi, using the mileage with respect to payload calibrated using code in [this repo](https://github.com/mcsc-impact-climate/Green_Trucking_Analysis) ([link to relevant section of README](https://github.com/mcsc-impact-climate/Green_Trucking_Analysis?tab=readme-ov-file#evaluate-straight-line-approximation-of-fuel-economy-as-a-function-of-payload)). The underlying calibration is performed in [this repo](https://github.com/mcsc-impact-climate/PepsiCo_NACFE_Analysis) using data from the PepsiCo Tesla Semi pilot. 

To run:

```bash
python source/EvaluateTruckingEnergyDemand.py
```

This produces an output shapefile in `data/trucking_energy_demand` containing the energy demand for each state from electrified trucking, both as an absolute value (in MWh), and as a percent of each of the following:
* The total energy generated in the state in 2022
* The theoretical total energy generation capacity for the state in 2022 (if the grid were to run at its full summer generating capacity 24/7)
* The theoretical excess energy generation capacity (i.e. theoretical - actual energy generated in 2022)

## Comparing electricity demand for full trucking electrification with historical load in Texas ERCOT weather zones

### Visualizing demand for each charging site

The script [`TT_charging_analysis.py`](./source/TT_charging_analysis.py) produces a plot visualizing the demands associated with electrifying trucking with charging at 8 sites in the Texas triangle region. To run:

```bash
python source/TT_charging_analysis.py
```
This will produce `Texas_charger_locations.png` in the `plots` directory that compares the 

### Producing daily electricity demand curves for each charging site

The script [`MakeChargingLoadByZone.py`](source/MakeChargingLoadByZone.py) produces a csv file for each ERCOT weather zone containing one or more charging sites. For each such zone, the csv file contains the daily load from each charging site in the weather zone, assuming it follows the most extreme variation found in Borlaug et al (2021) for immediate charging (see red curve in Fig. 5 in the paper). 

To run:
```bash
python source/MakeChargingLoadByZone.py
```

This will produce a csv file `daily_ev_load_[zone].csv` for each zone.

### Comparing daily EV demand with historical load for each month

The script [`AnalyzeErcotData.py`](source/AnalyzeErcotData.py) compares the daily EV demand each charging site in a zone (along with the total combined demand) with the estimated excess capacity of the grid over the day. 

To run:

```bash
python source/AnalyzeErcotData.py
```

This will produce a plot for each zone and month called `daily_ev_load_with_excess_[zone]_[month].png` in the `plots` directory.




