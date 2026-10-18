# Deterministic Evaluation Harness

Milestone 9 measures connected-data correctness, multi-agent coordination, governed memory, safety and security controls, and repository performance. The fixture is created through public APIs. The harness uses real FalkorDB queries and repository calls, writes `evals/results/milestone-9-report.json`, and exits non-zero if any case fails. No random score, synthetic pass flag, or model-judged success is used.
