from app.graph.errors import EntityNotFound, InvalidInput
from app.graph.repositories.base import BaseRepository

class ActionGovernanceRepository(BaseRepository):
    def propose(self, action_id, proposal, idempotency_key):
        """Create an idempotent governed action from a validated finding.

        The query deliberately follows the same FalkorDB-compatible structure as
        the established workflow action writer: resolve prerequisites first,
        merge the action by idempotency key, then merge provenance relationships.
        """
        params = self.params(
            action_id=action_id,
            idempotency_key=idempotency_key,
            finding_id=proposal["finding_id"],
            team_id=proposal["team_id"],
            action_type=proposal["action_type"],
            summary=proposal["summary"],
            rationale=proposal["rationale"],
            reversibility=proposal["reversibility"],
        )
        rows = self.executor.write(
            "action.propose",
            """
            MATCH (finding:Finding {tenant_id: $tenant_id, id: $finding_id})
            WHERE finding.status = 'validated'
            MATCH (team:Team {tenant_id: $tenant_id, id: $team_id})
            MERGE (action:Action {tenant_id: $tenant_id, idempotency_key: $idempotency_key})
            ON CREATE SET action.id = $action_id,
                          action.action_type = $action_type,
                          action.summary = $summary,
                          action.rationale = $rationale,
                          action.reversibility = $reversibility,
                          action.status = 'PROPOSED',
                          action.synthetic = true,
                          action.source = 'runtime',
                          action.created_at = timestamp()
            MERGE (action)-[:ADDRESSES {tenant_id: $tenant_id, synthetic: true, source: 'runtime'}]->(finding)
            MERGE (action)-[:ASSIGNED_TO {tenant_id: $tenant_id, synthetic: true, source: 'runtime'}]->(team)
            RETURN action.id, action.status, action.action_type
            """,
            params,
            result_limit=1,
        ).rows
        if not rows:
            raise InvalidInput("Validated finding and responsible team are required")
        return {"id": rows[0][0], "status": rows[0][1], "action_type": rows[0][2]}

    def decide(self,action_id,decision,reviewer_id,reason,approval_id,idempotency_key):
        target="APPROVED" if decision=="approve" else "REJECTED"
        rows=self.executor.write("action.decide","""
        MATCH (a:Action {tenant_id:$tenant_id,id:$action_id,status:'PROPOSED'})
        MERGE (r:ActionReview {tenant_id:$tenant_id,idempotency_key:$idempotency_key})
        ON CREATE SET r.id=$approval_id,r.decision=$decision,r.reviewer_id=$reviewer_id,r.reason=$reason,
          r.synthetic=true,r.source='runtime',r.created_at=timestamp()
        MERGE (a)-[:HAS_REVIEW {tenant_id:$tenant_id,synthetic:true,source:'runtime'}]->(r)
        SET a.status=$target,a.reviewed_at=timestamp()
        RETURN a.id,a.status
        """,self.params(action_id=action_id,decision=decision,reviewer_id=reviewer_id,reason=reason,approval_id=approval_id,idempotency_key=idempotency_key,target=target),result_limit=1).rows
        if not rows: raise InvalidInput("Action must be proposed before review")
        return {"id":rows[0][0],"status":rows[0][1]}
    def execute(self,action_id,execution_id,executor_id,idempotency_key):
        rows=self.executor.write("action.execute","""
        MATCH (a:Action {tenant_id:$tenant_id,id:$action_id,status:'APPROVED'})
        MATCH (a)-[:HAS_REVIEW]->(:ActionReview {decision:'approve'})
        MERGE (e:ActionExecution {tenant_id:$tenant_id,idempotency_key:$idempotency_key})
        ON CREATE SET e.id=$execution_id,e.mode='simulation',e.executor_id=$executor_id,e.status='COMPLETED',
          e.output='Synthetic workflow record created; no plant control performed',e.synthetic=true,e.source='runtime',e.created_at=timestamp()
        MERGE (a)-[:HAS_EXECUTION {tenant_id:$tenant_id,synthetic:true,source:'runtime'}]->(e)
        SET a.status='EXECUTED',a.executed_at=timestamp()
        RETURN a.id,a.status,e.id,e.mode,e.output
        """,self.params(action_id=action_id,execution_id=execution_id,executor_id=executor_id,idempotency_key=idempotency_key),result_limit=1).rows
        if not rows: raise InvalidInput("Only approved actions can be executed")
        r=rows[0]; return {"action_id":r[0],"status":r[1],"execution_id":r[2],"mode":r[3],"output":r[4]}
    def get(self,action_id):
        rows=self.executor.read("action.get","""
        MATCH (a:Action {tenant_id:$tenant_id,id:$action_id})
        OPTIONAL MATCH (a)-[:HAS_REVIEW]->(r:ActionReview)
        OPTIONAL MATCH (a)-[:HAS_EXECUTION]->(e:ActionExecution)
        RETURN a.id,a.status,a.action_type,a.summary,a.rationale,collect(DISTINCT {id:r.id,decision:r.decision,reviewer_id:r.reviewer_id,reason:r.reason}),collect(DISTINCT {id:e.id,mode:e.mode,status:e.status,output:e.output})
        """,self.params(action_id=action_id),result_limit=1).rows
        if not rows: raise EntityNotFound(action_id)
        r=rows[0]; return {"id":r[0],"status":r[1],"action_type":r[2],"summary":r[3],"rationale":r[4],"reviews":[x for x in r[5] if x.get('id')],"executions":[x for x in r[6] if x.get('id')]}
