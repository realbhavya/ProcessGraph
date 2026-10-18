from __future__ import annotations
import asyncio, json, logging, os
from datetime import UTC,datetime
from asyncua import Server, ua
from app.opcua.contracts import ReplaySelection
from app.opcua.repository import ReplayRepository
log=logging.getLogger("processgraph.opcua.server")
NAMESPACE="urn:processgraph:sentinel:tep"

class TepReplayServer:
    def __init__(self,dsn,endpoint,selection):
        self.repository=ReplayRepository(dsn); self.endpoint=endpoint; self.selection=selection; self.server=Server(); self.variables={}; self.sequence=0
    async def initialize(self):
        await self.server.init(); self.server.set_endpoint(self.endpoint); self.server.set_server_name("ProcessGraph Sentinel TEP Replay")
        index=await self.server.register_namespace(NAMESPACE); root=await self.server.nodes.objects.add_object(index,"TennesseeEastmanProcess")
        meta=await root.add_object(index,"ReplayMetadata")
        for name,value in {"DatasetId":self.selection.dataset_id,"Split":self.selection.split,"FaultNumber":self.selection.fault_number,"SimulationRun":self.selection.simulation_run,"SourceType":"published-benchmark-replay","ReadOnly":True}.items(): await meta.add_variable(ua.NodeId(f"TEP.Meta.{name}",index),name,value)
        tags_root=await root.add_object(index,"Tags")
        for tag in self.repository.tags():
            node=await tags_root.add_variable(ua.NodeId(tag['tag_id'],index),tag['tag_id'],0.0,ua.VariantType.Double)
            await node.add_property(index,"Description",tag['description']); await node.add_property(index,"EngineeringUnit",tag['unit'] or ""); await node.add_property(index,"Kind",tag['kind'])
            self.variables[tag['tag_id']]=node
    async def replay(self):
        previous=None
        for sample,points in self.repository.samples(self.selection):
            if previous is not None:
                await asyncio.sleep(max(0,(points[0].source_timestamp-previous).total_seconds()/self.selection.speed))
            self.sequence+=1
            for point in points:
                dv=ua.DataValue(ua.Variant(point.value,ua.VariantType.Double)); dv.SourceTimestamp=point.source_timestamp; dv.ServerTimestamp=datetime.now(UTC); dv.StatusCode_=ua.StatusCode(ua.StatusCodes.Good)
                await self.variables[point.tag_id].write_data_value(dv)
            previous=points[0].source_timestamp
            log.info(json.dumps({"event":"sample_published","sample":sample,"sequence":self.sequence,"points":len(points)}))
    async def run(self):
        await self.initialize()
        async with self.server:
            await self.replay()
            if os.getenv("OPCUA_HOLD_OPEN","true").lower()=="true": await asyncio.Event().wait()

def selection_from_env(): return ReplaySelection(os.getenv("REPLAY_DATASET_ID","rieth-tep-2017"),os.getenv("REPLAY_SPLIT","faulty_testing"),int(os.getenv("REPLAY_FAULT_NUMBER","1")),int(os.getenv("REPLAY_SIMULATION_RUN","1")),float(os.getenv("REPLAY_SPEED","180")))
if __name__=="__main__": logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO")); asyncio.run(TepReplayServer(os.environ["TIMESERIES_DSN"],os.getenv("OPCUA_ENDPOINT","opc.tcp://0.0.0.0:4840/processgraph/tep/"),selection_from_env()).run())
