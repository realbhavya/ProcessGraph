from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
EXPECTED=["faultNumber","simulationRun","sample"]+[f"xmeas_{i}" for i in range(1,42)]+[f"xmv_{i}" for i in range(1,12)]

def normalize_columns(frame:pd.DataFrame)->pd.DataFrame:
 aliases={str(c):str(c).strip().replace('.', '_') for c in frame.columns}; frame=frame.rename(columns=aliases)
 lower={c.lower():c for c in frame.columns}
 ren={}
 for required in EXPECTED:
  found=lower.get(required.lower())
  if found: ren[found]=required
 frame=frame.rename(columns=ren)
 missing=[x for x in EXPECTED if x not in frame.columns]
 if missing: raise ValueError(f"Dataset schema missing {len(missing)} columns: {missing[:8]}")
 return frame[EXPECTED].copy()

def read_source(path:Path)->pd.DataFrame:
 suffix=path.suffix.lower()
 if suffix=='.csv': return normalize_columns(pd.read_csv(path))
 if suffix in {'.rdata','.rda'}:
  import pyreadr
  objects=pyreadr.read_r(str(path)); frames=[x for x in objects.values() if isinstance(x,pd.DataFrame)]
  if len(frames)!=1: raise ValueError(f"Expected exactly one data frame in {path.name}, found {len(frames)}")
  return normalize_columns(frames[0])
 raise ValueError(f"Unsupported source format: {path.suffix}")

def infer_split(path:Path)->str:
 name=re.sub(r'[^a-z]+','_',path.stem.lower())
 return ('fault_free_' if 'fault_free' in name else 'faulty_')+('training' if 'train' in name else 'testing')
