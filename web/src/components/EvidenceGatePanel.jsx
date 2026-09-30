import React from 'react'
export default function EvidenceGatePanel({readiness}) {
  if (!readiness) return <p role="status">Loading readiness gates</p>
  return <section aria-label="Decision readiness gates">
    <p>Completeness is a checklist, not decision confidence. Real funding remains on HOLD.</p>
    <div className="table-wrap"><table><caption>Ten evidence and review gates</caption><thead><tr><th>Gate</th><th>State</th><th>Reason / next evidence</th></tr></thead>
    <tbody>{readiness.gates?.map(g=><tr key={g.id}><th scope="row">{g.id.replaceAll('_',' ')}</th><td>{g.status}</td><td>{g.reason}<small>{g.next_research_action}</small></td></tr>)}</tbody></table></div>
  </section>
}
