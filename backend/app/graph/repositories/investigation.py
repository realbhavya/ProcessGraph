from __future__ import annotations

from app.graph.errors import EntityNotFound
from app.graph.repositories.base import BaseRepository


class InvestigationRepository(BaseRepository):
    def create(self, *, investigation_id: str, incident_id: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "investigation.create",
            """
            MATCH (incident:Incident {tenant_id:$tenant_id, id:$incident_id})
            MERGE (investigation:Investigation {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET investigation.id=$investigation_id, investigation.status='RUNNING',
                          investigation.synthetic=true, investigation.source='runtime',
                          investigation.created_at=timestamp()
            MERGE (incident)-[:HAS_INVESTIGATION {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(investigation)
            RETURN investigation.id, investigation.status
            """,
            self.params(investigation_id=investigation_id, incident_id=incident_id, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(incident_id)
        return {"id": rows[0][0], "status": rows[0][1]}

    def create_task(self, *, investigation_id: str, task_id: str, agent_id: str, task_type: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "investigation.create_task",
            """
            MATCH (investigation:Investigation {tenant_id:$tenant_id, id:$investigation_id})
            MATCH (agent:Agent {tenant_id:$tenant_id, id:$agent_id})
            MERGE (task:Task {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET task.id=$task_id, task.task_type=$task_type, task.status='PENDING',
                          task.synthetic=true, task.source='runtime', task.created_at=timestamp()
            MERGE (investigation)-[:HAS_TASK {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(task)
            MERGE (task)-[:ASSIGNED_TO {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(agent)
            RETURN task.id, task.status
            """,
            self.params(investigation_id=investigation_id, task_id=task_id, agent_id=agent_id, task_type=task_type, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(investigation_id)
        return {"id": rows[0][0], "status": rows[0][1]}

    def update_task(self, task_id: str, status: str, error_code: str | None = None) -> None:
        self.executor.write(
            "investigation.update_task",
            """
            MATCH (task:Task {tenant_id:$tenant_id, id:$task_id})
            SET task.status=$status, task.error_code=$error_code, task.updated_at=timestamp()
            """,
            self.params(task_id=task_id, status=status, error_code=error_code),
        )

    def record_finding(self, *, investigation_id: str, finding: dict, status: str, validation_reasons: list[str], idempotency_key: str) -> dict:
        evidence_ids = [item["entity_id"] for item in finding["evidence"]]
        rows = self.executor.write(
            "investigation.record_finding",
            """
            MATCH (investigation:Investigation {tenant_id:$tenant_id, id:$investigation_id})
            MATCH (task:Task {tenant_id:$tenant_id, id:$task_id})
            MATCH (agent:Agent {tenant_id:$tenant_id, id:$agent_id})
            MERGE (finding:Finding {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET finding.id=$finding_id, finding.category=$category,
                          finding.summary=$summary, finding.confidence=$confidence,
                          finding.status=$status, finding.validation_reasons=$validation_reasons,
                          finding.limitations=$limitations, finding.synthetic=true,
                          finding.source='runtime', finding.created_at=timestamp()
            MERGE (task)-[:PRODUCED {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(finding)
            MERGE (investigation)-[:HAS_FINDING {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(finding)
            MERGE (finding)-[:PRODUCED_BY {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(agent)
            WITH finding
            UNWIND $evidence_ids AS evidence_id
            MATCH (evidence {tenant_id:$tenant_id, id:evidence_id})
            MERGE (finding)-[:SUPPORTED_BY {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(evidence)
            RETURN finding.id, finding.status
            """,
            self.params(
                investigation_id=investigation_id, task_id=finding["task_id"], agent_id=finding["agent_id"],
                finding_id=finding["finding_id"], category=finding["category"], summary=finding["summary"],
                confidence=finding["confidence"], status=status, validation_reasons=validation_reasons,
                limitations=finding["limitations"], evidence_ids=evidence_ids, idempotency_key=idempotency_key,
            ),
            result_limit=1,
        ).rows
        return {"id": rows[0][0], "status": rows[0][1]}

    def create_handoff(self, *, investigation_id: str, handoff_id: str, task_id: str, from_agent_id: str, to_agent_id: str, reason: str, idempotency_key: str) -> dict:
        rows = self.executor.write(
            "investigation.create_handoff",
            """
            MATCH (investigation:Investigation {tenant_id:$tenant_id, id:$investigation_id})
            MATCH (task:Task {tenant_id:$tenant_id, id:$task_id})
            MATCH (from:Agent {tenant_id:$tenant_id, id:$from_agent_id})
            MATCH (to:Agent {tenant_id:$tenant_id, id:$to_agent_id})
            MERGE (handoff:Handoff {tenant_id:$tenant_id, idempotency_key:$idempotency_key})
            ON CREATE SET handoff.id=$handoff_id, handoff.reason=$reason,
                          handoff.status='created', handoff.synthetic=true,
                          handoff.source='runtime', handoff.created_at=timestamp()
            MERGE (investigation)-[:HAS_HANDOFF {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(handoff)
            MERGE (handoff)-[:TRANSFERS {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(task)
            MERGE (handoff)-[:FROM_AGENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(from)
            MERGE (handoff)-[:TO_AGENT {tenant_id:$tenant_id, synthetic:true, source:'runtime'}]->(to)
            RETURN handoff.id
            """,
            self.params(investigation_id=investigation_id, handoff_id=handoff_id, task_id=task_id, from_agent_id=from_agent_id, to_agent_id=to_agent_id, reason=reason, idempotency_key=idempotency_key),
            result_limit=1,
        ).rows
        return {"id": rows[0][0]}

    def entity_exists(self, entity_id: str) -> bool:
        rows = self.executor.read(
            "investigation.entity_exists",
            "MATCH (entity {tenant_id:$tenant_id, id:$entity_id}) RETURN count(entity)",
            self.params(entity_id=entity_id), result_limit=1,
        ).rows
        return bool(rows and rows[0][0] == 1)

    def complete(self, investigation_id: str, status: str, summary: str) -> None:
        self.executor.write(
            "investigation.complete",
            """
            MATCH (investigation:Investigation {tenant_id:$tenant_id, id:$investigation_id})
            SET investigation.status=$status, investigation.summary=$summary,
                investigation.completed_at=timestamp()
            """,
            self.params(investigation_id=investigation_id, status=status, summary=summary),
        )

    def get(self, investigation_id: str) -> dict:
        rows = self.executor.read(
            "investigation.get",
            """
            MATCH (incident:Incident)-[:HAS_INVESTIGATION]->(investigation:Investigation {tenant_id:$tenant_id, id:$investigation_id})
            OPTIONAL MATCH (investigation)-[:HAS_TASK]->(task:Task)-[:ASSIGNED_TO]->(agent:Agent)
            OPTIONAL MATCH (investigation)-[:HAS_FINDING]->(finding:Finding)-[:PRODUCED_BY]->(producer:Agent)
            OPTIONAL MATCH (finding)-[:SUPPORTED_BY]->(evidence)
            OPTIONAL MATCH (investigation)-[:HAS_HANDOFF]->(handoff:Handoff)-[:TO_AGENT]->(receiver:Agent)
            RETURN investigation.id, incident.id, investigation.status, investigation.summary,
                   collect(DISTINCT {id:task.id, type:task.task_type, status:task.status, agent_id:agent.id, error_code:task.error_code}),
                   collect(DISTINCT {id:finding.id, category:finding.category, summary:finding.summary, confidence:finding.confidence, status:finding.status, agent_id:producer.id, evidence_id:evidence.id, reasons:finding.validation_reasons}),
                   collect(DISTINCT {id:handoff.id, receiver_id:receiver.id, reason:handoff.reason})
            """,
            self.params(investigation_id=investigation_id), result_limit=1,
        ).rows
        if not rows:
            raise EntityNotFound(investigation_id)
        r=rows[0]
        return {"id":r[0],"incident_id":r[1],"status":r[2],"summary":r[3],"tasks":[x for x in r[4] if x.get("id")],"findings":[x for x in r[5] if x.get("id")],"handoffs":[x for x in r[6] if x.get("id")]}
