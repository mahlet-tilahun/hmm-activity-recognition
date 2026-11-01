#!/usr/bin/env python3
"""Build chained multi-activity recordings (seq_XX.csv) by joining single-activity clips.

Usage:
  # training: copies your single clips into data/train and adds 5 chained files
  python scripts/make_sequences.py --clips data/clips/train --out data/train --n 5 --copy-singles
  # test: builds 2 chained files from clips that are NEVER used for training
  python scripts/make_sequences.py --clips data/clips/test --out data/test --n 2 --seed 7

"""
import argparse, glob, os, shutil, random
import numpy as np, pandas as pd

ACTS = ["standing", "walking", "jumping", "still"]
COLS = ["ax", "ay", "az", "gx", "gy", "gz"]
PATTERNS = [["still", "standing", "walking", "jumping", "walking", "standing", "still"],
            ["standing", "walking", "standing", "still", "standing", "jumping", "walking"],
            ["still", "standing", "walking", "jumping", "standing", "walking", "still"]]

def resample(path, fs):
    df = pd.read_csv(path).rename(columns={"timestamp": "time"})
    t = df["time"].values.astype(float)
    tn = np.arange(t[0], t[-1], 1 / fs)
    out = pd.DataFrame({"time": tn - tn[0]})
    for c in COLS: out[c] = np.interp(tn, t, df[c].values)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=3); ap.add_argument("--fs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--copy-singles", action="store_true")
    a = ap.parse_args(); rnd = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    pools = {act: sorted(glob.glob(os.path.join(a.clips, f"{act}_*.csv"))) for act in ACTS}
    for act, p in pools.items():
        print(f"{act:9s}: {len(p)} clips")
        if not p: raise SystemExit(f"No clips found for '{act}' in {a.clips}")
    if a.copy_singles:
        for p in sum(pools.values(), []): shutil.copy(p, a.out)
        print("copied single clips to", a.out)
    for k in range(a.n):
        pattern, used, parts, offset = PATTERNS[k % len(PATTERNS)], {}, [], 0.0
        for act in pattern:
            left = [p for p in pools[act] if p not in used.get(act, [])]
            if not left:
                print(f"  note: reusing a '{act}' clip in seq_{k+1:02d} (record more clips for more variety)"); left = pools[act]
            pick = rnd.choice(left); used.setdefault(act, []).append(pick)
            df = resample(pick, a.fs); df["time"] += offset; offset = df["time"].iloc[-1] + 1 / a.fs
            df["label"] = act; parts.append(df)
        out = pd.concat(parts, ignore_index=True)
        path = os.path.join(a.out, f"seq_{k+1:02d}.csv"); out.to_csv(path, index=False)
        print(f"wrote {path}: {len(out)/a.fs:.0f} s  ({' > '.join(pattern)})")

if __name__ == "__main__":
    main()
