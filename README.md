# Maritime Trajectory Anomaly Detection

## Purpose
This codebase is a benchmarking suite focused on artificially generated anomaly
detection algorithms. 

Maritime Trajectory Anomaly Detection is extremely difficult for a vast number
of reasons, the most prevelent of which is the lack of expert labeled ground
truth data. Without a source of expert labeled ground truth, researchers have
to either insert synthetic anomalies into unlabeled data or implement
unsurpervised algorithms without any way to validate the results. There is no
standard way of inserting anomalies, however, and implementations of inserting
different types of anomalies often lack realism. This codebase works to
address those issues by not only providing a consistent way for researchers
to generate different types of anomalies, but also taking a more nuanced
approach to synthetic anomaly generation so that they more closely mirror
real anomalous behavior. Creating a standard for the field as well as making
anomalies more realistic gives researchers the opportunity to develop
algorithms that work well on real data and can be reproduced and validated
(as well as built upon and improved) by others working in this space.    

## Installation

> [!IMPORTANT]
> Note that Python 3.10 or higher is required for this package.

We recommend creating a virtual environment before installation and usage.

### For Mac/Linux
    ```
    python -m venv maritime_benchmark_env
    source maritime_benchmark_env/bin/activate
    # Run in the root directory
    pip install .
    ```

### For Windows
    ```
    python -m venv maritime_benchmark_env
    maritime_benchmark_env\Scripts\activate
    # Run in the root directory
    pip install .
    ```

## Data

### 1. Download the HawaiiCoast_GT Data Set

This package was created for use with the HawaiiCoast_GT dataset.
The dataset is available for download via Zenodo:
[https://zenodo.org/records/8253611](https://zenodo.org/records/8253611)

### 2. Unzip and Move the AIS data files

Move all `.csv` files from the `AIS_data` folder into the [data](./data)
folder. Below is an example command for moving these files:

```
mv Downloads/HawaiiCoast_GT/AIS_data/* maritime/data
```

### Alternative Datasets

If you would like to use other AIS data, please ensure that the data structure
matches that of the HawaiiCoast_GT dataset.

If you are using flags in your run command, ensure that the "Hawaii_GT" is
followed by "false". If not, make sure to respond false to the Hawaii_GT
prompt and specify a valid file name that is in the data folder.

## Usage

The simplest run command is:

```
# Linux/MacOS
python src/main.py
# Windows
python src\main.py
```

Running this way, you'll be prompted for required parameters.

### Runtime Parameters

1. `Hawaii_GT` - Flag to indicate whether you are using Hawaii_GT data (True/False)
   - If set to False, must specify alternative `AIS_file_name`
2. `vessel_class` - Vessel class(es) on which to filter (e.g., cargo, diving)
3. `length` - Length range of vessels on which to filter (e.g., 10-100)
4. `date_start` - Beginning date on which to filter (e.g., 2018-01-01)
5. `date_end` - End date on which to filter (e.g., 2018-01-31)
6. `hour_start` - Beginning time constraint on which to filter (e.g., 13:30)
7. `hour_end` - End time constraint on which to filter (e.g., 15:45)

You can alternatively directly use the parameter flags rather than go through
the prompts.

```
  --anomaly_type {overspeed}
                        Type of anomaly to detect (choose one).
  --Hawaii_GT HAWAII_GT
                        Whether to use Hawaii GT data (True or False).
  --AIS_file_name AIS_FILE_NAME
                        Name of the AIS file (without extension).
  --vessel_class {cargo,diving,fishing,industrial vessel,military,offshore supply vessel,oil recovery,other,passenger,pilot vessel,pleasure craft/sailing,port tender,public vessel, unclassified,research vessel,school ship,search and rescue vessel,tanker,tug tow} [{cargo,diving,fishing,industrial vessel,military,offshore supply vessel,oil recovery,other,passenger,pilot vessel,pleasure craft/sailing,port tender,public vessel, unclassified,research vessel,school ship,search and rescue vessel,tanker,tug tow} ...]
                        Vessel classes (multiple allowed).
  --length LENGTH       Length range in the format min-max, e.g., 50-100.
  --percentile PERCENTILE
                        Speed percentile value (between 0 and 1). Default is 0.98.
  --date_start DATE_START
                        Start date in YYYY-MM-DD format.
  --date_end DATE_END   End date in YYYY-MM-DD format.
  --hour_start HOUR_START
                        Start of hour constraints (24 hour timekeeping - HH:MM, no AM/PM)
  --hour_end HOUR_END   End of hour constraints (24 hour timekeeping - HH:MM, no AM/PM)
```

Below is an example command with complete and valid params specified through flags.

```
python src/main.py --anomaly_type overspeed --Hawaii_GT true --vessel_class cargo --length 200-300 --percentile 0.98 --date_start 2017-01-01 --date_end 2017-03-15 --hour_start 6:00 --hour_end 18:00
```

## Finding the Output

Your output can be found in the [output](./output) folder. Output files
will be in `.csv` format and will be timestamped based on when the
corresponding run was completed.


## Acknowledgements

### Primary Developer

Maisy Dunlavy (ORCID: [0009-0009-6007-2325](https://orcid.org/0009-0009-6007-2325))

### Project Contributors

- Amelia Henriksen (ORCID: [0000-0001-5042-8417](https://orcid.org/0000-0001-5042-8417))
- Miranda Mundt (ORCID: [0000-0002-5283-2138](https://orcid.org/0000-0002-5283-2138))
- Elizabeth Newman (ORCID: [0000-0002-6309-7706](https://orcid.org/0000-0002-6309-7706))
- Chelsea Drum (ORCID: [0009-0009-7087-1569](https://orcid.org/0009-0009-7087-1569))

### Funding

This project was funded by Sandia National Laboratories. Sandia National
Laboratories is a multimission laboratory managed and operated by National
Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidiary
of Honeywell International Inc., for the U.S. Department of Energy’s
National Nuclear Security Administration under contract DE-NA0003525.

## License Terms

By contributing to this software project, you are agreeing to the
following terms and conditions for your contributions:

1. You agree your contributions are submitted under the BSD license.
2. You represent you are authorized to make the contributions and grant
   the license. If your employer has rights to intellectual property that
   includes your contributions, you represent that you have received
   permission to make contributions and grant the required license on
   behalf of that employer.
