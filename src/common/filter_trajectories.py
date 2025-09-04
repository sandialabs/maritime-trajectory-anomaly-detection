#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________


# Function to filter AIS data based on user selections
def filter_ais_data(params, ais_data):
    """Filters AIS data based on user selections."""
    vessel_classes = params["vessel_class"]
    length_range = params["length_range"]
    timeframe = params["timeframe"]

    # VESSEL CLASS
    ais_data["vessel_class"] = ais_data["vessel_class"].str.lower().str.strip()

    ais_data = ais_data[
        ais_data["vessel_class"].isin(vessel_classes)
    ]  # only include trajectories with the labels from params

    # LENGTH RANGE
    ais_data = ais_data[
        (ais_data["length_m"] >= length_range[0])
        & (ais_data["length_m"] <= length_range[1])
    ]

    # Check ranges based on UTC timestamps - need to check whether it's timezone aware timestamping or not
    timeframe["start"] = ensure_utc(timeframe["start"])
    timeframe["end"] = ensure_utc(timeframe["end"])

    # TIMEFRAME
    ais_data = ais_data[
        (ais_data["datetime_utc"] >= timeframe["start"])
        & (ais_data["datetime_utc"] <= timeframe["end"])
    ]

    ais_data["time"] = ais_data["datetime_utc"].dt.time

    # HOUR CONSTRAINTS
    params["hour_constraint"]["start"]

    ais_data = ais_data[
        (ais_data["time"] >= params["hour_constraint"]["start"].time())
        & (ais_data["time"] <= params["hour_constraint"]["end"].time())
    ]

    if ais_data.empty:
        print(
            "WARNING: Your selected parameters have resulted in all trajectories in this data file being filtered out."
        )

    else:
        return ais_data


def ensure_utc(dt):
    if dt.tzinfo is None:
        return dt.tz_localize("UTC")
    return dt.tz_convert("UTC")
