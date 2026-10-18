TENANT_ID = "TENANT-DEMO"
SOURCE = "processgraph-sentinel-seed-v1"

NODES = {
    "Tenant": [{"id": TENANT_ID, "name": "Demo Tenant"}],
    "Plant": [{"id": "PLANT-DEMO", "name": "Sentinel Synthetic Chemicals Plant", "location": "Synthetic Site"}],
    "Unit": [
        {"id": "UNIT-FEED", "name": "Feed Preparation"},
        {"id": "UNIT-REACTION", "name": "Reaction"},
        {"id": "UNIT-SEPARATION", "name": "Separation"},
        {"id": "UNIT-UTILITIES", "name": "Utilities"},
    ],
    "Equipment": [
        {"id": "EQ-T-101", "name": "T-101", "normalized_name": "t-101", "equipment_type": "feed_tank", "criticality": "medium", "status": "active"},
        {"id": "EQ-P-101", "name": "P-101", "normalized_name": "p-101", "equipment_type": "feed_pump", "criticality": "medium", "status": "active"},
        {"id": "EQ-F-101", "name": "F-101", "normalized_name": "f-101", "equipment_type": "feed_filter", "criticality": "medium", "status": "active"},
        {"id": "EQ-H-101", "name": "H-101", "normalized_name": "h-101", "equipment_type": "feed_heater", "criticality": "high", "status": "active"},
        {"id": "EQ-R-101", "name": "R-101", "normalized_name": "r-101", "equipment_type": "reactor", "criticality": "high", "status": "active"},
        {"id": "EQ-A-101", "name": "A-101", "normalized_name": "a-101", "equipment_type": "agitator", "criticality": "high", "status": "active"},
        {"id": "EQ-E-101", "name": "E-101", "normalized_name": "e-101", "equipment_type": "reactor_cooling_exchanger", "criticality": "high", "status": "active"},
        {"id": "EQ-E-102", "name": "E-102", "normalized_name": "e-102", "equipment_type": "secondary_exchanger", "criticality": "high", "status": "active"},
        {"id": "EQ-V-101", "name": "V-101", "normalized_name": "v-101", "equipment_type": "separator", "criticality": "high", "status": "active"},
        {"id": "EQ-C-101", "name": "C-101", "normalized_name": "c-101", "equipment_type": "vent_condenser", "criticality": "high", "status": "active"},
        {"id": "EQ-P-301", "name": "P-301", "normalized_name": "p-301", "equipment_type": "product_pump", "criticality": "medium", "status": "active"},
        {"id": "EQ-T-301", "name": "T-301", "normalized_name": "t-301", "equipment_type": "product_tank", "criticality": "medium", "status": "active"},
        {"id": "EQ-P-201", "name": "P-201", "normalized_name": "p-201", "equipment_type": "cooling_water_pump", "criticality": "high", "status": "active"},
        {"id": "EQ-P-202", "name": "P-202", "normalized_name": "p-202", "equipment_type": "cooling_water_pump", "criticality": "high", "status": "standby"},
        {"id": "EQ-T-201", "name": "T-201", "normalized_name": "t-201", "equipment_type": "cooling_tower", "criticality": "high", "status": "active"},
        {"id": "EQ-S-201", "name": "S-201", "normalized_name": "s-201", "equipment_type": "cooling_water_strainer", "criticality": "high", "status": "active"},
        {"id": "EQ-P-211", "name": "P-211", "normalized_name": "p-211", "equipment_type": "chilled_water_pump", "criticality": "medium", "status": "active"},
        {"id": "EQ-CH-201", "name": "CH-201", "normalized_name": "ch-201", "equipment_type": "chiller", "criticality": "medium", "status": "active"},
        {"id": "EQ-B-201", "name": "B-201", "normalized_name": "b-201", "equipment_type": "steam_boiler", "criticality": "high", "status": "active"},
        {"id": "EQ-AIR-201", "name": "AIR-201", "normalized_name": "air-201", "equipment_type": "air_compressor", "criticality": "medium", "status": "active"},
        {"id": "EQ-N2-201", "name": "N2-201", "normalized_name": "n2-201", "equipment_type": "nitrogen_header", "criticality": "high", "status": "active"},
        {"id": "EQ-D-201", "name": "D-201", "normalized_name": "d-201", "equipment_type": "cooling_water_drum", "criticality": "medium", "status": "active"},
        {"id": "EQ-FL-201", "name": "FL-201", "normalized_name": "fl-201", "equipment_type": "flare_header", "criticality": "high", "status": "active"},
        {"id": "EQ-V-301", "name": "V-301", "normalized_name": "v-301", "equipment_type": "knockout_drum", "criticality": "high", "status": "active"},
    ],
    "UtilitySystem": [
        {"id": "UTIL-CW-201", "name": "Cooling Water CW-201", "utility_type": "cooling_water"},
        {"id": "UTIL-CHW-201", "name": "Chilled Water CHW-201", "utility_type": "chilled_water"},
        {"id": "UTIL-STEAM-201", "name": "Steam ST-201", "utility_type": "steam"},
        {"id": "UTIL-AIR-201", "name": "Instrument Air IA-201", "utility_type": "instrument_air"},
        {"id": "UTIL-N2-201", "name": "Nitrogen N2-201", "utility_type": "nitrogen"},
    ],
    "Sensor": [
        {"id": "SEN-TI-101", "name": "TI-101", "sensor_type": "temperature"},
        {"id": "SEN-FI-201", "name": "FI-201", "sensor_type": "flow"},
        {"id": "SEN-PI-201", "name": "PI-201", "sensor_type": "pressure"},
        {"id": "SEN-VI-201", "name": "VI-201", "sensor_type": "vibration"},
        {"id": "SEN-TI-102", "name": "TI-102", "sensor_type": "temperature"},
        {"id": "SEN-LI-101", "name": "LI-101", "sensor_type": "level"},
        {"id": "SEN-PI-101", "name": "PI-101", "sensor_type": "pressure"},
        {"id": "SEN-FI-101", "name": "FI-101", "sensor_type": "flow"},
        {"id": "SEN-TI-301", "name": "TI-301", "sensor_type": "temperature"},
        {"id": "SEN-LI-301", "name": "LI-301", "sensor_type": "level"},
        {"id": "SEN-PI-301", "name": "PI-301", "sensor_type": "pressure"},
        {"id": "SEN-FI-202", "name": "FI-202", "sensor_type": "flow"},
    ],
    "Parameter": [
        {"id": "PAR-TEMP", "name": "Temperature", "default_unit": "degC"},
        {"id": "PAR-FLOW", "name": "Flow", "default_unit": "m3/h"},
        {"id": "PAR-PRESS", "name": "Pressure", "default_unit": "bar"},
        {"id": "PAR-VIB", "name": "Vibration", "default_unit": "mm/s"},
        {"id": "PAR-LEVEL", "name": "Level", "default_unit": "percent"},
        {"id": "PAR-DP", "name": "Differential Pressure", "default_unit": "bar"},
        {"id": "PAR-STATUS", "name": "Status", "default_unit": "state"},
        {"id": "PAR-PH", "name": "pH", "default_unit": "pH"},
    ],
    "Hazard": [
        {"id": "HAZ-RUNAWAY", "name": "Runaway reaction", "severity": "critical"},
        {"id": "HAZ-OVERPRESS", "name": "Overpressure", "severity": "critical"},
        {"id": "HAZ-LOSS-COOL", "name": "Loss of cooling", "severity": "high"},
        {"id": "HAZ-FIRE", "name": "Fire exposure", "severity": "critical"},
        {"id": "HAZ-RELEASE", "name": "Loss of containment", "severity": "critical"},
        {"id": "HAZ-HIGHLEVEL", "name": "High liquid level", "severity": "high"},
        {"id": "HAZ-CAVITATION", "name": "Pump cavitation", "severity": "medium"},
    ],
    "Safeguard": [
        {"id": "SAFE-TTRIP-101", "name": "R-101 high-temperature trip", "safeguard_type": "trip", "design_status": "installed"},
        {"id": "SAFE-PAHH-101", "name": "R-101 high-pressure trip", "safeguard_type": "trip", "design_status": "installed"},
        {"id": "SAFE-PSV-101", "name": "R-101 relief valve", "safeguard_type": "relief", "design_status": "installed"},
        {"id": "SAFE-CWALARM-201", "name": "Cooling-water low-flow alarm", "safeguard_type": "alarm", "design_status": "installed"},
        {"id": "SAFE-P202", "name": "Standby cooling-water pump P-202", "safeguard_type": "redundancy", "design_status": "installed"},
        {"id": "SAFE-LAHH-101", "name": "V-101 high-level alarm", "safeguard_type": "alarm", "design_status": "installed"},
        {"id": "SAFE-FG-101", "name": "Reaction-area gas detector", "safeguard_type": "detector", "design_status": "installed"},
        {"id": "SAFE-FLARE", "name": "Flare disposal path", "safeguard_type": "containment", "design_status": "installed"},
        {"id": "SAFE-N2", "name": "Nitrogen inerting connection", "safeguard_type": "inerting", "design_status": "installed"},
        {"id": "SAFE-BUND", "name": "Tank bund", "safeguard_type": "secondary_containment", "design_status": "installed"},
    ],
    "Team": [
        {"id": "TEAM-OPS", "name": "Operations Team"},
        {"id": "TEAM-UTIL", "name": "Utilities Team"},
        {"id": "TEAM-MAINT", "name": "Maintenance Team"},
        {"id": "TEAM-PROCESS", "name": "Process Safety Team"},
    ],
    "Person": [
        {"id": "PERSON-A", "name": "Aarav Mehta", "role": "shift_supervisor"},
        {"id": "PERSON-B", "name": "Diya Rao", "role": "utilities_engineer"},
        {"id": "PERSON-C", "name": "Kabir Shah", "role": "maintenance_planner"},
        {"id": "PERSON-D", "name": "Meera Nair", "role": "process_engineer"},
        {"id": "PERSON-E", "name": "Rohan Das", "role": "operator"},
        {"id": "PERSON-F", "name": "Isha Kulkarni", "role": "reliability_engineer"},
        {"id": "PERSON-G", "name": "Neel Joshi", "role": "instrument_engineer"},
        {"id": "PERSON-H", "name": "Tara Bose", "role": "safety_reviewer"},
    ],
    "MaintenanceFinding": [
        {"id": "MF-001", "summary": "P-201 vibration increasing", "severity": "high", "status": "open", "created_at": 1792261800},
        {"id": "MF-002", "summary": "S-201 differential pressure elevated", "severity": "medium", "status": "monitoring", "created_at": 1792175400},
        {"id": "MF-003", "summary": "E-101 cooling-side fouling suspected", "severity": "medium", "status": "open", "created_at": 1792089000},
        {"id": "MF-004", "summary": "FI-201 calibration drift", "severity": "low", "status": "closed", "created_at": 1791916200},
        {"id": "MF-005", "summary": "P-202 monthly test overdue", "severity": "high", "status": "open", "created_at": 1792002600},
        {"id": "MF-006", "summary": "V-101 level transmitter intermittent", "severity": "medium", "status": "monitoring", "created_at": 1791830000},
        {"id": "MF-007", "summary": "C-101 cooling duty below baseline", "severity": "medium", "status": "open", "created_at": 1791743600},
        {"id": "MF-008", "summary": "P-101 seal inspection complete", "severity": "low", "status": "closed", "created_at": 1791657200},
        {"id": "MF-009", "summary": "AIR-201 discharge temperature elevated", "severity": "medium", "status": "open", "created_at": 1791570800},
        {"id": "MF-010", "summary": "PSV-101 inspection completed", "severity": "low", "status": "closed", "created_at": 1791484400},
    ],
    "Procedure": [
        {"id": "PROC-LOSS-COOL", "name": "Loss of Cooling Review", "version": "1.0", "status": "approved"},
        {"id": "PROC-HIGHTEMP", "name": "High Temperature Triage", "version": "1.0", "status": "approved"},
        {"id": "PROC-PUMP", "name": "Pump Abnormality Review", "version": "1.0", "status": "approved"},
        {"id": "PROC-HIGHLEVEL", "name": "Separator High Level Review", "version": "1.0", "status": "approved"},
        {"id": "PROC-SENSOR", "name": "Sensor Validation", "version": "1.0", "status": "approved"},
        {"id": "PROC-ESCALATE", "name": "Operations Escalation", "version": "1.0", "status": "approved"},
    ],
    "Incident": [
        {"id": "INC-HIST-001", "summary": "R-101 high temperature with reduced cooling-water flow", "status": "resolved", "occurred_at": 1789576200},
        {"id": "INC-HIST-002", "summary": "P-201 vibration alert", "status": "resolved", "occurred_at": 1786984200},
        {"id": "INC-HIST-003", "summary": "FI-201 false-low flow indication", "status": "resolved", "occurred_at": 1784392200},
        {"id": "INC-HIST-004", "summary": "E-101 cooling performance degradation", "status": "resolved", "occurred_at": 1781800200},
        {"id": "INC-HIST-005", "summary": "Cooling-water header pressure reduction", "status": "resolved", "occurred_at": 1779208200},
        {"id": "INC-HIST-006", "summary": "V-101 high level", "status": "resolved", "occurred_at": 1776616200},
        {"id": "INC-HIST-007", "summary": "P-101 feed pump trip", "status": "resolved", "occurred_at": 1774024200},
        {"id": "INC-HIST-008", "summary": "E-102 cooling duty decline", "status": "inconclusive", "occurred_at": 1771432200},
    ],
    "Action": [
        {"id": "ACT-HIST-001", "action_type": "CREATE_INSPECTION_TASK", "summary": "Inspect S-201 and P-201 supply path", "status": "completed"},
        {"id": "ACT-HIST-002", "action_type": "REVIEW_SENSOR", "summary": "Validate FI-201 reading", "status": "completed"},
        {"id": "ACT-HIST-003", "action_type": "REVIEW_EXCHANGER", "summary": "Review E-101 fouling indicators", "status": "completed"},
        {"id": "ACT-HIST-004", "action_type": "ESCALATE_TO_TEAM", "summary": "Escalate cooling-water header issue", "status": "completed"},
    ],
    "Outcome": [
        {"id": "OUT-HIST-001", "summary": "Partial S-201 blockage was found and addressed in the synthetic scenario", "effectiveness": "helpful"},
        {"id": "OUT-HIST-002", "summary": "FI-201 calibration check confirmed measurement drift", "effectiveness": "helpful"},
        {"id": "OUT-HIST-003", "summary": "E-101 cleaning restored synthetic baseline duty", "effectiveness": "helpful"},
        {"id": "OUT-HIST-004", "summary": "Header pressure recovered after utility review", "effectiveness": "helpful"},
    ],
    "Agent": [
        {"id": "AGENT-ORCH", "name": "Incident Orchestrator", "agent_type": "orchestrator"},
        {"id": "AGENT-CONN", "name": "Connectivity Agent", "agent_type": "specialist"},
        {"id": "AGENT-SAFE", "name": "Safety Context Agent", "agent_type": "specialist"},
        {"id": "AGENT-MEM", "name": "Maintenance and Memory Agent", "agent_type": "specialist"},
    ],
    "Memory": [
        {"id": "MEM-EP-001", "memory_type": "episodic", "summary": "INC-HIST-001 combined high R-101 temperature with reduced cooling-water flow", "confidence": 0.92, "status": "active"},
        {"id": "MEM-PR-001", "memory_type": "procedural", "summary": "Validate the observation, traverse the cooling supply path, and review unresolved findings before escalation", "confidence": 0.90, "status": "active"},
        {"id": "MEM-SE-001", "memory_type": "semantic", "summary": "E-101 and E-102 share the synthetic CW-201 utility system", "confidence": 0.99, "status": "active"},
    ],
}

