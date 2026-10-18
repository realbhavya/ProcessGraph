import pandas as pd,pytest
from app.realdata.quality import validate_frame
from app.realdata.readers import EXPECTED,normalize_columns
def frame(): return pd.DataFrame([{**{'faultNumber':0,'simulationRun':1,'sample':1},**{x:1.0 for x in EXPECTED[3:]}}])
def test_valid_tep_frame_passes_quality(): assert validate_frame(normalize_columns(frame()))['valid'] is True
def test_missing_variable_fails_schema():
 with pytest.raises(ValueError): normalize_columns(frame().drop(columns=['xmeas_9']))
def test_duplicate_identity_fails_quality():
 f=frame(); assert validate_frame(pd.concat([f,f],ignore_index=True))['valid'] is False
