from __future__ import annotations
from collections import Counter, defaultdict
from threading import RLock
from time import monotonic

class MetricsRegistry:
    """Dependency-free, thread-safe Prometheus text registry."""
    def __init__(self):
        self._lock=RLock(); self._counts=Counter(); self._durations=defaultdict(list); self.started=monotonic()
    def increment(self,name:str,labels:dict[str,str]|None=None,value:int=1):
        with self._lock: self._counts[(name,self._freeze(labels))]+=value
    def observe(self,name:str,value:float,labels:dict[str,str]|None=None):
        with self._lock: self._durations[(name,self._freeze(labels))].append(float(value))
    @staticmethod
    def _freeze(labels): return tuple(sorted((labels or {}).items()))
    @staticmethod
    def _fmt(labels): return "{"+",".join(f'{k}="{str(v).replace(chr(34), chr(92)+chr(34))}"' for k,v in labels)+"}" if labels else ""
    def render(self):
        with self._lock:
            lines=["# HELP processgraph_uptime_seconds Process uptime","# TYPE processgraph_uptime_seconds gauge",f"processgraph_uptime_seconds {monotonic()-self.started:.3f}"]
            for (name,labels),value in sorted(self._counts.items()): lines.append(f"{name}{self._fmt(labels)} {value}")
            for (name,labels),values in sorted(self._durations.items()):
                lines.extend([f"{name}_count{self._fmt(labels)} {len(values)}",f"{name}_sum{self._fmt(labels)} {sum(values):.6f}"])
            return "\n".join(lines)+"\n"

registry=MetricsRegistry()