# Each relationship tuple: start label, start id, relationship type, end label, end id, properties.
RELATIONSHIPS = [
    ("Tenant", TENANT_ID, "OWNS_GRAPH_CONTEXT", "Plant", "PLANT-DEMO", {}),
    ("Plant", "PLANT-DEMO", "HAS_UNIT", "Unit", "UNIT-FEED", {}),
    ("Plant", "PLANT-DEMO", "HAS_UNIT", "Unit", "UNIT-REACTION", {}),
    ("Plant", "PLANT-DEMO", "HAS_UNIT", "Unit", "UNIT-SEPARATION", {}),
    ("Plant", "PLANT-DEMO", "HAS_UNIT", "Unit", "UNIT-UTILITIES", {}),
]

UNIT_EQUIPMENT = {
    "UNIT-FEED": ["EQ-T-101", "EQ-P-101", "EQ-F-101", "EQ-H-101"],
    "UNIT-REACTION": ["EQ-R-101", "EQ-A-101", "EQ-E-101", "EQ-E-102"],
    "UNIT-SEPARATION": ["EQ-V-101", "EQ-C-101", "EQ-P-301", "EQ-T-301", "EQ-V-301", "EQ-FL-201"],
    "UNIT-UTILITIES": ["EQ-P-201", "EQ-P-202", "EQ-T-201", "EQ-S-201", "EQ-P-211", "EQ-CH-201", "EQ-B-201", "EQ-AIR-201", "EQ-N2-201", "EQ-D-201"],
}
for unit, equipment_ids in UNIT_EQUIPMENT.items():
    RELATIONSHIPS.extend(("Unit", unit, "CONTAINS", "Equipment", eid, {}) for eid in equipment_ids)

