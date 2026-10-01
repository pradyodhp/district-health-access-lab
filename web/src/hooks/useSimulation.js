import {useEffect, useState} from 'react'
import {apiClient as API} from '../services/apiClient.js'

export function useSimulation(selected, setError) {
  const [inputs, setInputs] = useState(null)
  useEffect(() => {
    let active = true
    setInputs(null)
    API('scenario/' + selected).then(value => {
      if (active) setInputs(value.inputs)
    }).catch(error => { if (active) setError(error.message) })
    return () => { active = false }
  }, [selected, setError])
  return {inputs, setInputs}
}
