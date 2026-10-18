from pathlib import Path
ROOT=Path(__file__).parents[2]

def test_release_ignore_policies_cover_runtime_artifacts():
 patterns=(ROOT/'.gitignore').read_text()+(ROOT/'.dockerignore').read_text()
 for value in ('.env','__pycache__','.pytest_cache','node_modules','dist','test-results'):
  assert value in patterns, f'missing ignore policy for {value}'

def test_release_docs_exist():
 for name in ('operations-runbook.md','security-model.md','release-checklist.md'): assert (ROOT/'docs'/name).is_file()

def test_no_generic_cypher_tool():
 text=(ROOT/'mcp-server'/'sentinel_mcp'/'server.py').read_text(); assert 'execute_cypher' not in text and 'raw_graph_query' not in text