RELATIONSHIPS += [
    ("Equipment", "EQ-T-101", "FEEDS", "Equipment", "EQ-P-101", {}),
    ("Equipment", "EQ-P-101", "FEEDS", "Equipment", "EQ-F-101", {}),
    ("Equipment", "EQ-F-101", "FEEDS", "Equipment", "EQ-H-101", {}),
    ("Equipment", "EQ-H-101", "FEEDS", "Equipment", "EQ-R-101", {}),
    ("Equipment", "EQ-R-101", "FEEDS", "Equipment", "EQ-V-101", {}),
    ("Equipment", "EQ-V-101", "FEEDS", "Equipment", "EQ-P-301", {}),
    ("Equipment", "EQ-P-301", "FEEDS", "Equipment", "EQ-T-301", {}),
    ("Equipment", "EQ-R-101", "COOLED_BY", "Equipment", "EQ-E-101", {}),
    ("Equipment", "EQ-E-102", "COOLED_BY", "UtilitySystem", "UTIL-CW-201", {}),
    ("Equipment", "EQ-E-101", "SUPPLIED_BY", "UtilitySystem", "UTIL-CW-201", {}),
    ("UtilitySystem", "UTIL-CW-201", "SUPPLIED_BY", "Equipment", "EQ-P-201", {"duty": "primary"}),
    ("UtilitySystem", "UTIL-CW-201", "SUPPLIED_BY", "Equipment", "EQ-P-202", {"duty": "standby"}),
    ("Equipment", "EQ-P-201", "DEPENDS_ON", "Equipment", "EQ-S-201", {}),
    ("Equipment", "EQ-P-202", "DEPENDS_ON", "Equipment", "EQ-S-201", {}),
    ("Equipment", "EQ-S-201", "DEPENDS_ON", "Equipment", "EQ-D-201", {}),
    ("Equipment", "EQ-D-201", "DEPENDS_ON", "Equipment", "EQ-T-201", {}),
    ("UtilitySystem", "UTIL-CHW-201", "SUPPLIED_BY", "Equipment", "EQ-P-211", {}),
    ("Equipment", "EQ-P-211", "DEPENDS_ON", "Equipment", "EQ-CH-201", {}),
    ("Equipment", "EQ-H-101", "SUPPLIED_BY", "UtilitySystem", "UTIL-STEAM-201", {}),
    ("UtilitySystem", "UTIL-STEAM-201", "SUPPLIED_BY", "Equipment", "EQ-B-201", {}),
    ("Equipment", "EQ-R-101", "SUPPLIED_BY", "UtilitySystem", "UTIL-N2-201", {}),
    ("UtilitySystem", "UTIL-N2-201", "SUPPLIED_BY", "Equipment", "EQ-N2-201", {}),
    ("Sensor", "SEN-TI-101", "MONITORS", "Equipment", "EQ-R-101", {}),
    ("Sensor", "SEN-TI-101", "MEASURES", "Parameter", "PAR-TEMP", {}),
    ("Sensor", "SEN-FI-201", "MONITORS", "UtilitySystem", "UTIL-CW-201", {}),
    ("Sensor", "SEN-FI-201", "MEASURES", "Parameter", "PAR-FLOW", {}),
    ("Sensor", "SEN-PI-201", "MONITORS", "UtilitySystem", "UTIL-CW-201", {}),
    ("Sensor", "SEN-PI-201", "MEASURES", "Parameter", "PAR-PRESS", {}),
    ("Sensor", "SEN-VI-201", "MONITORS", "Equipment", "EQ-P-201", {}),
    ("Sensor", "SEN-VI-201", "MEASURES", "Parameter", "PAR-VIB", {}),
    ("Sensor", "SEN-TI-102", "MONITORS", "Equipment", "EQ-E-102", {}),
    ("Sensor", "SEN-TI-102", "MEASURES", "Parameter", "PAR-TEMP", {}),
    ("Sensor", "SEN-LI-101", "MONITORS", "Equipment", "EQ-V-101", {}),
    ("Sensor", "SEN-LI-101", "MEASURES", "Parameter", "PAR-LEVEL", {}),
    ("Sensor", "SEN-PI-101", "MONITORS", "Equipment", "EQ-R-101", {}),
    ("Sensor", "SEN-PI-101", "MEASURES", "Parameter", "PAR-PRESS", {}),
    ("Equipment", "EQ-R-101", "EXPOSED_TO", "Hazard", "HAZ-RUNAWAY", {}),
    ("Equipment", "EQ-R-101", "EXPOSED_TO", "Hazard", "HAZ-OVERPRESS", {}),
    ("Equipment", "EQ-R-101", "EXPOSED_TO", "Hazard", "HAZ-LOSS-COOL", {}),
    ("Equipment", "EQ-V-101", "EXPOSED_TO", "Hazard", "HAZ-HIGHLEVEL", {}),
    ("Equipment", "EQ-P-201", "EXPOSED_TO", "Hazard", "HAZ-CAVITATION", {}),
    ("Safeguard", "SAFE-TTRIP-101", "PROTECTS", "Equipment", "EQ-R-101", {}),
    ("Safeguard", "SAFE-TTRIP-101", "MITIGATES", "Hazard", "HAZ-RUNAWAY", {}),
    ("Safeguard", "SAFE-PAHH-101", "PROTECTS", "Equipment", "EQ-R-101", {}),
    ("Safeguard", "SAFE-PAHH-101", "MITIGATES", "Hazard", "HAZ-OVERPRESS", {}),
    ("Safeguard", "SAFE-PSV-101", "PROTECTS", "Equipment", "EQ-R-101", {}),
    ("Safeguard", "SAFE-CWALARM-201", "PROTECTS", "UtilitySystem", "UTIL-CW-201", {}),
    ("Safeguard", "SAFE-CWALARM-201", "MITIGATES", "Hazard", "HAZ-LOSS-COOL", {}),
    ("Safeguard", "SAFE-P202", "PROTECTS", "UtilitySystem", "UTIL-CW-201", {}),
    ("Safeguard", "SAFE-LAHH-101", "PROTECTS", "Equipment", "EQ-V-101", {}),
    ("Safeguard", "SAFE-LAHH-101", "MITIGATES", "Hazard", "HAZ-HIGHLEVEL", {}),
]

