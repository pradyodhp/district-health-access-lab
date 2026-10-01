import { useEffect, useState } from 'react'
import { apiClient as API } from '../services/apiClient.js'

export function useEvidence(setError) {
  const [evidence, setEvidence] = useState(null)
  useEffect(() => {
    let active = true
    Promise.all(['evidence'].map(path => API(path))).then(values => {
      if (active) {setEvidence(values[0])}
    }).catch(error => { if (active) setError(error.message) })
    return () => { active = false }
  }, [setError])
  return {evidence, setEvidence}
}
