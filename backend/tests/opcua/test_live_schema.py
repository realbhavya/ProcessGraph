from app.opcua.repository import LIVE_DDL
def test_live_observations_preserve_three_timestamps_and_quality():
 for x in ('source_timestamp','server_timestamp','ingestion_timestamp','quality','sequence_number'): assert x in LIVE_DDL
def test_offsets_are_persistent(): assert 'ingestion_offsets' in LIVE_DDL and 'GREATEST' in __import__('inspect').getsource(__import__('app.opcua.repository',fromlist=['LiveObservationRepository']).LiveObservationRepository.offset)
