#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import os
import pandas as pd
from datetime import datetime

from anomaly_rules.anomaly_rule_overspeeding import overspeeding
from params_builder import ParamsBuilder, ArgParser
from common.filter_trajectories import filter_ais_data

one_dir_up_from_this_file = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def main():

    arg_parser = ArgParser()
    args = arg_parser.parse()

    params_builder = ParamsBuilder()
    params_builder.update_params(args)

    params = params_builder.params

    params = fill_in_params(params)  # first pass

    # the way this is set up, they will not be kicked out and have to rerun main, no matter how many times they give incorrect input
    # the errors will just be a notification, they will be looped back to try again
    while not validate_params(params):
        params = fill_in_params(params)

    print("\nParameter specifications are complete. Loading filtered AIS data... \n")
    ais_data = load_and_filter_data(params)

    print("AIS data loaded and filtered successfully. \n")

    if params["anomaly_type"] == "overspeed":

        print("Calculating speed threshold... \n")
        processed_data = overspeeding(params, ais_data)

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        output_path = os.path.join(one_dir_up_from_this_file, "output")
        os.makedirs(output_path, exist_ok=True)

        path = os.path.join(output_path, f"overspeed_detection_{current_date}.csv")
        # then save processed to a csv in an output dir
        processed_data.to_csv(path, index=False)

        # We have determined through trial-and-error that datasets
        # smaller than 50,000 are somewhat unreliable in their calculated results.
        # This is just to warn the users about it.
        if len(processed_data) < 50000:
            print("\n" + 105 * "*")
            print(
                "*** WARNING: The resulting dataset is small; we recommend adjusting your filters to expand the dataset."
            )
            print(105 * "*" + "\n")

        print(
            f"Successfully saved data (with all overspeed trajectories flagged) to {path}."
        )

    elif params["anomaly_type"] == "speed abnormality":
        print(
            "Speed abnormality functionality still in production. Please reach out to developers."
        )

    # other anomaly type cases will be run here


def fill_in_params(params):
    global PASS

    if params["anomaly_type"] is None:
        params["anomaly_type"] = "overspeed"
        # Currently only support overspeed, so this prompt is just misguiding
        # params["anomaly_type"] = (
        #     input(
        #         "Please specify which type of anomaly rules or anomaly generation you want to create. \nChoose from Overspeed: \n"
        #     )
        #     .strip()
        #     .lower()
        # )

    if params["Hawaii_GT"] is None:
        params["Hawaii_GT"] = (
            input(
                "Please specify if you want to use the Hawaii GT data (True/False): \n"
            )
            .strip()
            .lower()
        )

    if (params["Hawaii_GT"] is False) and (params["AIS_file_name"] is None):
        params["AIS_file_name"] = input(
            "Please enter the AIS file name (without .csv extension): \n"
        ).strip()

    if params["vessel_class"] is None:
        params["vessel_class"] = input(
            "Please enter vessel classes (space-separated): \n"
        ).split()

    # safegaurd against entering something that is not a number;
    # this allows them to try again without rerunning main
    try:
        if params["length_range"] is None:
            length_input = input(
                "Please enter the length range in the correct format (min-max): \n"
            )
            min_length, max_length = map(int, length_input.split("-"))
            params["length_range"] = [min_length, max_length]
    except Exception as e:
        params["length_range"] = None
        print(
            "Invalid length range. Please enter the length range in the "
            f"correct format (min-max). {e}"
        )

    # TIMEFRAME
    try:
        if params["timeframe"]["start"] is None:
            params["timeframe"]["start"] = pd.to_datetime(
                input("Please enter the start date (YYYY-MM-DD): \n")
            )
    except Exception as e:
        params["timeframe"]["start"] = None
        print(f"Invalid start date. {e}")

    try:
        if params["timeframe"]["end"] is None:
            params["timeframe"]["end"] = pd.to_datetime(
                input("Please enter the end date (YYYY-MM-DD): \n")
            )
    except Exception as e:
        params["timeframe"]["end"] = None
        print(f"Invalid end date. {e}")

    # HOUR CONSTRAINTS
    try:
        if params["hour_constraint"]["start"] is None:
            start = input(
                "Please enter the start of the hour constraint (or press Enter to use the full day): \n"
            )
            if start.strip() == "":
                # Set to the beginning of the day
                params["hour_constraint"]["start"] = datetime.combine(
                    params["timeframe"]["start"].date(), datetime.min.time()
                )
                params["hour_constraint"]["end"] = datetime.combine(
                    params["timeframe"]["start"].date(), datetime.max.time()
                )
            else:
                params["hour_constraint"]["start"] = datetime.strptime(start, "%H:%M")
    except Exception as e:
        params["hour_constraint"]["start"] = None
        print(f"Invalid start time. {e}")

    try:
        if (params["hour_constraint"]["start"] is not None) and (
            params["hour_constraint"]["end"] is None
        ):
            end = input("Please enter the end of the hour constraint. \n")
            params["hour_constraint"]["end"] = datetime.strptime(end, "%H:%M")
    except Exception as e:
        params["hour_constraint"]["end"] = None
        print(f"Invalid end time. {e}")

    return params


