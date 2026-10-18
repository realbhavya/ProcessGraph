import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import "./styles.css";

const scenario = {
  summary: "R-101 temperature is high while cooling-water flow is falling.",
  equipment_names: ["R-101"],
  observations: [
    { parameter: "temperature", qualifier: "high" },
    { parameter: "cooling_water_flow", qualifier: "falling" },
  ],
};

const key = (prefix) => `${prefix}-${crypto.randomUUID()}`;

function Pill({ children, tone = "neutral" }) { return <span className={`pill ${tone}`}>{children}</span>; }
function Empty({ children }) { return <div className="empty">{children}</div>; }

export function App() {
  const [health, setHealth] = useState("checking");
  const [incident, setIncident] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => { api.health().then(() => setHealth("connected")).catch(() => setHealth("unavailable")); }, []);
  const findings = investigation?.validated_findings || [];
  const rejected = investigation?.rejected_findings || [];
  const selectedFinding = useMemo(() => findings.find((x) => x.finding.finding_id === selected) || findings[0], [findings, selected]);

  async function runInvestigation() {
    setBusy(true); setError(null); setIncident(null); setInvestigation(null);
    try {
      const created = await api.createIncident(scenario, key("ui-incident"));
      setIncident(created);
      const result = await api.investigate(created.id, key("ui-investigation"));
      setInvestigation(result);
      setSelected(result.validated_findings?.[0]?.finding?.finding_id || null);
    } catch (e) { setError({ message: e.message, code: e.code, requestId: e.requestId }); }
    finally { setBusy(false); }
  }

  return <main className="app-shell">
    <header className="topbar">
      <div><p className="eyebrow">Synthetic process decision support</p><h1>ProcessGraph Sentinel</h1></div>
      <div className={`connection ${health}`}><span /> API {health}</div>
    </header>

    <section className="overview">
      <div><Pill tone="cyan">R-101 investigation workspace</Pill><h2>Evidence before conclusions.</h2><p>Run a bounded, graph-backed investigation. Specialist findings stay linked to their source entities, limitations, and handoffs.</p></div>
      <button className="primary" onClick={runInvestigation} disabled={busy || health !== "connected"}>{busy ? "Investigating..." : "Run synthetic investigation"}</button>
    </section>

    {error && <section className="error"><strong>{error.code}</strong><span>{error.message}</span>{error.requestId && <code>{error.requestId}</code>}</section>}

    <section className="metrics">
      <article><span>Incident</span><strong>{incident?.id || "Not started"}</strong></article>
      <article><span>Investigation status</span><strong>{investigation?.status || "Pending"}</strong></article>
      <article><span>Validated findings</span><strong>{findings.length}</strong></article>
      <article><span>Explicit handoffs</span><strong>{investigation?.handoff_ids?.length || 0}</strong></article>
    </section>

    <section className="workspace">
      <div className="panel timeline-panel"><div className="panel-head"><div><p className="eyebrow">Shared state</p><h3>Agent workflow</h3></div>{investigation && <Pill tone={investigation.status === "COMPLETED" ? "green" : "amber"}>{investigation.status}</Pill>}</div>
        {!investigation ? <Empty>Run the scenario to create graph-backed tasks and handoffs.</Empty> : <ol className="timeline">
          <li><b>Incident orchestrator</b><span>Resolved R-101 and created scoped tasks.</span></li>
          <li><b>Connectivity + safety</b><span>Executed in parallel through permission-aware tools.</span></li>
          <li><b>Graph handoff</b><span>Connectivity context transferred to maintenance and memory.</span></li>
          <li><b>Evidence validator</b><span>{findings.length} accepted, {rejected.length} rejected.</span></li>
        </ol>}
      </div>

      <div className="panel findings-panel"><div className="panel-head"><div><p className="eyebrow">Validated outputs</p><h3>Findings</h3></div></div>
        {!findings.length ? <Empty>No validated findings yet.</Empty> : <div className="finding-list">{findings.map(({ finding }) => <button key={finding.finding_id} className={selectedFinding?.finding.finding_id === finding.finding_id ? "finding active" : "finding"} onClick={() => setSelected(finding.finding_id)}><span>{finding.category}</span><b>{finding.summary}</b><small>Confidence {Math.round(finding.confidence * 100)}%</small></button>)}</div>}
      </div>

      <div className="panel evidence-panel"><div className="panel-head"><div><p className="eyebrow">Explainability</p><h3>Evidence and limits</h3></div></div>
        {!selectedFinding ? <Empty>Select a finding to inspect its provenance.</Empty> : <><div className="evidence-summary"><Pill tone="green">validated</Pill><strong>{selectedFinding.finding.agent_id}</strong><span>{Math.round(selectedFinding.finding.confidence * 100)}% confidence</span></div>
        <div className="evidence-list">{selectedFinding.finding.evidence.map((item) => <div key={`${item.entity_id}-${item.source}`}><b>{item.entity_id}</b><span>{item.entity_type} · {item.source.replaceAll("_", " ")}</span>{item.path_node_ids?.length > 0 && <code>{item.path_node_ids.join(" → ")}</code>}</div>)}</div>
        <h4>Limitations</h4>{selectedFinding.finding.limitations.length ? <ul>{selectedFinding.finding.limitations.map((x) => <li key={x}>{x}</li>)}</ul> : <p className="muted">No additional limitation recorded.</p>}</>}
      </div>
    </section>

    {investigation && <section className="conclusion"><div><p className="eyebrow">Bounded conclusion</p><h3>Investigation summary</h3></div><p>{investigation.summary}</p></section>}
    <footer>Synthetic demonstration only. No plant-control commands are available.</footer>
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
