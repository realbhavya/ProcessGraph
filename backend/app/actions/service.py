from hashlib import sha256
from app.actions.policy import ActionPolicy
class ActionService:
    def __init__(self,repository,policy=None): self.repository=repository; self.policy=policy or ActionPolicy()
    @staticmethod
    def sid(prefix,key): return f"{prefix}-{sha256(key.encode()).hexdigest()[:16].upper()}"
    def propose(self,payload,key):
        self.policy.validate(payload); d=payload.model_dump(mode="json"); d["action_type"]=payload.action_type.value
        return self.repository.propose(self.sid("ACTION",key),d,key)
    def decide(self,action_id,payload,key): return self.repository.decide(action_id,payload.decision,payload.reviewer_id,payload.reason,self.sid("ACTREV",key),key)
    def execute(self,action_id,payload,key): return self.repository.execute(action_id,self.sid("EXEC",key),payload.executor_id,key)
