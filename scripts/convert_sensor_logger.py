#!/usr/bin/env python3
"""Converts one Sensor Logger export folder into a clean CSV.
    Usage:
    python scripts/convert_sensor_logger.py raw/walk_01 data/train/walking_01.csv
    python scripts/convert_sensor_logger.py raw/chain_01 data/train/seq_01.csv --label-file raw/chain_01_labels.csv
"""
import argparse, os
import numpy as np, pandas as pd

def convert(folder, out_csv, fs=50, trim=0.5, acc_scale=1.0, label_file=None):
    # Prefer TotalAcceleration.csv (accelerometer INCLUDING gravity). On many Android phones Accelerometer.csv has gravity removed.
    acc_name = "TotalAcceleration.csv" if os.path.exists(os.path.join(folder, "TotalAcceleration.csv")) else "Accelerometer.csv"
    acc = pd.read_csv(os.path.join(folder, acc_name))
    gyr = pd.read_csv(os.path.join(folder, "Gyroscope.csv"))
    native_fs = float(1 / np.median(np.diff(acc.seconds_elapsed.values)))   # real rate the phone delivered
    t0 = max(acc.seconds_elapsed.min(), gyr.seconds_elapsed.min()) + trim
    t1 = min(acc.seconds_elapsed.max(), gyr.seconds_elapsed.max()) - trim
    t = np.arange(t0, t1, 1 / fs)
    out = {"time": t - t0}
    for df, pre, sc in ((acc, "a", acc_scale), (gyr, "g", 1.0)):
        for ax in "xyz":
            out[pre + ax] = np.interp(t, df.seconds_elapsed, df[ax] * sc)
    out = pd.DataFrame(out)
    if label_file:
        segs = pd.read_csv(label_file)
        lab = np.array([""] * len(out), dtype=object)
        for _, r in segs.iterrows():
            lab[(out.time >= r.start_s) & (out.time < r.end_s)] = r.label
        out["label"] = lab
        out = out[out.label != ""]
    out.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}: {len(out)} rows, {len(out)/fs:.1f} s at {fs} Hz (native {native_fs:.1f} Hz)")
    return native_fs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("out_csv")
    ap.add_argument("--fs", type=int, default=50)
    ap.add_argument("--trim", type=float, default=0.5, help="seconds cut from start and end")
    ap.add_argument("--acc-scale", type=float, default=1.0, help="9.81 if your accelerometer is in g")
    ap.add_argument("--label-file", default=None)
    a = ap.parse_args()
    convert(a.folder, a.out_csv, a.fs, a.trim, a.acc_scale, a.label_file)
