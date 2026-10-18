from __future__ import annotations
import pandas as pd
from app.realdata.readers import EXPECTED

def validate_frame(frame:pd.DataFrame)->dict:
 invalid_identity=int(frame[['faultNumber','simulationRun','sample']].isna().any(axis=1).sum())
 duplicate=int(frame.duplicated(['faultNumber','simulationRun','sample']).sum())
 values=frame[EXPECTED[3:]]
 non_numeric=int(values.apply(pd.to_numeric,errors='coerce').isna().sum().sum())
 return {'rows':len(frame),'invalid_identity_rows':invalid_identity,'duplicate_identity_rows':duplicate,'non_numeric_values':non_numeric,'faults':sorted(int(x) for x in frame.faultNumber.dropna().unique()),'runs':int(frame[['faultNumber','simulationRun']].drop_duplicates().shape[0]),'valid':invalid_identity==0 and duplicate==0 and non_numeric==0}
