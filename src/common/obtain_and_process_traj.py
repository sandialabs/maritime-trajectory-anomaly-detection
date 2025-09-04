#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import logging
import numpy as np
import pandas as pd
from datetime import datetime

from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="output.log",
    filemode="a",
)

timestamp = datetime.now().strftime("%d-%m-%Y")


def obtain_trajectory(
    data_dict, mmsi_val, date1, date2, primary_dt="datetime_hst", inc_date=None
):
    """
    Obtains the AIS points associated with the vessel given in mmsi_val between
    date1 and date2.

    """
    try:
        vessel_df_list = []
        dr = pd.date_range(date1, date2, freq="D")
        df_key_list = list(set(zip(dr.year, dr.month)))

        for year, month in df_key_list:
            try:
                for mmsi in mmsi_val:
                    vessel_df_list.append(data_dict[year, month].loc[mmsi])
            except KeyError:
                vessel_df_list.append(data_dict[year, month].loc[mmsi_val])

        vessel_df = pd.concat(vessel_df_list)

        points_df = vessel_df[
            (vessel_df[primary_dt] >= date1) & (vessel_df[primary_dt] <= date2)
        ].sort_values(by=primary_dt)

        return points_df
    except Exception as e:
        logging.error("Error occurred while trying to obtain trajectory: %s", e)
        raise


def extract_traj_from_df(
    AIS_points_df,
    time_col="datetime_hst",
    sep_time=np.timedelta64(30, "m"),
    min_points=5,
    min_chull_area=0.2,
):
    """
    Extracts trajectories from the AIS points DataFrame.

    """
    mmsi_list = AIS_points_df.index.unique()
    trajectory_list = []
    for mmsi in mmsi_list:
        vessel_points = AIS_points_df.loc[mmsi]
        traj_points = (
            [0]
            + list(
                np.where(
                    (
                        vessel_points[time_col].iloc[1:]
                        - vessel_points[time_col].iloc[:-1]
                    )
                    > sep_time
                )[0]
                + 1
            )
            + [vessel_points.shape[0]]
        )
        for i in range(len(traj_points) - 1):
            traj_df = vessel_points.iloc[
                traj_points[i] : traj_points[i + 1]
            ].drop_duplicates()

            if traj_df.shape[0] >= min_points:
                traj_obj = PdTrajectory(traj_df, primary_dt=time_col)
                traj_obj.get_chull_area()

                if traj_obj.chull_area > min_chull_area:
                    trajectory_list.append(traj_obj)

    final_times = [t.traj_df[time_col].iloc[-1] for t in trajectory_list]
    end_times_sortarg = list(np.argsort(final_times))
    return (
        list(np.array(trajectory_list, dtype=object)[end_times_sortarg]),
        np.array(final_times)[end_times_sortarg],
    )


class PdTrajectory:
    """
    Class representing a trajectory of a vessel based on AIS data.
    """

    def __init__(self, traj_df, primary_dt="datetime_hst"):
        """
        Initializes the trajectory object.

        traj_df: DataFrame of the AIS data associated with a given trajectory.
        primary_dt: Column name corresponding to the primary datetime for a given trajectory.

        """

        self.traj_df = traj_df.copy()
        self.npoints, self.ncol = traj_df.shape
        self.primary_dt = primary_dt
        self.get_tracktable_traj()
        self.chull_area = 0
        self.distances = False
        self.turn_angles = False

    def get_tracktable_traj(self):
        """Converts the trajectory DataFrame into a tracktable trajectory."""
        self.traj_tt = Trajectory()
        for i in range(self.npoints):
            point = TrajectoryPoint(
                self.traj_df.iloc[i]["lon"], self.traj_df.iloc[i]["lat"]
            )
            point.object_id = str(self.traj_df.index.unique()[0])
            point.timestamp = self.traj_df.iloc[i][self.primary_dt]
            self.traj_tt.append(point)

    def get_chull_area(self):
        """Calculates the convex hull area of the trajectory."""
        # Implementation of convex hull area calculation goes here
        pass

    def get_distances(self):
        """Calculates distances for the trajectory."""
        self.traj_df["Current Lengths"] = np.array(
            [self.traj_tt[i].current_length for i in range(self.npoints)]
        )
        if "distances_km" in self.traj_df.columns:
            self.total_length = np.sum(self.traj_df["distances_km"])
        else:
            self.traj_df["distances_km"] = np.array(
                [np.nan] + list(self.traj_df["Current Lengths"].iloc[1:])
            )
