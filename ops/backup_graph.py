from datetime import UTC,datetime
import json,os
from pathlib import Path
from falkordb import FalkorDB
g=FalkorDB(host=os.getenv('FALKORDB_HOST','localhost'),port=int(os.getenv('FALKORDB_PORT','6379')),password=os.getenv('FALKORDB_PASSWORD')).select_graph(os.getenv('FALKORDB_GRAPH_NAME','processgraph'))
rows=g.ro_query("MATCH (n) RETURN labels(n), properties(n) ORDER BY coalesce(n.id,'')").result_set
out=Path(os.getenv('BACKUP_PATH','graph-backup.json')); out.write_text(json.dumps({'created_at':datetime.now(UTC).isoformat(),'graph':os.getenv('FALKORDB_GRAPH_NAME','processgraph'),'nodes':[{'labels':r[0],'properties':r[1]} for r in rows]},indent=2,default=str)); print(out)
