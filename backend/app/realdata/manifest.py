import json
from pathlib import Path
from app.realdata.contracts import DatasetManifest

def load_manifest(path:Path)->DatasetManifest:
 d=json.loads(path.read_text(encoding='utf-8'))
 required={'dataset_id','title','persistent_id','repository','license','access_api','sampling_interval_seconds','expected_variables','identity_columns','expected_source_files','provenance'}
 missing=required-set(d)
 if missing: raise ValueError(f"Manifest missing fields: {sorted(missing)}")
 if d['provenance'].get('is_live_commercial_plant_data') is not False: raise ValueError('Public benchmark must not be represented as live plant data')
 return DatasetManifest(d['dataset_id'],d['title'],d['persistent_id'],d['repository'],d['license'],d['access_api'],int(d['sampling_interval_seconds']),int(d['expected_variables']),tuple(d['identity_columns']),tuple(d['expected_source_files']))
