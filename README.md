# Human Activity Recognition with a Hidden Markov Model

An HMM (implemented from scratch with NumPy) infers four hidden activities (standing, walking, jumping, still) from phone accelerometer + gyroscope recordings. Submission for Formative 2 – Hidden Markov Models.

## Repository layout

```
HMM_activity_recognition.ipynb   main notebook (data loading, features, HMM, Viterbi, Baum-Welch, evaluation)
data/clips/train/                converted single-activity training clips (standing_01.csv, ...)
data/clips/test/                 converted single-activity TEST clips (recorded at a different location)
data/train/                      written by make_sequences.py: training clips + chained seq files
data/test/                       written by make_sequences.py: chained test files (never used for training)
raw/                             raw Sensor Logger exports
scripts/convert_all.py           converts all Sensor Logger exports in raw/ at once
scripts/convert_sensor_logger.py CLI to turn a Sensor Logger export into a clean CSV
scripts/make_sequences.py        joins single clips into chained, labelled recordings
figures/                         plots + metrics_table.csv written by the notebook
report/                          the report
```

## Proof videos

https://drive.google.com/drive/folders/1-Gn5BNXVeGn1wjRSVzAVfXMgQh5QwjZZ?usp=drive_link

## Dataset

Phone: Samsung Galaxy A33 5G, recorded with Sensor Logger. Native sampling rate 62.4 Hz, resampled to 50 Hz. Windows: 2 s, 50% overlap.

| Activity  | Training clips | Training data (s) | Test clips | Test data (s) |
| --------- | -------------- | ----------------- | ---------- | ------------- |
| Standing  | 13             | 111.7             | 3          | 25.3          |
| Walking   | 13             | 102.3             | 3          | 18.8          |
| Jumping   | 13             | 92.1              | 3          | 19.0          |
| Still     | 13             | 104.8             | 3          | 27.9          |
| **Total** | **52**         | **410.9**         | **12**     | **91.0**      |

Seconds are counted after trimming the start and end of each clip (1.5 s for training, 1.0 s for test).

### Chained recordings (built from the single clips above)

| File                                   | Length (s) |
| -------------------------------------- | ---------- |
| `data/train/seq_01.csv` – `seq_05.csv` | 54–60      |
| `data/test/seq_01.csv`, `seq_02.csv`   | 53–55      |

Windows: 608 for training and 106 for testing.

### CSV format

Columns: `time` (s), `ax, ay, az`, `gx, gy, gz`, and for chained recordings a per-row `label`. Single-activity files are named `standing_01.csv`, `walking_02.csv`, `jumping_03.csv`, `still_04.csv`, ... Chained files are named `seq_01.csv` and contain a `label` column.

## Run

```
pip install -r requirements.txt
jupyter notebook HMM_activity_recognition.ipynb      # Run All
```

### Workflow (rebuilding the data from the raw exports)

```
# each Sensor Logger export zip is located in raw/train/<activity>/ or raw/test/<activity>/
python scripts/convert_all.py --trim 1.5 --trim-test 1.0                              # converts everything at once
python scripts/make_sequences.py --clips data/clips/train --out data/train --n 5 --copy-singles
python scripts/make_sequences.py --clips data/clips/test  --out data/test  --n 2 --seed 7
jupyter notebook HMM_activity_recognition.ipynb
```

The converted data is already in the repo, so the three conversion commands can be skipped.

## Results on unseen test data

| Activity    | Test windows | Sensitivity | Specificity | Accuracy (one-vs-rest) |
| ----------- | ------------ | ----------- | ----------- | ---------------------- |
| Standing    | 42           | 0.905       | 0.938       | 0.925                  |
| Walking     | 24           | 0.875       | 0.951       | 0.934                  |
| Jumping     | 13           | 1.000       | 0.968       | 0.972                  |
| Still       | 27           | 0.852       | 1.000       | 0.962                  |
| **Overall** | **106**      |             |             | **0.896**              |

Confusion matrix (rows = true, columns = predicted):

|              | Standing | Walking | Jumping | Still |
| ------------ | -------- | ------- | ------- | ----- |
| **Standing** | 38       | 4       | 0       | 0     |
| **Walking**  | 0        | 21      | 3       | 0     |
| **Jumping**  | 0        | 0       | 13      | 0     |
| **Still**    | 4        | 0       | 0       | 23    |

All 11 errors fall within one window of an activity change.

## Sensor notes

- The acceleration channel used is Sensor Logger's `TotalAcceleration.csv` (accelerometer including gravity, m/s²), together with `Gyroscope.csv` (rad/s). `Accelerometer.csv` has gravity removed on Android, which would hide the phone's orientation.
- Recorded on a Samsung Galaxy A33 5G (SM-A336B); the requested 100 Hz was delivered as about 62 Hz; every clip is resampled to 50 Hz.
- The chained files are built by joining separate clips, so the changes between activities in them are idealised.