TEAM_OWNERSHIP = {
    "TEAM-OPS": ["EQ-T-101", "EQ-P-101", "EQ-F-101", "EQ-H-101", "EQ-R-101", "EQ-A-101", "EQ-E-101", "EQ-E-102", "EQ-V-101", "EQ-C-101", "EQ-P-301", "EQ-T-301"],
    "TEAM-UTIL": ["EQ-P-201", "EQ-P-202", "EQ-T-201", "EQ-S-201", "EQ-P-211", "EQ-CH-201", "EQ-B-201", "EQ-AIR-201", "EQ-N2-201", "EQ-D-201"],
}
for team, equipment_ids in TEAM_OWNERSHIP.items():
    RELATIONSHIPS.extend(("Team", team, "OWNS", "Equipment", eid, {}) for eid in equipment_ids)

MEMBERSHIP = {
    "TEAM-OPS": ["PERSON-A", "PERSON-E"],
    "TEAM-UTIL": ["PERSON-B", "PERSON-G"],
    "TEAM-MAINT": ["PERSON-C", "PERSON-F"],
    "TEAM-PROCESS": ["PERSON-D", "PERSON-H"],
}
for team, people in MEMBERSHIP.items():
    RELATIONSHIPS.extend(("Person", person, "MEMBER_OF", "Team", team, {}) for person in people)

