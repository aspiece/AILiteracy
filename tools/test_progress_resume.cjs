const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../assets/app.js'), 'utf8');
const core = source.slice(0, source.indexOf("document.querySelector('.menu-button')"));
test('progress resume validation, restore, and storage failure', () => {

const results = [];
function assert(condition, label) { if (!condition) throw Error(label); results.push(label); }
function makeHarness(disabled = false) {
  const store = new Map();
  const storage = {
    getItem(k) { if (disabled) throw Error('blocked'); return store.get(k) ?? null; },
    setItem(k,v) { if (disabled) throw Error('blocked'); store.set(k,v); },
    removeItem(k) { if (disabled) throw Error('blocked'); store.delete(k); }
  };
  const choice = (name,value,type='radio') => ({name,value,type,tagName:'INPUT',dataset:{},checked:false});
  const a=choice('q1','A'), b=choice('q1','B');
  const c=choice('q2','C','checkbox'), d=choice('q2','D','checkbox');
  const sel={name:'',type:'select-one',tagName:'SELECT',dataset:{responseId:'row-1'},options:[{value:''},{value:'opt-1'},{value:'opt-2'}],value:''};
  const r=choice('program-risk-1','1'), r2=choice('program-risk-1','2');
  const group=(id,controls)=>({dataset:{questionId:id},closest(){return null},querySelectorAll(){return controls}});
  const card={dataset:{program:'HVAC'},closest(){return this},querySelectorAll(){return [r,r2]},contains(x){return [r,r2].includes(x)}};
  const sim={dataset:{feedbackMode:'program-scenario'},querySelectorAll(){return [card]}};
  const handlers={};
  const document={
    body:{dataset:{lesson:'1'}},
    querySelectorAll(q) {
      if(q==='.question, .scenario-card')return [group('1.2.1',[a,b]),group('1.2.2',[c,d]),group('1.2.3',[sel]),card];
      if(q==='.scenario-simulation')return [sim];
      if(q==='.lesson-step')return Array(6).fill({});
      return [];
    },
    addEventListener(name,handler){handlers[name]=handler},
    contains(){return true}
  };
  const factory = new Function('document','localStorage', core+'\nreturn {practice, sanitizePractice, localProgress, restoreChoices, rememberScenario, savePractice};');
  return {...factory(document,storage),store,document,a,b,c,d,sel,r,r2,card,handlers};
}
const h=makeHarness();
const base={version:1,lesson:'1',step:3,choices:{'1.2.1:q1':['B'],'1.2.2:q2':['C','D'],'1.2.3:row-1':['opt-2'],'scenario:HVAC:program-risk-1':['1']},scenarios:{'program-scenario':'HVAC'}};
const imported=h.sanitizePractice({...base,studentName:'not retained',reflection:'not retained',choices:{...base.choices,unknown:['free text']}});
assert(imported && imported.step===3,'valid same-lesson resume');
assert(!('studentName' in imported)&&!('reflection' in imported)&&!('unknown' in imported.choices),'strip unrecognized fields and free text');
assert(h.sanitizePractice({...base,lesson:'2'})===null,'reject another lesson');
assert(h.sanitizePractice({...base,version:99})===null,'reject unsupported version');
assert(h.sanitizePractice({...base,step:6})===null,'reject out-of-range step');
assert(h.sanitizePractice({...base,step:1.5})===null,'reject fractional step');
assert(h.sanitizePractice({...base,choices:{'1.2.1:q1':['A','B']}})===null,'reject multiple radio values');
assert(h.sanitizePractice({...base,choices:{'1.2.2:q2':['C','C']}})===null,'reject duplicate choices');
assert(h.sanitizePractice({...base,choices:{'1.2.3:row-1':['unknown']}})===null,'reject unknown select option');
assert(h.sanitizePractice({...base,choices:{'1.2.1:q1':[123]}})===null,'reject non-string choice');
assert(h.sanitizePractice({...base,scenarios:{'program-scenario':'Unknown'}})===null,'reject unknown career scenario');
Object.assign(h.practice,imported);
h.restoreChoices();
assert(h.b.checked&&!h.a.checked&&h.c.checked&&h.d.checked&&h.sel.value==='opt-2'&&h.r.checked,'restore radio checkbox select and scenario by value');
h.b.checked=false;h.a.checked=true;h.handlers.change({target:h.a});
assert(JSON.parse(h.store.get('ai-literacy-practice-v1-1')).choices['1.2.1:q1'][0]==='A','persist updated answer');
h.rememberScenario('program-scenario',h.card);
assert(JSON.parse(h.store.get('ai-literacy-practice-v1-1')).scenarios['program-scenario']==='HVAC','persist active scenario');
h.rememberScenario('program-scenario',null);
assert(!JSON.parse(h.store.get('ai-literacy-practice-v1-1')).scenarios['program-scenario'],'clear active scenario without erasing other answers');
const blocked=makeHarness(true);
assert(blocked.localProgress.available===false&&blocked.savePractice()===false,'blocked storage handled without crash');

console.log(results.join('\n'));
});
