from __future__ import annotations
import hashlib,json
from pathlib import Path
from app.realdata.contracts import ImportSummary
from app.realdata.manifest import load_manifest
from app.realdata.quality import validate_frame
from app.realdata.readers import infer_split,read_source
from app.realdata.store import RealDataStore

def import_dataset(manifest_path:Path,mapping_path:Path,source_dir:Path,dsn:str,batch_rows:int=10000)->ImportSummary:
 manifest=load_manifest(manifest_path); manifest_json=json.loads(manifest_path.read_text()); tags=json.loads(mapping_path.read_text())['tags']; tag_by_col={x['source_column']:x['canonical_tag'] for x in tags}
 sources=sorted([p for p in source_dir.rglob('*') if p.suffix.lower() in {'.csv','.rdata','.rda'}])
 if not sources: raise ValueError(f'No real dataset source files found in {source_dir}')
 store=RealDataStore(dsn); store.initialize(); store.register(manifest_json,tags)
 reports=[]; total=0; runs=set()
 for path in sources:
  sha=hashlib.sha256(path.read_bytes()).hexdigest(); split=infer_split(path); frame=read_source(path); report=validate_frame(frame); report.update({'file':path.name,'sha256':sha,'split':split}); reports.append(report)
  if not report['valid']: raise ValueError(f'Quality gate failed for {path.name}: {report}')
  store.register_file(manifest.dataset_id,split,path,sha)
  batch=[]
  for row in frame.itertuples(index=False):
   fault=int(row.faultNumber); run=int(row.simulationRun); sample=int(row.sample); runs.add((split,fault,run)); event_seconds=sample*manifest.sampling_interval_seconds
   for column in tag_by_col:
    batch.append((manifest.dataset_id,split,fault,run,sample,event_seconds,tag_by_col[column],float(getattr(row,column)),sha))
    if len(batch)>=batch_rows: store.write_long(batch); total+=len(batch); batch=[]
  if batch: store.write_long(batch); total+=len(batch)
 report_path=source_dir.parent/'reports'/f'{manifest.dataset_id}-quality.json'; report_path.parent.mkdir(exist_ok=True); report_path.write_text(json.dumps({'dataset_id':manifest.dataset_id,'files':reports,'observations':total},indent=2))
 return ImportSummary(manifest.dataset_id,len(sources),len(runs),total,0,str(report_path))