FINDING_TARGETS = {
    "MF-001": "EQ-P-201", "MF-002": "EQ-S-201", "MF-003": "EQ-E-101", "MF-004": "EQ-P-201",
    "MF-005": "EQ-P-202", "MF-006": "EQ-V-101", "MF-007": "EQ-C-101", "MF-008": "EQ-P-101",
    "MF-009": "EQ-AIR-201", "MF-010": "EQ-R-101",
}
for finding, target in FINDING_TARGETS.items():
    RELATIONSHIPS.append(("MaintenanceFinding", finding, "ABOUT", "Equipment", target, {}))

RELATIONSHIPS += [
    ("Procedure", "PROC-LOSS-COOL", "APPLIES_TO", "Hazard", "HAZ-LOSS-COOL", {}),
    ("Procedure", "PROC-HIGHTEMP", "APPLIES_TO", "Hazard", "HAZ-RUNAWAY", {}),
    ("Procedure", "PROC-PUMP", "APPLIES_TO", "Hazard", "HAZ-CAVITATION", {}),
    ("Incident", "INC-HIST-001", "AFFECTS", "Equipment", "EQ-R-101", {}),
    ("Incident", "INC-HIST-001", "AFFECTS", "Equipment", "EQ-E-101", {}),
    ("Incident", "INC-HIST-002", "AFFECTS", "Equipment", "EQ-P-201", {}),
    ("Incident", "INC-HIST-003", "AFFECTS", "Equipment", "EQ-P-201", {}),
    ("Incident", "INC-HIST-004", "AFFECTS", "Equipment", "EQ-E-101", {}),
    ("Incident", "INC-HIST-005", "AFFECTS", "UtilitySystem", "UTIL-CW-201", {}),
    ("Incident", "INC-HIST-006", "AFFECTS", "Equipment", "EQ-V-101", {}),
    ("Incident", "INC-HIST-007", "AFFECTS", "Equipment", "EQ-P-101", {}),
    ("Incident", "INC-HIST-008", "AFFECTS", "Equipment", "EQ-E-102", {}),
    ("Incident", "INC-HIST-001", "RESULTED_IN", "Action", "ACT-HIST-001", {}),
    ("Incident", "INC-HIST-003", "RESULTED_IN", "Action", "ACT-HIST-002", {}),
    ("Incident", "INC-HIST-004", "RESULTED_IN", "Action", "ACT-HIST-003", {}),
    ("Incident", "INC-HIST-005", "RESULTED_IN", "Action", "ACT-HIST-004", {}),
    ("Action", "ACT-HIST-001", "PRODUCED", "Outcome", "OUT-HIST-001", {}),
    ("Action", "ACT-HIST-002", "PRODUCED", "Outcome", "OUT-HIST-002", {}),
    ("Action", "ACT-HIST-003", "PRODUCED", "Outcome", "OUT-HIST-003", {}),
    ("Action", "ACT-HIST-004", "PRODUCED", "Outcome", "OUT-HIST-004", {}),
    ("Memory", "MEM-EP-001", "DERIVED_FROM", "Incident", "INC-HIST-001", {}),
    ("Memory", "MEM-EP-001", "ABOUT", "Equipment", "EQ-R-101", {}),
    ("Memory", "MEM-PR-001", "DERIVED_FROM", "Outcome", "OUT-HIST-001", {}),
    ("Memory", "MEM-PR-001", "ABOUT", "UtilitySystem", "UTIL-CW-201", {}),
    ("Memory", "MEM-SE-001", "ABOUT", "Equipment", "EQ-E-101", {}),
    ("Memory", "MEM-SE-001", "ABOUT", "Equipment", "EQ-E-102", {}),
]

