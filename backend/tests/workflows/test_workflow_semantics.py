from pathlib import Path


def test_agents_use_tool_client_not_repositories():
    root=Path(__file__).parents[2]/"app"/"agents"
    text="\n".join(p.read_text() for p in root.glob("*.py"))
    assert "AgentToolClient" in text
    assert "Repository(" not in text


def test_parallel_specialists_and_explicit_handoff_exist():
    text=(Path(__file__).parents[2]/"app"/"workflows"/"investigation.py").read_text()
    assert "ThreadPoolExecutor" in text
    assert "create_handoff" in text
    assert 'to_agent_id="AGENT-MEM"' in text
