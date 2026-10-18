# Graph Data Model

## Purpose

The Milestone 1 graph represents the synthetic plant, connected process and utility equipment, instrumentation, hazards, safeguards, organizational ownership, maintenance records, historical incidents, actions, outcomes, agents, and initial memories.

## Central proof path

```text
R-101
  -[:COOLED_BY]-> E-101
  -[:SUPPLIED_BY]-> Cooling Water CW-201
  -[:SUPPLIED_BY]-> P-201
```

P-201 is also connected to an open vibration finding and is owned by the Utilities Team. This allows later agents to derive an assignment from graph evidence.

## Node labels

- `Tenant`, `Plant`, `Unit`
- `Equipment`, `UtilitySystem`
- `Sensor`, `Parameter`, `Observation`
- `Hazard`, `Safeguard`
- `Team`, `Person`
- `MaintenanceFinding`, `Procedure`
- `Incident`, `Action`, `Outcome`
- `Agent`, `Memory`

## Relationship families

### Process and utility

`HAS_UNIT`, `CONTAINS`, `FEEDS`, `COOLED_BY`, `SUPPLIED_BY`, `DEPENDS_ON`

### Instrumentation

`MONITORS`, `MEASURES`

### Safety

`EXPOSED_TO`, `PROTECTS`, `MITIGATES`, `APPLIES_TO`

### Organization

`OWNS`, `MEMBER_OF`

### Maintenance, incident, and memory

`ABOUT`, `AFFECTS`, `RESULTED_IN`, `PRODUCED`, `DERIVED_FROM`

## Common properties

Every seeded node and relationship includes:

```json
{
  "tenant_id": "TENANT-DEMO",
  "synthetic": true,
  "source": "processgraph-sentinel-seed-v1"
}
```

Every node has a stable `id`. Equipment also has a normalized name used for deterministic entity resolution.

## Modeling decisions

- Utilities are first-class nodes because equipment can share a common utility dependency.
- Ownership is an explicit relationship so assignment is graph-derived.
- Safeguard existence is distinct from current operating availability.
- Historical incidents, actions, and outcomes remain separate for provenance.
- Memories are linked to source incidents or outcomes and to the entities they concern.
- All default data is synthetic and tenant-scoped.
