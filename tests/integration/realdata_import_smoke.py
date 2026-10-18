import csv,os,tempfile
from pathlib import Path
from app.realdata.importer import import_dataset
from app.realdata.readers import EXPECTED
root=Path('/workspace'); tmp=Path(tempfile.mkdtemp(prefix='tep-contract-fixture-')); source=tmp/'fault_free_training.csv'
with source.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=EXPECTED); w.writeheader()
 for sample in (1,2): w.writerow({**{'faultNumber':0,'simulationRun':1,'sample':sample},**{x:float(sample) for x in EXPECTED[3:]}})
summary=import_dataset(root/'realdata/manifests/rieth_tep.json',root/'realdata/mappings/tep_tags.json',tmp,os.environ['TIMESERIES_DSN'])
assert summary.files==1 and summary.runs==1 and summary.observations==104
print('[M11] real-data importer contract smoke passed')
