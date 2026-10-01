import {useState} from 'react'

// Saved-run research or named-preset research, never unsaved edits.
export function useResearchBacklog() {
  const [research, setResearch] = useState(null)
  return {research, setResearch}
}
