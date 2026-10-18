from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ReplaySelection:
    dataset_id: str
    split: str
    fault_number: int
    simulation_run: int
    speed: float = 30.0

    def __post_init__(self):
        if self.speed <= 0 or self.speed > 1000:
            raise ValueError("Replay speed must be greater than 0 and at most 1000")
        if self.fault_number < 0 or self.simulation_run < 1:
            raise ValueError("Invalid fault or simulation-run identity")

@dataclass(frozen=True)
class TelemetryPoint:
    tag_id: str
    value: float
    source_timestamp: datetime
    quality: str
    sample: int
    fault_number: int
    simulation_run: int
