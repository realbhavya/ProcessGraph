# Safety and Data Boundaries

## Mandatory disclaimer

ProcessGraph Sentinel is a synthetic decision-support demonstration. It must not be used to control equipment or replace qualified operations, maintenance, process-safety, or emergency-response personnel.

## Allowed actions

- Create a synthetic task.
- Assign a synthetic team.
- Ask for additional observations.
- Escalate for human review.
- Attach an approved procedure reference.
- Record a finding or outcome.
- Promote reviewed memory.

## Prohibited actions

- Operate real equipment.
- Change a set point.
- Start or stop machinery.
- Open or close a valve.
- Bypass, suppress, or disable a safeguard.
- Create operating instructions for real incidents.
- Alter an approved procedure autonomously.
- Treat an LLM hypothesis as a confirmed cause.

## Data policy

Allowed:

- Synthetic data
- Public data with appropriate permission
- Project-owned data

Prohibited:

- Private or personal information
- Login-protected data
- Paywalled content
- Restricted industrial information
- Credentials and secrets

## Agent boundaries

- Agents receive only allow-listed tools.
- Agents cannot execute arbitrary Cypher.
- Tools validate tenant, permissions, input shape, depth, and result limits.
- Historical memory is labelled as prior evidence, not current proof.
- Unknown entities and insufficient evidence cause abstention.
- Safety-significant actions require human approval.
