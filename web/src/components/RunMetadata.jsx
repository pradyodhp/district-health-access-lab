import React from 'react'
export default function RunMetadata({run}) {
  return <dl className="run-metadata"><dt>Engine</dt><dd>{run.snapshot.engine_version || 'legacy'}</dd><dt>Input SHA256</dt><dd><code>{run.snapshot_digest}</code></dd><dt>Output SHA256</dt><dd><code>{run.output_digest || 'not recorded'}</code></dd><dt>Seed / draws</dt><dd>{run.snapshot.seed} / {run.snapshot.simulation_count}</dd><dt>Storage</dt><dd>Local JSON, not durable hosted persistence</dd></dl>
}
