"""Exercise every compatibility API pattern against a running local service."""
import json
import sys
import httpx
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000'
c=httpx.Client(base_url=base,timeout=30)
paths=['/health','/api/health','/api/indicators','/api/case','/api/evidence','/api/readiness','/api/hypotheses',
       '/api/research-backlog','/api/research/status-quo','/api/robustness','/api/reversal/status-quo/outreach',
       '/api/threshold/status-quo','/api/presets','/api/scenario/status-quo','/api/compare/status-quo/outreach']
for path in paths:c.get(path).raise_for_status()
e=c.get('/api/evidence').json()['records'][0];c.get('/api/evidence/'+e['id']+'/lineage').raise_for_status()
case=c.get('/api/case').json();inputs=c.get('/api/scenario/status-quo').json()['inputs']
c.post('/api/case/readiness',json=case).raise_for_status();c.post('/api/scenario',json=inputs).raise_for_status()
r=c.post('/api/runs',json=dict(case=case,inputs=inputs,scenario_id='smoke',scenario_version='1',simulation_count=100,seed=42));r.raise_for_status();run=r.json()['run_id']
for path in [f'/api/runs/{run}',f'/api/runs/{run}/memo',f'/api/runs/{run}/replay',f'/api/runs/{run}/compare/{run}']:c.get(path).raise_for_status()
c.post('/api/optimize',json=dict(budget_inr=100,district_capacity={'Training':100},options=[dict(id='one',district='Training',min_inr=0,max_inr=100,step_inr=50,assumed_people_per_inr=1,max_people=100)])).raise_for_status()
assert c.get('/api/scenario/status-quo?draws=1').status_code==422
assert c.get('/api/robustness?seed=-1').status_code==422
print(json.dumps({'status':'PASS','classification':'HYPOTHETICAL','run_id':run}))
