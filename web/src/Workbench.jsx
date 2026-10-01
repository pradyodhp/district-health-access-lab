import React from 'react'
import {useWorkbench} from './hooks/useWorkbench.js'
import CaseEvidence from './components/workbench/CaseEvidence.jsx'
import ModelRuns from './components/workbench/ModelRuns.jsx'
import SensitivityResearch from './components/workbench/SensitivityResearch.jsx'
import AllocationRobustness from './components/workbench/AllocationRobustness.jsx'
import MemoPanel from './components/workbench/MemoPanel.jsx'

export default function Workbench() {
  const state = useWorkbench()
  const {section, setSection, error} = state
  return <div className="workbench"><div className="warning">HYPOTHETICAL WORKBENCH · THIS DOES NOT ESTIMATE DISTRICT GAPS OR RECOMMEND REAL FUNDING</div>
    <nav className="worknav" aria-label="Workbench sections">{['Case & evidence','Model & runs','Sensitivity & research','Allocation & robustness','Memo'].map(t=><button key={t} aria-pressed={section===t} className={section===t?'chosen':''} onClick={()=>setSection(t)}>{t}</button>)}</nav>
    {error && <p role="alert">{error}</p>}
    {section==='Case & evidence' && <CaseEvidence a={state.a} budget={state.budget} caseFile={state.caseFile} editCase={state.editCase} evidence={state.evidence} lineage={state.lineage} perform={state.perform} readiness={state.readiness} run={state.run} setLineage={state.setLineage}/>}
    {section==='Model & runs' && <ModelRuns a={state.a} caseFile={state.caseFile} comparison={state.comparison} edit={state.edit} inputs={state.inputs} perform={state.perform} presets={state.presets} priorRun={state.priorRun} run={state.run} selected={state.selected} setChallenger={state.setChallenger} setComparison={state.setComparison} setError={state.setError} setPriorRun={state.setPriorRun} setRun={state.setRun} setSelected={state.setSelected} working={state.working}/>}
    {section==='Sensitivity & research' && <SensitivityResearch a={state.a} hypotheses={state.hypotheses} perform={state.perform} research={state.research} run={state.run} selected={state.selected} setResearch={state.setResearch} working={state.working}/>}
    {section==='Allocation & robustness' && <AllocationRobustness a={state.a} allocation={state.allocation} budget={state.budget} challenger={state.challenger} inputs={state.inputs} perform={state.perform} presets={state.presets} reversal={state.reversal} robust={state.robust} run={state.run} selected={state.selected} setAllocation={state.setAllocation} setBudget={state.setBudget} setChallenger={state.setChallenger} setReversal={state.setReversal} setRobust={state.setRobust} setThreshold={state.setThreshold} setThresholdResult={state.setThresholdResult} threshold={state.threshold} thresholdResult={state.thresholdResult} working={state.working}/>}
    {section==='Memo' && <MemoPanel a={state.a} evidence={state.evidence} exportMemo={state.exportMemo} memo={state.memo} perform={state.perform} research={state.research} run={state.run} setMemo={state.setMemo} working={state.working}/>}
  </div>
}