def validate_params(params):
    """
    Each case will check, then immediately return false if a parameter is invalid.
    if all are valid, they will all be formatted and reassigned to themselves

    AIS_file_name will be validated in load_ais_data function

    """

    # needs to be an anomaly type that we support
    if params["anomaly_type"] not in [
        "overspeed",
        # speed abnormality not completed
        # "speed abnormality",
    ]:
        print(
            "PARAM ERROR: Anomaly Type ~ Please choose from the allowed anomaly rule/generation types"
        )
        params["anomaly_type"] = None
        return False

    # for prompted user input (that is valid), convert to bool
    if params["Hawaii_GT"] in ["true", "false", "True", "False", "T", "F"]:
        params["Hawaii_GT"] = params["Hawaii_GT"].lower()[0] == "t"
    elif isinstance(params["Hawaii_GT"], bool):
        pass
    # then the general catch all
    else:
        print("PARAM ERROR: Hawaii_GT ~ Please enter either true or false")
        params["Hawaii_GT"] = None
        return False

    # if a user wants to select their own file, they need to set Hawaii_GT to False
    if params["Hawaii_GT"] == False:
        try:
            # try to read the file they asked for as a csv
            file_name = params["AIS_file_name"]
            file_path = os.path.join(
                one_dir_up_from_this_file, "data", f"{file_name}.csv"
            )
            pd.read_csv(file_path)

        except Exception as e:
            params["AIS_file_name"] = None
            print(
                f"Cannot find specified file. Make sure file exists and you are entering the name correctly. {e}"
            )

    valid_vessel_classes = [
        "cargo",
        "diving",
        "fishing",
        "industrial vessel",
        "military",
        "offshore supply vessel",
        "oil recovery",
        "other",
        "passenger",
        "pilot vessel",
        "pleasure craft/sailing",
        "port tender",
        "public vessel, unclassified",
        "research vessel",
        "school ship",
        "search and rescue vessel",
        "tanker",
        "tug tow",
    ]
    # make sure it's a vessel class that we know is valid
    if not any(vessel in valid_vessel_classes for vessel in params["vessel_class"]):
        print(f"PARAM ERROR: Vessel class ~ Please choose from {valid_vessel_classes}.")
        return False

    # tries to convert to datetime in param collection, if it fails, the variable will be set to None
    # the next 4 lines serve to loop the user back around and try to enter valid input

    if params["timeframe"]["start"] is None:
        print(
            "PARAM ERROR: Timeframe ~ please insert a valid timeframe in YYYY-MM-DD format"
        )
        return False
    if params["timeframe"]["end"] is None:
        print(
            "PARAM ERROR: Timeframe ~ please insert a valid timeframe in YYYY-MM-DD format"
        )
        return False

    if params["hour_constraint"]["start"] is None:
        print("PARAM ERROR: Hour constraint ~ please insert a valid hour")
        return False
    if params["hour_constraint"]["end"] is None:
        print("PARAM ERROR: Hour constraint ~ please insert a valid hour")
        return False

    # checks to make sure the length is a non-negative, reasonable range
    if not all(1 <= x <= 400 for x in params["length_range"]):
        print(
            "PARAM ERROR: Length range ~ please insert a valid length range (between 1 and 400)."
        )
        return False

    return True


def load_and_filter_data(params):

    try:
        if params["Hawaii_GT"] is True:

            start_date = params["timeframe"]["start"]
            end_date = params["timeframe"]["end"]

            # generate the list of month-year combinations
            date_range = pd.date_range(start=start_date, end=end_date, freq="MS")

            data_frames = []

            for date in date_range:
                file_name = f"Hawaii_{date.year}_{date.month:02d}.csv"
                file_path = os.path.join(
                    one_dir_up_from_this_file, "data", f"{file_name}"
                )
                print(f"INFO: Loading file {file_path}...")

                # each month is filtered before being concatenated to final dataframe
                current_month = pd.read_csv(file_path)
                current_month["datetime_utc"] = pd.to_datetime(
                    current_month["datetime_utc"]
                )
                current_month["datetime_hst"] = pd.to_datetime(
                    current_month["datetime_hst"]
                )

                current_month_filtered = filter_ais_data(params, current_month)

                data_frames.append(current_month_filtered)

            if not data_frames or all(df is None for df in data_frames):
                raise ValueError(
                    "No data could be gathered given your specified parameters. Please adjust and try again."
                )
            data = pd.concat(data_frames)

        else:
            file_name = params["AIS_file_name"]
            file_path = os.path.join(
                one_dir_up_from_this_file, "data", f"{file_name}.csv"
            )

            data = pd.read_csv(file_path)

            data["datetime_utc"] = pd.to_datetime(data["datetime_utc"])
            data["datetime_hst"] = pd.to_datetime(data["datetime_hst"])
            # filter before returning
            filter_ais_data(params, data)

        data.set_index("MMSI", inplace=True)

        return data

    except Exception as e:
        print(
            f"FAILED: {e}\nEnsure that you have the correct file name or have specified valid Hawaii_GT dates and try again. "
        )
        raise


if __name__ == "__main__":

    main()
