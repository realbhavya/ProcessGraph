from pathlib import Path
from app.realdata.manifest import load_manifest
ROOT=Path(__file__).parents[3]
def test_official_manifest_is_explicit_about_provenance():
 m=load_manifest(ROOT/'realdata/manifests/rieth_tep.json'); assert m.persistent_id=='doi:10.7910/DVN/6C3JR1' and m.expected_variables==52 and m.sampling_interval_seconds==180
def test_tag_mapping_has_all_52_unique_variables():
 import json
 tags=json.loads((ROOT/'realdata/mappings/tep_tags.json').read_text())['tags']; assert len(tags)==52 and len({x['source_column'] for x in tags})==52 and len({x['canonical_tag'] for x in tags})==52
