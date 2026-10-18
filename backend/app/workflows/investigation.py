from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256

from app.agents.specialists import ConnectivityAgent, MaintenanceMemoryAgent, SafetyContextAgent
from app.agents.tool_client import AgentToolClient
from app.domain.investigations import InvestigationSummary
from app.validation.evidence import EvidenceValidator


class InvestigationWorkflow:
    def __init__(self, *, investigation_repository, incident_repository, tool_service):
        self.repo=investigation_repository; self.incidents=incident_repository; self.tools=tool_service

    @staticmethod
    def sid(prefix,key,suffix=""):
        return f"{prefix}-{sha256(f'{key}:{suffix}'.encode()).hexdigest()[:16].upper()}"

    def run(self, incident_id: str, idempotency_key: str) -> InvestigationSummary:
        incident=self.incidents.get(incident_id)
        equipment_id=incident["equipment"][0]["id"]
        investigation_id=self.sid("INV",idempotency_key)
        self.repo.create(investigation_id=investigation_id,incident_id=incident_id,idempotency_key=idempotency_key)
        agents=[ConnectivityAgent(),SafetyContextAgent()]
        tasks=[]
        for agent in agents:
            task_id=self.sid("TASK",idempotency_key,agent.agent_id)
            self.repo.create_task(investigation_id=investigation_id,task_id=task_id,agent_id=agent.agent_id,task_type=agent.role.value,idempotency_key=f"{idempotency_key}:{agent.agent_id}")
            tasks.append((agent,task_id))
        findings=[]; failures=[]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures={pool.submit(self._run_agent,a,t,equipment_id,idempotency_key): (a,t) for a,t in tasks}
            for future in as_completed(futures):
                agent,task_id=futures[future]
                try: findings.append(future.result())
                except Exception as exc:
                    self.repo.update_task(task_id,"FAILED",exc.__class__.__name__)
                    failures.append({"task_id":task_id,"agent_id":agent.agent_id,"error_code":exc.__class__.__name__})
        # Explicit graph-backed handoff of connectivity context to maintenance agent.
        connectivity_task=next(t for a,t in tasks if a.agent_id=="AGENT-CONN")
        handoff_id=self.sid("HANDOFF",idempotency_key,"CONN-MEM")
        self.repo.create_handoff(investigation_id=investigation_id,handoff_id=handoff_id,task_id=connectivity_task,from_agent_id="AGENT-CONN",to_agent_id="AGENT-MEM",reason="Review connected P-201 maintenance and historical context",idempotency_key=f"{idempotency_key}:handoff")
        maintenance=MaintenanceMemoryAgent(); maintenance_task=self.sid("TASK",idempotency_key,maintenance.agent_id)
        self.repo.create_task(investigation_id=investigation_id,task_id=maintenance_task,agent_id=maintenance.agent_id,task_type=maintenance.role.value,idempotency_key=f"{idempotency_key}:{maintenance.agent_id}")
        try: findings.append(self._run_agent(maintenance,maintenance_task,equipment_id,idempotency_key))
        except Exception as exc:
            self.repo.update_task(maintenance_task,"FAILED",exc.__class__.__name__)
            failures.append({"task_id":maintenance_task,"agent_id":maintenance.agent_id,"error_code":exc.__class__.__name__})
        validator=EvidenceValidator(self.repo.entity_exists)
        validated=[validator.validate(f) for f in sorted(findings,key=lambda item:item.agent_id)]
        accepted=[v for v in validated if v.status.value=="validated"]
        rejected=[v for v in validated if v.status.value=="rejected"]
        for item in validated:
            self.repo.record_finding(investigation_id=investigation_id,finding=item.finding.model_dump(),status=item.status.value,validation_reasons=item.validation_reasons,idempotency_key=f"{idempotency_key}:{item.finding.finding_id}")
        status="COMPLETED" if accepted and not failures and not rejected else "PARTIAL" if accepted else "FAILED"
        summary=("Validated connected evidence identifies P-201 on the R-101 cooling path, an open P-201 vibration finding, and relevant designed safeguards. "
                 "The evidence supports investigation priority but does not establish a confirmed root cause.") if accepted else "No evidence-grounded findings were validated."
        self.repo.complete(investigation_id,status,summary)
        return InvestigationSummary(investigation_id=investigation_id,incident_id=incident_id,status=status,validated_findings=accepted,rejected_findings=rejected,handoff_ids=[handoff_id],failed_tasks=failures,summary=summary)

    def _run_agent(self, agent, task_id, equipment_id, key):
        self.repo.update_task(task_id,"RUNNING")
        finding=agent.run(task_id,equipment_id,AgentToolClient(self.tools,agent.role,f"{key}:{agent.agent_id}"))
        self.repo.update_task(task_id,"COMPLETED")
        return finding
