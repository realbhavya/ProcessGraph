from __future__ import annotations

from app.domain.investigations import FindingStatus, SpecialistFinding, ValidatedFinding


class EvidenceValidator:
    """Validate specialist output against graph-backed evidence and allowed claims."""

    def __init__(self, entity_exists):
        self.entity_exists = entity_exists

    def validate(self, finding: SpecialistFinding) -> ValidatedFinding:
        reasons: list[str] = []
        if not finding.evidence:
            reasons.append("Finding contains no evidence")
        for evidence in finding.evidence:
            if not self.entity_exists(evidence.entity_id):
                reasons.append(f"Evidence entity does not exist: {evidence.entity_id}")
            if len(evidence.path_node_ids) > 1 and len(evidence.path_relationships) != len(evidence.path_node_ids) - 1:
                reasons.append(f"Evidence path is structurally inconsistent: {evidence.entity_id}")
            if evidence.source in {"historical_incident", "memory"} and finding.category == "connectivity" and finding.confidence >= 1:
                reasons.append("Historical evidence cannot provide absolute current-state certainty")
        status = FindingStatus.REJECTED if reasons else FindingStatus.VALIDATED
        return ValidatedFinding(finding=finding, status=status, validation_reasons=reasons or ["Evidence entities and paths validated"])