# Additional provenance-rich operational context required by Milestone 1.
NODES["ProcessStream"] = [
    {"id": f"STREAM-{i:02d}", "name": name, "stream_type": kind}
    for i, (name, kind) in enumerate([
        ("Feed transfer", "process"), ("Filtered feed", "process"), ("Heated feed", "process"),
        ("Reactor effluent", "process"), ("Separator liquid", "process"), ("Product transfer", "process"),
        ("Reactor cooling supply", "utility"), ("Reactor cooling return", "utility"),
        ("E-102 cooling supply", "utility"), ("E-102 cooling return", "utility"),
        ("Steam supply", "utility"), ("Nitrogen supply", "utility"),
        ("Vent to condenser", "process"), ("Relief to flare", "safety"),
    ], start=1)
]

NODES["Observation"] = [
    {"id": f"OBS-HIST-{i:03d}", "qualifier": qualifier, "value": value, "unit": unit, "observed_at": 1789576200 + i * 60, "source_type": "synthetic_history"}
    for i, (qualifier, value, unit) in enumerate([
        ("high", 188.4, "degC"), ("falling", 62.0, "m3/h"), ("elevated", 7.2, "mm/s"),
        ("low", 2.1, "bar"), ("normal", 54.0, "percent"), ("high", 3.6, "bar"),
        ("normal", 120.0, "m3/h"), ("low", 78.0, "m3/h"), ("elevated", 176.0, "degC"),
        ("normal", 4.8, "mm/s"), ("high", 81.0, "percent"), ("falling", 70.0, "m3/h"),
        ("normal", 1.2, "bar"), ("high", 5.9, "mm/s"), ("low", 1.8, "bar"),
        ("normal", 165.0, "degC"), ("normal", 59.0, "percent"), ("high", 190.0, "degC"),
        ("falling", 58.0, "m3/h"), ("elevated", 7.5, "mm/s"),
    ], start=1)
]

