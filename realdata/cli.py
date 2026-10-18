import argparse,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'backend'))
from app.realdata.download import download_dataset
from app.realdata.importer import import_dataset
ROOT=Path(__file__).parent
p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
d=sub.add_parser('download'); d.add_argument('--destination',type=Path,default=ROOT/'raw'/'rieth-tep-2017')
i=sub.add_parser('import'); i.add_argument('--source',type=Path,default=ROOT/'raw'/'rieth-tep-2017'/'extracted'); i.add_argument('--dsn',default=os.getenv('TIMESERIES_DSN','postgresql://processgraph:processgraph-local@localhost:5432/processgraph'))
args=p.parse_args(); manifest=ROOT/'manifests'/'rieth_tep.json'
if args.command=='download': print(download_dataset(manifest,args.destination))
else: print(import_dataset(manifest,ROOT/'mappings'/'tep_tags.json',args.source,args.dsn))
