/** UI projections with explicit hypothetical provenance. */
export function screenedBands(run) {
  if (run?.classification !== 'HYPOTHETICAL' || !run.bands?.screened) throw Error('No hypothetical screened band')
  const {p10, p50, p90} = run.bands.screened
  if (![p10,p50,p90].every(Number.isFinite) || p10 > p50 || p50 > p90) throw Error('Invalid screened band')
  return {p10,p50,p90,classification:'HYPOTHETICAL'}
}
export function fundingDecision(memo) {
  if (memo?.classification !== 'HYPOTHETICAL' || !memo.decision?.startsWith('DECISION ON HOLD')) {
    throw Error('Memo cannot be used as a real funding decision')
  }
  return memo.decision
}
export function inputChanged(previous, next) {
  return JSON.stringify(previous) !== JSON.stringify(next)
}
