export const fmt = n => Number.isFinite(Number(n)) ? Number(n).toLocaleString('en-IN', {maximumFractionDigits: 1}) : 'not available'
export const FIELDS = ['eligible','need_rate','awareness_rate','screening_rate','followup_rate','capacity','spend_inr']
export const defaults = () => ({classification:'HYPOTHETICAL', budget_inr:150000, district_capacity:{'Training cohort':700}, options:[
  {id:'outreach',district:'Training cohort',min_inr:0,max_inr:100000,step_inr:25000,assumed_people_per_inr:.004,max_people:400,depends_on:[]},
  {id:'capacity',district:'Training cohort',min_inr:0,max_inr:100000,step_inr:25000,assumed_people_per_inr:.005,max_people:500,depends_on:['outreach']}
]})