_steps = {
    "PROC-LOSS-COOL": ["Confirm the reported observation", "Identify connected cooling equipment", "Review open findings", "Confirm owning team", "Escalate for human review"],
    "PROC-HIGHTEMP": ["Validate temperature indication", "Identify affected equipment", "Review cooling relationships", "Review designed safeguards", "Request qualified review"],
    "PROC-PUMP": ["Validate vibration indication", "Review recent findings", "Identify dependent systems", "Create inspection proposal", "Record approved outcome"],
    "PROC-HIGHLEVEL": ["Validate level indication", "Review connected inflows", "Review downstream path", "Review designed safeguards", "Escalate for human review"],
    "PROC-SENSOR": ["Check observation source", "Compare related observations", "Review calibration finding", "Mark uncertainty", "Request instrument review"],
    "PROC-ESCALATE": ["Identify graph-derived owner", "Attach evidence path", "Select allowed action", "Request approval", "Record decision"],
}
NODES["ProcedureStep"] = []
for procedure_id, steps in _steps.items():
    for sequence, instruction in enumerate(steps, start=1):
        step_id = f"STEP-{procedure_id.removeprefix('PROC-')}-{sequence:02d}"
        NODES["ProcedureStep"].append({"id": step_id, "instruction": instruction, "sequence": sequence, "status": "approved"})
        RELATIONSHIPS.append(("Procedure", procedure_id, "HAS_STEP", "ProcedureStep", step_id, {"sequence": sequence}))

