from __future__ import annotations

import json

import psycopg

DDL = """
CREATE TABLE IF NOT EXISTS datasets(
    dataset_id text PRIMARY KEY,
    title text NOT NULL,
    persistent_id text NOT NULL,
    repository text NOT NULL,
    license text NOT NULL,
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS source_files(
    file_id bigserial PRIMARY KEY,
    dataset_id text NOT NULL REFERENCES datasets(dataset_id),
    split text NOT NULL,
    filename text NOT NULL,
    sha256 text NOT NULL,
    size_bytes bigint NOT NULL,
    UNIQUE(dataset_id, sha256)
);
CREATE TABLE IF NOT EXISTS tags(
    tag_id text PRIMARY KEY,
    source_column text NOT NULL UNIQUE,
    kind text NOT NULL,
    description text NOT NULL,
    engineering_unit text
);
CREATE TABLE IF NOT EXISTS process_observations(
    dataset_id text NOT NULL REFERENCES datasets(dataset_id),
    split text NOT NULL,
    fault_number integer NOT NULL,
    simulation_run integer NOT NULL,
    sample integer NOT NULL,
    event_time_seconds bigint NOT NULL,
    tag_id text NOT NULL REFERENCES tags(tag_id),
    value double precision NOT NULL,
    quality text NOT NULL DEFAULT 'GOOD',
    source_file_sha256 text NOT NULL,
    PRIMARY KEY(dataset_id, split, fault_number, simulation_run, sample, tag_id)
);
CREATE INDEX IF NOT EXISTS ix_observations_tag_time
    ON process_observations(tag_id, event_time_seconds);
CREATE INDEX IF NOT EXISTS ix_observations_run
    ON process_observations(dataset_id, split, fault_number, simulation_run, sample);
"""


class RealDataStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def initialize(self) -> None:
        with psycopg.connect(self.dsn) as connection:
            connection.execute(DDL)

    def register(self, manifest: dict, tags: list[dict]) -> None:
        with psycopg.connect(self.dsn) as connection:
            connection.execute(
                """
                INSERT INTO datasets(
                    dataset_id, title, persistent_id, repository, license, manifest
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT(dataset_id) DO UPDATE
                SET title = excluded.title,
                    persistent_id = excluded.persistent_id,
                    repository = excluded.repository,
                    license = excluded.license,
                    manifest = excluded.manifest
                """,
                (
                    manifest["dataset_id"],
                    manifest["title"],
                    manifest["persistent_id"],
                    manifest["repository"],
                    manifest["license"],
                    json.dumps(manifest),
                ),
            )
            # Psycopg 3 exposes executemany on Cursor, not Connection.
            # Keep all tag registration in this transaction so a partial tag
            # dictionary can never be committed.
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO tags(
                        tag_id, source_column, kind, description, engineering_unit
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT(tag_id) DO UPDATE
                    SET source_column = excluded.source_column,
                        kind = excluded.kind,
                        description = excluded.description,
                        engineering_unit = excluded.engineering_unit
                    """,
                    [
                        (
                            tag["canonical_tag"],
                            tag["source_column"],
                            tag["kind"],
                            tag["description"],
                            tag["unit"],
                        )
                        for tag in tags
                    ],
                )

    def register_file(self, dataset_id, split, path, sha) -> None:
        with psycopg.connect(self.dsn) as connection:
            connection.execute(
                """
                INSERT INTO source_files(
                    dataset_id, split, filename, sha256, size_bytes
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(dataset_id, sha256) DO UPDATE
                SET split = excluded.split,
                    filename = excluded.filename,
                    size_bytes = excluded.size_bytes
                """,
                (dataset_id, split, path.name, sha, path.stat().st_size),
            )

    def write_long(self, rows: list[tuple]) -> None:
        if not rows:
            return
        with psycopg.connect(self.dsn) as connection:
            # The cursor owns batched execution in Psycopg 3. ON CONFLICT keeps
            # re-imports idempotent at the observation primary key.
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO process_observations(
                        dataset_id, split, fault_number, simulation_run, sample,
                        event_time_seconds, tag_id, value, source_file_sha256
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    rows,
                )
