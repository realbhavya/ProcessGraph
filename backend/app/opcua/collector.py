from __future__ import annotations
import asyncio,logging,os
from datetime import UTC,datetime
from asyncua import Client,ua
from app.opcua.contracts import TelemetryPoint
from app.opcua.repository import LiveObservationRepository
log=logging.getLogger("processgraph.opcua.collector")
class Handler:
    def __init__(self,repo,endpoint,dataset,split,consumer,fault,run): self.repo=repo; self.endpoint=endpoint; self.dataset=dataset; self.split=split; self.consumer=consumer; self.fault=fault; self.run=run; self.sequence=0
    async def datachange_notification(self,node,val,data):
        self.sequence+=1; tag=str(node.nodeid.Identifier); monitored=data.monitored_item.Value
        source=monitored.SourceTimestamp or datetime.now(UTC); server=monitored.ServerTimestamp or datetime.now(UTC); quality=str(monitored.StatusCode)
        point=TelemetryPoint(tag,float(val),source,quality,self.sequence,self.fault,self.run)
        # Replay identity is read from endpoint configuration; sample/run enrichment is added in M13 event correlation.
        self.repo.write(self.endpoint,self.dataset,self.split,point,server,self.sequence); self.repo.offset(self.consumer,self.endpoint,self.sequence)
class Collector:
    def __init__(self,dsn,endpoint,dataset,split,consumer="processgraph-opcua-collector"): self.repo=LiveObservationRepository(dsn); self.endpoint=endpoint; self.dataset=dataset; self.split=split; self.consumer=consumer
    async def run(self):
        self.repo.initialize(); delay=1.0
        while True:
            try:
                async with Client(url=self.endpoint,timeout=10) as client:
                    index=await client.get_namespace_index("urn:processgraph:sentinel:tep"); tags=client.get_node(ua.NodeId("TEP.XMEAS.01",index)).get_parent
                    root=client.get_node(ua.NodeId("TEP.XMEAS.01",index)); parent=await root.get_parent(); children=await parent.get_children()
                    handler=Handler(self.repo,self.endpoint,self.dataset,self.split,self.consumer,int(os.getenv("REPLAY_FAULT_NUMBER","1")),int(os.getenv("REPLAY_SIMULATION_RUN","1"))); sub=await client.create_subscription(500,handler); await sub.subscribe_data_change(children)
                    delay=1.0
                    while True: await asyncio.sleep(5); await client.check_connection()
            except asyncio.CancelledError: raise
            except Exception as exc: log.warning("OPC UA connection lost: %s; retrying in %.1fs",exc,delay); await asyncio.sleep(delay); delay=min(delay*2,30)
if __name__=="__main__": logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO")); asyncio.run(Collector(os.environ["TIMESERIES_DSN"],os.getenv("OPCUA_ENDPOINT","opc.tcp://opcua-replay:4840/processgraph/tep/"),os.getenv("REPLAY_DATASET_ID","rieth-tep-2017"),os.getenv("REPLAY_SPLIT","faulty_testing")).run())
