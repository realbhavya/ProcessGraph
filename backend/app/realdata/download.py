from __future__ import annotations
import hashlib,json,shutil,urllib.request,zipfile
from datetime import UTC,datetime
from pathlib import Path
from app.realdata.manifest import load_manifest

def download_dataset(manifest_path:Path,destination:Path,timeout:int=180)->Path:
 manifest=load_manifest(manifest_path); destination.mkdir(parents=True,exist_ok=True)
 archive=destination/f"{manifest.dataset_id}.zip"; tmp=archive.with_suffix('.part')
 request=urllib.request.Request(manifest.access_api,headers={'User-Agent':'ProcessGraph-Sentinel/1.0 real-data importer'})
 try:
  with urllib.request.urlopen(request,timeout=timeout) as response,tmp.open('wb') as target: shutil.copyfileobj(response,target)
  if not zipfile.is_zipfile(tmp): raise ValueError('Dataverse response is not a ZIP archive; dataset may require manual access')
  tmp.replace(archive)
  with zipfile.ZipFile(archive) as zf: zf.extractall(destination/'extracted')
  receipt={'dataset_id':manifest.dataset_id,'persistent_id':manifest.persistent_id,'downloaded_at':datetime.now(UTC).isoformat(),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'size_bytes':archive.stat().st_size,'url':manifest.access_api}
  (destination/'download-receipt.json').write_text(json.dumps(receipt,indent=2))
  return archive
 finally:
  tmp.unlink(missing_ok=True)
