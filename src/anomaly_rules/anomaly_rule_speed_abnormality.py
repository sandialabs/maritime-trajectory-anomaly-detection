#  ___________________________________________________________________________
#  Copyright (c) 2025
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________


def detect_speed_abnormality(traj_points):
    """
    Implements speed abnormality rule by Hu et al. 2022 (https://ieeexplore.ieee.org/document/9759236)
    Compares the average ship speed between the ith and (i+1)th AIS data points
    for a given trajectory. If the average ship speed > 2*(speed at the ith point),
    then the ith AIS data point is considered abnormal and the trajectory will be
    classified as anomalous.
    -------------------------------------------------------------------------------
    INPUTS:
    traj_points = pandas dataframe containing the AIS points for a trajectory

    Outputs:
    anomalous = 0 if no speed abnormalities are detected, 1 if speed abnormalities are detected
    speed_abnormality_indices = integer indices for the rows of traj_points found to be anomalous
    """
    print("Speed abnormality rule hit.")
    # For the given trajectory, loop through and evaluate consecutive AIS data points
    speed_abnormality_indices = []
    for j in range(0, len(traj_points) - 1):
        # Obtain the ship's displacement, in km, between consecutive points
        dist_btwn_pts_column = traj_points.columns.get_loc("distances_km")
        dist_btwn_pts = traj_points.iloc[j + 1, dist_btwn_pts_column]

        # Compute the change in time in seconds between the jth and (j+1)th point and then convert to hours
        timecol = traj_points.columns.get_loc("datetime_hst")
        timej = traj_points.iloc[j, timecol]
        time_btwn_pts = traj_points.iloc[j + 1, timecol] - timej
        time_btwn_pts = time_btwn_pts.total_seconds() / 3600
        if time_btwn_pts == 0:
            continue

        # Compute the average ship speed between the jth and (j+1)th point (km/hr to knots)
        avg_speed = dist_btwn_pts / time_btwn_pts / 1.852

        # Obtain the jth instantaneous speed
        speed_col_index = traj_points.columns.get_loc("speed_over_ground_knots")
        speedj = traj_points.iloc[j, speed_col_index]

        # Compare the avg ship speed to the jth instantaneous speed.
        if avg_speed > 2 * speedj:
            speed_abnormality_indices.append(j)

    if len(speed_abnormality_indices) == 0:
        anomalous = 0
        return anomalous
    else:
        anomalous = 1
        return (anomalous, speed_abnormality_indices)
