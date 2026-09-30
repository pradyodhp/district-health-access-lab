import React from 'react'
import {it,expect,vi,afterEach} from 'vitest'
import {render,screen,cleanup,fireEvent,waitFor} from '@testing-library/react'
import Workbench from './Workbench.jsx'
afterEach(()=>{cleanup();vi.unstubAllGlobals()})
const assumption={low:.2,mode:.4,high:.7,unit:'rate',rationale:'Training only'}
const inputs=Object.fromEntries(['eligible','need_rate','awareness_rate','screening_rate','followup_rate','capacity','spend_inr'].map(f=>[f,{...assumption,unit:['eligible','capacity'].includes(f)?'people':f==='spend_inr'?'INR':'rate'}]))
const run={run_id:'run-123',classification:'HYPOTHETICAL',snapshot_digest:'inputs',output_digest:'outputs',disclaimer:'Training only',snapshot:{engine_version:'1',seed:42,simulation_count:500},bands:{screened:{p10:1,p50:2,p90:3}}}
it('journey keeps hypothetical labeling and invalidates a saved result after editing',async()=>{
 vi.stubGlobal('fetch',vi.fn(async url=>({ok:true,json:async()=>url.endsWith('/case')?{name:'Training',version:'1',population:'adults',geography:['Training'],horizon_months:12,budget_inr:100,classification:'HYPOTHETICAL'}:url.endsWith('/evidence')?{warning:'Unverified',records:[]}:url.endsWith('/readiness')?{status:'HYPOTHETICAL_ONLY',score:0,max_score:100,blockers:['Missing evidence'],gates:[]}:url.endsWith('/presets')?{presets:['status-quo','outreach']}:url.endsWith('/hypotheses')?{hypotheses:[]}:url.includes('/scenario/')?{inputs}:run})))
 render(<Workbench/> )
 await waitFor(()=>expect(screen.getByLabelText('Case name').value).toBe('Training'))
 expect(screen.getByText(/REAL DECISION: HOLD/)).toBeTruthy()
 fireEvent.click(screen.getByText('Model & runs'))
 fireEvent.click(await screen.findByText('Run reproducible model'))
 await screen.findByText(/SAVED LOCAL RUN/)
 expect(screen.getByText(/Training only/)).toBeTruthy()
 fireEvent.change(screen.getByLabelText('awareness_rate mode'),{target:{value:'.5'}})
 await waitFor(()=>expect(screen.queryByText(/SAVED LOCAL RUN/)).toBeNull())
})
it('API failure is visible instead of a fabricated success',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>({ok:false,json:async()=>({detail:'Unavailable'})})))
 render(<Workbench/>);expect((await screen.findByRole('alert')).textContent).toContain('Unavailable')
})
