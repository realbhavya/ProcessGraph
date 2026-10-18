import pytest
from app.opcua.contracts import ReplaySelection
def test_replay_selection_is_bounded():
 assert ReplaySelection('d','faulty_testing',1,1,180).speed==180
 with pytest.raises(ValueError): ReplaySelection('d','s',1,1,0)
 with pytest.raises(ValueError): ReplaySelection('d','s',-1,1,1)
