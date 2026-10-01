import { useEffect, useState } from 'react'
import { apiClient as API } from '../services/apiClient.js'

export function useCase(setError) {
  const [caseFile, setCaseFile] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [hypotheses, setHypotheses] = useState(null)
  useEffect(() => {
    let active = true
    Promise.all(['case', 'readiness', 'hypotheses'].map(path => API(path))).then(values => {
      if (active) {setCaseFile(values[0]);setReadiness(values[1]);setHypotheses(values[2])}
    }).catch(error => { if (active) setError(error.message) })
    return () => { active = false }
  }, [setError])
  return {caseFile, readiness, hypotheses, setCaseFile, setReadiness, setHypotheses}
}
