import json
from pathlib import Path
ROOT=Path(__file__).parents[3]/"evals"
def test_all_eval_case_files_are_valid_and_have_unique_ids():
 ids=[]
 for path in sorted((ROOT/"cases").glob("*.json")):
  data=json.loads(path.read_text()); assert data["suite"] and data["cases"]
  ids.extend(x["id"] for x in data["cases"])
 assert len(ids)==len(set(ids)) and len(ids)>=20
def test_eval_runner_has_no_random_pass_logic():
 text=(ROOT/"run.py").read_text(); assert "random" not in text; assert "total_failed" in text; assert "raise SystemExit(1)" in text
def test_performance_has_real_thresholds():
 data=json.loads((ROOT/"cases"/"performance.json").read_text()); assert all(x["iterations"]>=20 and x["p95_limit_ms"]>0 for x in data["cases"])
