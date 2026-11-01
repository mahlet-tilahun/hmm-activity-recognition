#!/usr/bin/env python3
"""Converts all Sensor Logger exports in one go.
   Writes data/clips/train/standing_01.csv, ... and data/clips/test/standing_01.csv, ... (numbered in file-name order),
   and prints how many clips and seconds there is for each activity.
   Usage:
   python scripts/convert_all.py --trim 1.5 --trim-test 1.0  
"""
import argparse, os, sys, tempfile, zipfile
sys.path.insert(0, os.path.dirname(__file__))
from convert_sensor_logger import convert

ACTS = ["standing", "walking", "jumping", "still"]

def find_exports(folder):
    """Return folders containing (Total)Acceleration + Gyroscope csv files (unzipping any .zip first)."""
    tmp = tempfile.mkdtemp()
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".zip"):
            dest = os.path.join(tmp, os.path.splitext(f)[0])
            with zipfile.ZipFile(os.path.join(folder, f)) as z: z.extractall(dest)
    found = []
    for base in (folder, tmp):
        for root, _, files in os.walk(base):
            low = {x.lower() for x in files}
            if ("totalacceleration.csv" in low or "accelerometer.csv" in low) and "gyroscope.csv" in low: found.append(root)
    return sorted(found, key=lambda p: os.path.basename(p))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fs", type=int, default=50); ap.add_argument("--trim", type=float, default=0.5)
    ap.add_argument("--trim-test", type=float, default=None, help="seconds cut from each end of TEST clips (default: same as --trim)")
    ap.add_argument("--acc-scale", type=float, default=1.0)
    a = ap.parse_args()
    rates = []
    for split in ("train", "test"):
        out_dir = os.path.join("data", "clips", split); os.makedirs(out_dir, exist_ok=True)
        print(f"\n=== {split} ===")
        for act in ACTS:
            src = os.path.join("raw", split, act)
            if not os.path.isdir(src): print(f"  {act:9s}: folder {src} missing"); continue
            exps = find_exports(src)
            for i, e in enumerate(exps, 1):
                import io, contextlib
                with contextlib.redirect_stdout(io.StringIO()):
                    nfs = convert(e, os.path.join(out_dir, f"{act}_{i:02d}.csv"), a.fs, (a.trim_test if split == "test" and a.trim_test is not None else a.trim), a.acc_scale)
                rates.append(dict(split=split, activity=act, file=f"{act}_{i:02d}.csv", native_fs_hz=round(nfs, 2)))
            print(f"  {act:9s}: {len(exps)} clips converted")
    import pandas as pd
    if rates:
        df = pd.DataFrame(rates); df.to_csv(os.path.join("data", "sampling_rates.csv"), index=False)
        print(f"\nNative sampling rate of your phone: mean {df.native_fs_hz.mean():.1f} Hz (min {df.native_fs_hz.min():.1f}, max {df.native_fs_hz.max():.1f}) -> saved data/sampling_rates.csv")
    print("\nNext: python scripts/make_sequences.py ... (see README)")

if __name__ == "__main__":
    main()
