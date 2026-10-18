import pytest

from app.graph.errors import InvalidInput, TenantMismatch
from app.graph.repositories.equipment import EquipmentRepository


class FakeExecutor:
    def read(self, *args, **kwargs):
        class Result:
            rows = [["EQ-R-101", "R-101", "reactor", "high", "active"]]
        return Result()


def test_resolve_shapes_equipment():
    assert EquipmentRepository(FakeExecutor()).resolve("R-101")["id"] == "EQ-R-101"


def test_depth_is_bounded():
    repository = EquipmentRepository(FakeExecutor())
    with pytest.raises(InvalidInput):
        repository.trace_utility_path("EQ-R-101", 9)


def test_tenant_is_enforced():
    with pytest.raises(TenantMismatch):
        EquipmentRepository(FakeExecutor(), "OTHER")
