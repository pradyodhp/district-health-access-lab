import { useState } from 'react'

export function useDecisionRun() {
  const [run, setRun] = useState(null)
  const [memo, setMemo] = useState(null)
  const [priorRun, setPriorRun] = useState(null)
  const [comparison, setComparison] = useState(null)
  function clearRun() {setRun(null);setMemo(null);setComparison(null)}
  return {run, memo, priorRun, comparison, setRun, setMemo, setPriorRun, setComparison, clearRun}
}
