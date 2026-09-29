import test from 'node:test'
import assert from 'node:assert/strict'
import {screenedBands, fundingDecision, inputChanged} from './decision-utils.mjs'

test('screened bands only render ordered hypothetical values', () => {
  assert.deepEqual(screenedBands({classification:'HYPOTHETICAL',bands:{screened:{p10:1,p50:2,p90:3}}}),
    {p10:1,p50:2,p90:3,classification:'HYPOTHETICAL'})
  assert.throws(()=>screenedBands({classification:'REAL',bands:{screened:{p10:1,p50:2,p90:3}}}))
  assert.throws(()=>screenedBands({classification:'HYPOTHETICAL',bands:{screened:{p10:3,p50:2,p90:1}}}))
})
test('memo must hold real funding', () => {
  assert.match(fundingDecision({classification:'HYPOTHETICAL',decision:'DECISION ON HOLD - missing screening counts'}),/HOLD/)
  assert.throws(()=>fundingDecision({classification:'HYPOTHETICAL',decision:'Fund district A'}))
})
test('editing model assumptions invalidates stale run', () => {
  assert.equal(inputChanged({eligible:{mode:10}},{eligible:{mode:12}}),true)
  assert.equal(inputChanged({eligible:{mode:10}},{eligible:{mode:10}}),false)
})
