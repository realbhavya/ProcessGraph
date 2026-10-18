import asyncio,os
from asyncua import Client,ua
from app.opcua.contracts import ReplaySelection
from app.opcua.server import TepReplayServer

async def main():
 selection=ReplaySelection('rieth-tep-2017','fault_free_training',0,1,1000)
 endpoint='opc.tcp://0.0.0.0:4841/processgraph/test/'
 server=TepReplayServer(os.environ['TIMESERIES_DSN'],endpoint,selection); await server.initialize()
 async with server.server:
  task=asyncio.create_task(server.replay()); await asyncio.sleep(.5)
  async with Client('opc.tcp://127.0.0.1:4841/processgraph/test/') as client:
   idx=await client.get_namespace_index('urn:processgraph:sentinel:tep'); node=client.get_node(ua.NodeId('TEP.XMEAS.09',idx)); value=await node.read_value(); access=await node.read_attribute(ua.AttributeIds.UserAccessLevel)
   assert isinstance(value,float); assert not (int(access.Value.Value)&int(ua.AccessLevel.CurrentWrite.value))
  await task
 print('[M12] OPC UA read-only replay smoke passed')
asyncio.run(main())
