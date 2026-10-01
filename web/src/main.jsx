import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './style.css'
import {apiClient as API} from './services/apiClient.js'
import Workbench from './Workbench.jsx'

const money = n => n == null ? 'Not available' : `₹${Math.round(n).toLocaleString('en-IN')}`
const number = n => n == null ? 'Not available' : Math.round(n).toLocaleString('en-IN')
const tabs = ['Overview', 'District evidence', 'Scenario lab', 'Decision memo', 'Decision workbench']
const stages = [['eligible','Eligible cohort'],['need_proxy','Need proxy'],['aware','Aware'],['screened','Screened'],['followed_up','Followed up']]

function App() {
  const [tab, setTab] = useState(tabs[0])
  const [name, setName] = useState('status-quo')
  const [scenario, setScenario] = useState(null)
  const [observed, setObserved] = useState(null)
  const [error, setError] = useState('')
  const [district, setDistrict] = useState('Pune')
  useEffect(() => {
    API('scenario/' + name).then(setScenario).catch(e => setError(e.message))
  }, [name])
  useEffect(() => { API('indicators').then(setObserved).catch(e => setError(e.message)) }, [])
  const rows = observed?.rows.filter(r => r.district === district) || []
  const values = scenario?.point || {}
  const chart = stages.map(([key, label]) => ({ label, value: Math.round(values[key] || 0) }))
  const title = {Overview: 'What evidence do we actually have?', 'District evidence': 'Start with a source, not a story.', 'Scenario lab': 'Stress-test assumptions.', 'Decision memo': 'A decision needs an evidence gate.', 'Decision workbench': 'From uncertainty to a responsible decision.'}[tab]
  const memo = `DISTRICT HEALTH ACCESS LAB | WORK SAMPLE\n\nDECISION: Defer district prioritization until screening coverage, adult population and programme costs are validated.\n\nEVIDENCE: Six pilot districts across Maharashtra and Odisha. The bundled NFHS-5 figures are sex-specific percentages of elevated glucose or medicine use, not screening coverage or diagnosis. The third-party transcription still needs official district factsheet checks.\n\nILLUSTRATIVE SCENARIO: ${name}; ${number(values.screened)} screened in a synthetic cohort, with p10–p90 ${number(scenario?.bands.screened.p10)}–${number(scenario?.bands.screened.p90)}. These are invented training inputs, not actual district patients or expenditure.\n\nWHAT CHANGES THE DECISION: Obtain a compatible age-specific denominator, distinct screening counts and verified intervention costs. Verify geography and period. Then show bands and sensitivity, rather than rank districts from glucose percentage alone.\n\nLIMITATION: NFHS cross-sectional indicator cannot establish intervention effect, unmet need or private-sector screening. No policy or clinical recommendation is made.`
  function downloadMemo() {
    const blob = new Blob([memo], {type:'text/plain'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'decision-memo-draft.txt'; a.click()
    URL.revokeObjectURL(url)
  }
  return <><a className="skip-link" href="#main-content">Skip to main content</a><div className="shell">
    <aside><div className="brand"><span className="brandmark">D</span><span>HEALTH ACCESS<br/><small>DECISION LAB</small></span></div><div className="nav-label">WORKSPACE / 01</div><nav aria-label="Workspace">{tabs.map((t,i)=><button key={t} aria-pressed={tab===t} className={tab===t?'active':''} onClick={()=>setTab(t)}><span>0{i+1}</span>{t}</button>)}</nav><div className="aside-foot"><span className="status-dot"/> EVIDENCE GATE ACTIVE<br/><small>No district ranking until verified.</small></div></aside>
    <main id="main-content" tabIndex="-1"><header><span>PORTFOLIO WORK SAMPLE / INDIA</span><span>NFHS-5 · 2019–21 <span className="red">UNVERIFIED PARSE</span></span></header>
      <section className="hero"><div className="eyebrow">DISTRICT HEALTH ACCESS / {tab.toUpperCase()}</div><h1>{title}</h1><p>Six pilot districts. One hard rule: a missing screening denominator cannot be wished into a precise access gap.</p></section>
      {error && <p role="alert">Could not load API: {error}. Start the FastAPI service on port 8000.</p>}
      {tab==='Overview' && <><div className="metrics"><div><small>01 / GEOGRAPHY</small><strong>{observed ? new Set(observed.rows.map(r=>r.state+"/"+r.district)).size : "Loading"}</strong><span>Pilot districts · 2 states</span></div><div><small>02 / OBSERVED INPUTS</small><strong>{observed?.rows.length ?? "Loading"}</strong><span>Sex-specific NFHS-5 indicator rows</span></div><div><small>03 / DECISION STATUS</small><strong className="red">HOLD</strong><span>Screening coverage not sourced</span></div></div><div className="panel"><span className="eyebrow">THE CLIENT QUESTION</span><h2>Where would an NCD screening budget close the most verified gap per rupee?</h2><p>Not answerable yet. NFHS blood-glucose elevation is a measure of potential need, not the number screened. This project keeps the observed data apart from synthetic scenarios until sources align by cohort, geography and period.</p><div className="callout">NEXT EVIDENCE: official district factsheets → compatible adult denominators → distinct screening counts → cost and capacity inputs.</div></div></>}
      {tab==='District evidence' && <div className="panel"><div className="panel-head"><div><span className="eyebrow">NFHS-5 / OBSERVED_UNVERIFIED · NOT YET PDF-VERIFIED</span><h2>District indicator ledger</h2></div><select aria-label="District" value={district} onChange={e=>setDistrict(e.target.value)}>{[...new Set(observed?.rows.map(r=>r.district)||[])].map(d=><option key={d}>{d}</option>)}</select></div><p>Adult women and men aged 15+. Percentages are separate denominators; do not add or average them.</p><div className="ledger">{rows.map(r=><div key={r.indicator_id}><span>{r.indicator_id.replaceAll('_',' ')}</span><strong>{r.value_pct}%</strong><small>{r.value_status} · {r.survey_vintage}</small></div>)}</div><p className="caption">Source: <a href="https://github.com/SaiSiddhardhaKalla/NFHS" target="_blank" rel="noreferrer">community NFHS parse</a>. Official district fact-sheet cross-check pending. This is neither diagnosed prevalence nor screening coverage.</p></div>}
      {tab==='Scenario lab' && <><div className="warning">HYPOTHETICAL TRAINING SCENARIO · NOT DISTRICT DATA OR A POLICY ESTIMATE</div><div className="panel"><div className="panel-head"><div><span className="eyebrow">SYNTHETIC COHORT / MONTE CARLO</span><h2>Where does the model bend?</h2></div><select aria-label="Training scenario" value={name} onChange={e=>setName(e.target.value)}><option value="status-quo">Status quo</option><option value="outreach">More outreach</option><option value="capacity">More capacity</option></select></div><div className="chart" aria-hidden="true"><ResponsiveContainer width="100%" height={310}><BarChart data={chart} layout="vertical" margin={{left:20,right:20}}><CartesianGrid stroke="#ebeced" horizontal={false}/><XAxis type="number" tick={{fontSize:11}}/><YAxis type="category" dataKey="label" width={110} tick={{fontSize:12}}/><Tooltip formatter={v=>number(v)}/><Bar dataKey="value" fill="#2e607f" radius={[0,3,3,0]}/></BarChart></ResponsiveContainer></div><table><caption>Hypothetical funnel values, not district estimates</caption><thead><tr><th>Stage</th><th>Illustrative people</th></tr></thead><tbody>{stages.map(([key,label])=><tr key={key}><th scope="row">{label}</th><td>{number(values[key])}</td></tr>)}</tbody></table><div className="metrics compact"><div><small>HYPOTHETICAL MEDIAN SCREENED</small><strong>{number(scenario?.bands.screened.p50)}</strong><span>P10–P90: {number(scenario?.bands.screened.p10)}–{number(scenario?.bands.screened.p90)}</span></div><div><small>SPEND INPUT</small><strong>{money(values.spend_inr)}</strong><span>Synthetic amount, not a quoted cost</span></div></div></div><div className="panel"><span className="eyebrow">WHICH INPUT NEEDS RESEARCH?</span><h2>Sensitivity screen</h2><p>SALib Morris ranking of assumed ranges; a high rank means the model is sensitive, not that the input is wrong.</p><div className="rank">{scenario?.morris.slice(0,5).map((r,i)=><div key={r.input}><b>0{i+1}</b><span>{r.input.replaceAll('_',' ')}</span><strong>{r.mu_star.toFixed(1)}</strong></div>)}</div></div></>}
      {tab==='Decision workbench' && <Workbench/>}
      {tab==='Decision memo' && <div className="panel memo"><span className="eyebrow">LEGACY TEXT DRAFT / USE WORKBENCH FOR AUDITABLE MEMO</span><h2>Legacy draft: decision on hold.</h2><pre>{memo}</pre><button className="primary" onClick={downloadMemo}>Download text memo</button><button className="secondary" onClick={()=>window.print()}>Print / save as PDF</button><p className="caption">A scenario export is clearly hypothetical until the data gates close. The PDF button uses your browser print dialog; no automatic PDF generator is claimed.</p></div>}
      <footer>District Health Access Lab · Evidence-first portfolio build <span>OBSERVED ≠ ASSUMED</span></footer>
    </main>
  </div></>
}

createRoot(document.getElementById('root')).render(<App />)