_stream_edges = [
    ("STREAM-01", "EQ-T-101", "EQ-P-101"), ("STREAM-02", "EQ-P-101", "EQ-F-101"),
    ("STREAM-03", "EQ-F-101", "EQ-H-101"), ("STREAM-04", "EQ-R-101", "EQ-V-101"),
    ("STREAM-05", "EQ-V-101", "EQ-P-301"), ("STREAM-06", "EQ-P-301", "EQ-T-301"),
    ("STREAM-07", "EQ-P-201", "EQ-E-101"), ("STREAM-08", "EQ-E-101", "EQ-T-201"),
    ("STREAM-09", "EQ-P-201", "EQ-E-102"), ("STREAM-10", "EQ-E-102", "EQ-T-201"),
    ("STREAM-11", "EQ-B-201", "EQ-H-101"), ("STREAM-12", "EQ-N2-201", "EQ-R-101"),
    ("STREAM-13", "EQ-R-101", "EQ-C-101"), ("STREAM-14", "EQ-R-101", "EQ-FL-201"),
]
for stream_id, source_id, target_id in _stream_edges:
    RELATIONSHIPS.append(("ProcessStream", stream_id, "FLOWS_FROM", "Equipment", source_id, {}))
    RELATIONSHIPS.append(("ProcessStream", stream_id, "FLOWS_TO", "Equipment", target_id, {}))

_observation_links = [
    ("OBS-HIST-001", "SEN-TI-101", "INC-HIST-001"), ("OBS-HIST-002", "SEN-FI-201", "INC-HIST-001"),
    ("OBS-HIST-003", "SEN-VI-201", "INC-HIST-002"), ("OBS-HIST-004", "SEN-PI-201", "INC-HIST-005"),
    ("OBS-HIST-005", "SEN-LI-101", "INC-HIST-006"), ("OBS-HIST-006", "SEN-PI-101", "INC-HIST-001"),
    ("OBS-HIST-007", "SEN-FI-101", "INC-HIST-007"), ("OBS-HIST-008", "SEN-FI-201", "INC-HIST-004"),
    ("OBS-HIST-009", "SEN-TI-101", "INC-HIST-001"), ("OBS-HIST-010", "SEN-VI-201", "INC-HIST-002"),
    ("OBS-HIST-011", "SEN-LI-101", "INC-HIST-006"), ("OBS-HIST-012", "SEN-FI-202", "INC-HIST-008"),
    ("OBS-HIST-013", "SEN-PI-201", "INC-HIST-005"), ("OBS-HIST-014", "SEN-VI-201", "INC-HIST-002"),
    ("OBS-HIST-015", "SEN-PI-201", "INC-HIST-005"), ("OBS-HIST-016", "SEN-TI-101", "INC-HIST-001"),
    ("OBS-HIST-017", "SEN-LI-301", "INC-HIST-006"), ("OBS-HIST-018", "SEN-TI-101", "INC-HIST-001"),
    ("OBS-HIST-019", "SEN-FI-201", "INC-HIST-001"), ("OBS-HIST-020", "SEN-VI-201", "INC-HIST-002"),
]
for observation_id, sensor_id, incident_id in _observation_links:
    RELATIONSHIPS.append(("Observation", observation_id, "RECORDED_BY", "Sensor", sensor_id, {}))
    RELATIONSHIPS.append(("Observation", observation_id, "OBSERVED_DURING", "Incident", incident_id, {}))
