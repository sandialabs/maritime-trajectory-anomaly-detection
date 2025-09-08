#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import argparse
import pandas as pd
from datetime import datetime


class ParamsBuilder:
    def __init__(self):
        # Initialize params with None values
        self.params = {
            "anomaly_type": None,
            "Hawaii_GT": None,
            "AIS_file_name": None,
            "vessel_class": None,
            "length_range": None,
            "percentile": None,
            "timeframe": {
                "start": None,
                "end": None,
            },
            "hour_constraint": {
                "start": None,
                "end": None,
            },
        }

    def update_params(self, args):
        if args.anomaly_type is not None:
            self.params["anomaly_type"] = args.anomaly_type

        if args.Hawaii_GT is not None:
            self.params["Hawaii_GT"] = args.Hawaii_GT

        if args.AIS_file_name is not None:
            self.params["AIS_file_name"] = args.AIS_file_name

        if args.vessel_class is not None:
            self.params["vessel_class"] = args.vessel_class

        if args.length is not None:
            min_length, max_length = map(int, args.length.split("-"))
            self.params["length_range"] = [min_length, max_length]

        if args.percentile is not None:
            self.params["percentile"] = args.percentile

        if args.date_start is not None:
            self.params["timeframe"]["start"] = pd.to_datetime(args.date_start)

        if args.date_end is not None:
            self.params["timeframe"]["end"] = pd.to_datetime(args.date_end)

        if args.hour_start is not None:
            self.params["hour_constraint"]["start"] = datetime.strptime(
                args.hour_start, "%H:%M"
            ).time()

        if args.hour_end is not None:
            self.params["hour_constraint"]["end"] = datetime.strptime(
                args.hour_end, "%H:%M"
            ).time()


class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Process AIS data for anomaly detection."
        )
        self.build_parser()

    def build_parser(self):

        self.parser.add_argument(
            "--anomaly_type",
            choices=["overspeed"],
            help="Type of anomaly to detect (choose one).",
        )

        self.parser.add_argument(
            "--Hawaii_GT",
            type=lambda x: (str(x).lower() == "true"),  # Convert to boolean
            help="Whether to use Hawaii GT data (True or False).",
        )

        self.parser.add_argument(
            "--AIS_file_name",
            type=str,
            help="Name of the AIS file (without extension).",
        )

        self.parser.add_argument(
            "--vessel_class",
            type=str,
            nargs="+",  # Allows multiple inputs
            choices=[
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
            ],
            help="Vessel classes (multiple allowed).",
        )

        self.parser.add_argument(
            "--length",
            type=str,
            help="Length range in the format min-max, e.g., 50-100.",
        )

        self.parser.add_argument(
            "--percentile",
            type=float,
            help="Speed percentile value (between 0 and 1). Default is 0.99.",
        )

        self.parser.add_argument(
            "--date_start", type=str, help="Start date in YYYY-MM-DD format."
        )

        self.parser.add_argument(
            "--date_end", type=str, help="End date in YYYY-MM-DD format."
        )

        self.parser.add_argument(
            "--hour_start",
            type=str,
            help="Start of hour constraints (24 hour timekeeping - HH:MM, no AM/PM)",
        )
        self.parser.add_argument(
            "--hour_end",
            type=str,
            help="End of hour constraints (24 hour timekeeping - HH:MM, no AM/PM)",
        )

    def parse(self):
        return self.parser.parse_args()
