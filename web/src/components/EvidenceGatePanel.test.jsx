import React from 'react'
import {describe,it,expect,afterEach} from 'vitest'
import {render,screen,cleanup} from '@testing-library/react'
import EvidenceGatePanel from './EvidenceGatePanel.jsx'
import RunMetadata from './RunMetadata.jsx'
afterEach(cleanup)
describe('Evidence-first components',()=>{
 it('renders HOLD with reason and research action, not a recommendation',()=>{
  render(<EvidenceGatePanel readiness={{gates:[{id:'SCREENING_COVERAGE',status:'HOLD',reason:'Proxy is not screening coverage',next_research_action:'Get distinct-person counts'}]}}/> )
  expect(screen.getByText('HOLD')).toBeTruthy()
  expect(screen.getByText('Proxy is not screening coverage')).toBeTruthy()
  expect(screen.getByText('Get distinct-person counts')).toBeTruthy()
 })
 it('shows loading rather than a fake gate success',()=>{
  render(<EvidenceGatePanel/>);expect(screen.getByRole('status').textContent).toContain('Loading')
 })
 it('makes run integrity and storage boundaries visible',()=>{
  render(<RunMetadata run={{snapshot:{engine_version:'1',seed:42,simulation_count:100},snapshot_digest:'inputs',output_digest:'outputs'}}/> )
  expect(screen.getByText('outputs')).toBeTruthy();expect(screen.getByText(/not durable/)).toBeTruthy()
 })
})
