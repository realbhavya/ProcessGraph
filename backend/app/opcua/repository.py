from __future__ import annotations
from datetime import UTC, datetime, timedelta
import psycopg
from app.opcua.contracts import ReplaySelection, TelemetryPoint

LIVE_DDL = """
CREATE TABLE IF NOT EXISTS live_observations(
    source_endpoint text NOT NULL,
    dataset_id text NOT NULL,
    split text NOT NULL,
    fault_number integer NOT NULL,
    simulation_run integer NOT NULL,
    sample integer NOT NULL,
    tag_id text NOT NULL,
    source_timestamp timestamptz NOT NULL,
    server_timestamp timestamptz NOT NULL,
    ingestion_timestamp timestamptz NOT NULL DEFAULT now(),
    value double precision NOT NULL,
    quality text NOT NULL,
    sequence_number bigint NOT NULL,
    PRIMARY KEY(source_endpoint, dataset_id, split, fault_number, simulation_run, sample, tag_id)
);
CREATE INDEX IF NOT EXISTS ix_live_tag_timestamp ON live_observations(tag_id, source_timestamp DESC);
CREATE TABLE IF NOT EXISTS ingestion_offsets(
    consumer_id text PRIMARY KEY,
    source_endpoint text NOT NULL,
    sequence_number bigint NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
"""

class ReplayRepository:
    def __init__(self, dsn: str): self.dsn=dsn
    def tags(self)->list[dict]:
        with psycopg.connect(self.dsn) as c:
            rows=c.execute("SELECT tag_id,description,engineering_unit,kind FROM tags ORDER BY tag_id").fetchall()
        return [{"tag_id":r[0],"description":r[1],"unit":r[2],"kind":r[3]} for r in rows]
    def samples(self, selection:ReplaySelection):
        query="""
        SELECT sample,event_time_seconds,tag_id,value
        FROM process_observations
        WHERE dataset_id=%s AND split=%s AND fault_number=%s AND simulation_run=%s
        ORDER BY sample,tag_id
        """
        with psycopg.connect(self.dsn) as c:
            rows=c.execute(query,(selection.dataset_id,selection.split,selection.fault_number,selection.simulation_run)).fetchall()
        if not rows: raise ValueError("Selected real-data run does not exist")
        origin=datetime.now(UTC); current=None; points=[]
        for sample,seconds,tag,value in rows:
            if current is not None and sample!=current:
                yield current,points; points=[]
            current=sample; points.append(TelemetryPoint(tag,float(value),origin+timedelta(seconds=int(seconds)),"GOOD",int(sample),selection.fault_number,selection.simulation_run))
        if points: yield current,points

class LiveObservationRepository:
    def __init__(self,dsn:str): self.dsn=dsn
    def initialize(self):
        with psycopg.connect(self.dsn) as c: c.execute(LIVE_DDL)
    def write(self,endpoint,dataset_id,split,point,server_timestamp,sequence):
        with psycopg.connect(self.dsn) as c:
            c.execute("""
            INSERT INTO live_observations(source_endpoint,dataset_id,split,fault_number,simulation_run,sample,tag_id,source_timestamp,server_timestamp,value,quality,sequence_number)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO UPDATE SET source_timestamp=excluded.source_timestamp,server_timestamp=excluded.server_timestamp,ingestion_timestamp=now(),value=excluded.value,quality=excluded.quality,sequence_number=excluded.sequence_number
            """,(endpoint,dataset_id,split,point.fault_number,point.simulation_run,point.sample,point.tag_id,point.source_timestamp,server_timestamp,point.value,point.quality,sequence))
    def offset(self,consumer_id,endpoint,sequence):
        with psycopg.connect(self.dsn) as c:
            c.execute("""INSERT INTO ingestion_offsets(consumer_id,source_endpoint,sequence_number) VALUES(%s,%s,%s) ON CONFLICT(consumer_id) DO UPDATE SET source_endpoint=excluded.source_endpoint,sequence_number=GREATEST(ingestion_offsets.sequence_number,excluded.sequence_number),updated_at=now()""",(consumer_id,endpoint,sequence))
