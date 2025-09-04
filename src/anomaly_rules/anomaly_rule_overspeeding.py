#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import pandas as pd
import numpy as np


def overspeeding(params, filtered_data):
    percentile = 0.98  # default

    if params["percentile"] is not None:
        percentile = params["percentile"]

    # get rid of NaN speeds
    filtered_data = filtered_data.assign(
        computed_speed_knots=pd.to_numeric(
            filtered_data["comput_speed_knots"], errors="coerce"
        )
    ).dropna(subset=["comput_speed_knots"])

    speed_threshold = compute_speed_threshold(filtered_data, percentile)

    filtered_data["overspeed_flag"] = (
        filtered_data["computed_speed_knots"] > speed_threshold
    )

    print(
        f"DEBUG All Data:\n{filtered_data[['datetime_utc', 'comput_speed_knots', 'overspeed_flag']]}\n"
    )

    print(
        f"DEBUG Flagged:\n{filtered_data[filtered_data['overspeed_flag']][['datetime_utc', 'computed_speed_knots', 'overspeed_flag']]}\n"
    )

    return filtered_data


def compute_speed_threshold(filtered_ais_data, percentile=0.98):
    valid_speeds = (
        filtered_ais_data["speed_over_ground_knots"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    speed_threshold = np.percentile(valid_speeds, percentile * 100)

    print(f"Speed threshold successfully generated: {speed_threshold} knots\n")

    return speed_threshold
