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
    percentile = 0.99  # default

    if params["percentile"] is not None:
        percentile = params["percentile"]

    # get rid of NaN speeds
    filtered_data = filtered_data.assign(
        computed_speed_knots=pd.to_numeric(
            filtered_data["comput_speed_knots"], errors="coerce"
        )
    ).dropna(subset=["comput_speed_knots"])

    additionally_filtered_data = apply_additional_overspeed_filters(filtered_data)

    speed_threshold, filtered_data = compute_speed_threshold(
        additionally_filtered_data, percentile
    )

    additionally_filtered_data["overspeed_flag"] = (
        additionally_filtered_data["computed_speed_knots"] > speed_threshold
    )

    print(
        f"DEBUG All Filtered Data:\n{additionally_filtered_data[['datetime_utc', 'comput_speed_knots', 'overspeed_flag']]}\n"
    )

    print(
        f"DEBUG Flagged Data:\n{additionally_filtered_data[additionally_filtered_data['overspeed_flag']][['datetime_utc', 'computed_speed_knots', 'overspeed_flag']]}\n"
    )

    return additionally_filtered_data


def apply_additional_overspeed_filters(filtered_ais_data):
    # Remove stopped or moored data points where status code is 1 OR 5
    # AND the computed speed < 0.1 knots
    mask_status = ~(
        (
            (filtered_ais_data["status"].isin([1, 5]))
            & (filtered_ais_data["computed_speed_knots"] < 0.1)
        )
    )
    # The world's fastest ship can go 58 knots, per:
    # https://maritimepage.com/what-is-the-fastest-ship-in-the-world/
    # We're being safe and adding a bit more to that, which is how
    # we get to 65 knots as the "outlier" threshold
    mask_speed = filtered_ais_data["computed_speed_knots"] <= 65
    newly_filtered_data = filtered_ais_data[mask_status & mask_speed]

    return newly_filtered_data


def compute_speed_threshold(filtered_ais_data, percentile):
    valid_speeds = (
        filtered_ais_data["computed_speed_knots"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    speed_threshold = np.percentile(valid_speeds, percentile * 100)

    print(f"Speed threshold successfully generated: {speed_threshold} knots\n")

    return speed_threshold, valid_speeds
