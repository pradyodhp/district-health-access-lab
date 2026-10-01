import {useEffect, useState} from 'react'
import {apiClient as API} from '../services/apiClient.js'
import {useCase} from './useCase.js'
import {useEvidence} from './useEvidence.js'
import {useSimulation} from './useSimulation.js'
import {useResearchBacklog} from './useResearchBacklog.js'
import {useDecisionRun} from './useDecisionRun.js'

export function useWorkbench() {
  const [section, setSection] = useState('Case & evidence')
  const [lineage, setLineage] = useState(null)
  const [presets, setPresets] = useState({})
  const [selected, setSelected] = useState('status-quo')
  const [robust, setRobust] = useState(null)
  const [reversal, setReversal] = useState(null)
  const [challenger, setChallenger] = useState("outreach")
  const {research, setResearch} = useResearchBacklog()
  const [allocation, setAllocation] = useState(null)
  const [budget, setBudget] = useState(150000)
  const [threshold, setThreshold] = useState(250)
  const [thresholdResult, setThresholdResult] = useState(null)
  const {run, memo, priorRun, comparison, setRun, setMemo, setPriorRun, setComparison} = useDecisionRun()
  const [error, setError] = useState('')
  const {inputs, setInputs} = useSimulation(selected, setError)
  const [working, setWorking] = useState(false)
  const {caseFile, setCaseFile, readiness, hypotheses} = useCase(setError)
  const {evidence} = useEvidence(setError)
  useEffect(() => { let active = true; API('presets').then(value => {if(active) setPresets(value)}).catch(e => {if(active) setError(e.message)}); return () => {active=false} }, [])
  useEffect(() => {setResearch(null);setReversal(null);setRobust(null);setThresholdResult(null);setMemo(null)}, [selected])
  async function perform(action) {setWorking(true);setError('');try {await action()} catch(e) {setError(e.message)} finally {setWorking(false)} }
  function editCase(field, value) {setCaseFile({...caseFile,[field]:value});setRun(null);setPriorRun(null);setMemo(null);setComparison(null)}
  function edit(field, part, raw) {setResearch(null);setRobust(null);setReversal(null);setThresholdResult(null);if(run) setPriorRun(run);setInputs({...inputs,[field]:{...inputs[field],[part]:Number(raw)}});setRun(null);setComparison(null);setMemo(null)}
  function exportMemo() {const blob = new Blob([JSON.stringify(memo,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`memo-${memo.run_id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
  return {allocation, budget, caseFile, challenger, comparison, edit, editCase, error, evidence, exportMemo, hypotheses, inputs, lineage, memo, perform, presets, priorRun, readiness, research, reversal, robust, run, section, selected, setAllocation, setBudget, setCaseFile, setChallenger, setComparison, setError, setInputs, setLineage, setMemo, setPresets, setPriorRun, setResearch, setReversal, setRobust, setRun, setSection, setSelected, setThreshold, setThresholdResult, setWorking, threshold, thresholdResult, working}
}
