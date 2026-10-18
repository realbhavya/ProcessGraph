from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str; title: str; persistent_id: str; repository: str; license: str
    access_api: str; sampling_interval_seconds: int; expected_variables: int
    identity_columns: tuple[str,...]; expected_source_files: tuple[str,...]

@dataclass(frozen=True)
class SourceFile:
    path: Path; split: str; sha256: str; size_bytes: int

@dataclass(frozen=True)
class ImportSummary:
    dataset_id: str; files: int; runs: int; observations: int; rejected_rows: int
    report_path: str
