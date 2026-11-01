# Human Activity Recognition with a Hidden Markov Model

An HMM (implemented from scratch with NumPy) infers four hidden activities
(standing, walking, jumping, still) from phone accelerometer + gyroscope recordings.

## Repository layout

```
HMM_activity_recognition.ipynb   main notebook (data loading, features, HMM, Viterbi, Baum-Welch, evaluation)
data/clips/train/                converted single-activity training clips (standing_01.csv, ...)
data/clips/test/                 converted single-activity TEST clips (recorded in a different place/day)
data/train/                      written by make_sequences.py: training clips + chained seq files
data/test/                       written by make_sequences.py: chained test files (never used for training)
raw/                             raw Sensor Logger exports
scripts/convert_sensor_logger.py CLI to turn a Sensor Logger export into a clean CSV
scripts/make_sequences.py        joins single clips into chained, labelled recordings
figures/                         plots + metrics_table.csv written by the notebook

```

## CSV format

Columns: `time` (s), `ax, ay, az`, `gx, gy, gz`, and for chained recordings a per-row `label`.
Single-activity files are named `standing_01.csv`, `walking_02.csv`, `jumping_03.csv`, `still_04.csv`, ...
Chained files are named `seq_01.csv` and contain a `label` column.

## Run

```
pip install -r requirements.txt
jupyter notebook HMM_activity_recognition.ipynb      # Run All
```

## Workflow

```
# each Sensor Logger export zip is located in raw/train/<activity>/ or raw/test/<activity>/
python scripts/convert_all.py --trim 1.5 --trim-test 1.0                              # converts everything at once
python scripts/make_sequences.py --clips data/clips/train --out data/train --n 5 --copy-singles
python scripts/make_sequences.py --clips data/clips/test  --out data/test  --n 2 --seed 7
jupyter notebook HMM_activity_recognition.ipynb
```

## Sensor notes

- The acceleration channel used is Sensor Logger's `TotalAcceleration.csv` (accelerometer including gravity, m/s²), together with `Gyroscope.csv` (rad/s).
  `Accelerometer.csv` has gravity removed on Android, which would hide the phone's orientation.
- Recorded on a Samsung Galaxy A33; the requested 100 Hz was delivered as about 62 Hz; every clip is resampled to 50 Hz.
