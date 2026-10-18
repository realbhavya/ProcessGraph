CREATE INDEX FOR (n:Equipment) ON (n.id);
CREATE INDEX FOR (n:Equipment) ON (n.normalized_name);
CREATE INDEX FOR (n:Incident) ON (n.id);
CREATE INDEX FOR (n:MaintenanceFinding) ON (n.id);
CREATE INDEX FOR (n:Memory) ON (n.id);
CREATE INDEX FOR (n:Team) ON (n.id);
CREATE INDEX FOR (n:Sensor) ON (n.id);
