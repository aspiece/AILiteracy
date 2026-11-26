const fs=require('node:fs');
const path=require('node:path');
const {test}=require('node:test');
const read=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
const source=read('assets/app.js');
const core=source.slice(source.indexOf('function evaluatePracticeOrder'),source.indexOf("document.querySelectorAll('.question').forEach(question => {"));
const decode=s=>s.replace(/&quot;/g,'"').replace(/&amp;/g,'&');
function attrs(h,id){const tag=h.match(new RegExp('<article class="question" data-question-id="'+id.replace(/\\./g,"\\\\.")+'"[^>]*>'))?.[0];if(!tag)throw Error('Missing '+id);return Object.fromEntries([...tag.matchAll(/(data-[a-z-]+)="([^"]*)"/g)].map(x=>[x[1],decode(x[2])]))}
const q5=attrs(read('lessons/lesson-5.html'),'5.3.1'),q6=attrs(read('lessons/lesson-6.html'),'6.4.1');
test('formative question and alternative workflow regression',()=>{

const {evaluatePracticeOrder,practiceSelectionFeedback}=new Function(core+'\nreturn {evaluatePracticeOrder,practiceSelectionFeedback};')();
const correct=JSON.parse(q6['data-correct']), alternatives=JSON.parse(q6['data-accepted-orders']);
const privacy=JSON.parse(q5['data-correct']);
const results=[];
const assert=(condition,label)=>{if(!condition)throw Error(label);results.push(label)};
assert(evaluatePracticeOrder(correct,correct,alternatives).correct,'canonical ethics sequence accepted');
assert(evaluatePracticeOrder(['A','B','C','E','D','F'],correct,alternatives).correct,'alternative documentation-before-final-check sequence accepted');
assert(!evaluatePracticeOrder(['B','A','C','D','E','F'],correct,alternatives).correct,'drafting before purpose rejected');
assert(!evaluatePracticeOrder(['A','B','C','D','F','E'],correct,alternatives).correct,'approval before documentation rejected');
assert(!evaluatePracticeOrder(['A','B','C','D','D','F'],correct,alternatives).correct,'duplicate action rejected');
assert(!evaluatePracticeOrder(['A','B','C','D','E'],correct,alternatives).correct,'incomplete order rejected');
const diagnostic=evaluatePracticeOrder(['B','A','C','E','D','F'],correct,alternatives);
assert(diagnostic.best===4 && diagnostic.review.join(',')==='1,2','diagnose positions against closest valid alternative');
assert(evaluatePracticeOrder(correct,correct).correct,'legacy single-order question supported');
assert(evaluatePracticeOrder(['A','B','C','E','D','F'],correct).correct===false,'alternate order not accepted unless explicitly configured');
assert(evaluatePracticeOrder(['A','B','C','E','D','F'],correct,[['A','B','C','E','E','F']]).correct===false,'malformed alternate rejected');
assert(practiceSelectionFeedback(privacy,privacy).missing===0,'all responsible privacy actions selected');
let incomplete=practiceSelectionFeedback(['minimize','always-train'],privacy);
assert(incomplete.hits===1 && incomplete.missing===2 && incomplete.extra.join(',')==='always-train','identify missing and extraneous privacy choices');
assert(practiceSelectionFeedback(['minimize','authorized','reuse','delete-now'],privacy).extra.length===1,'reject unsafe deletion despite selecting correct choices');
assert(q5['data-question-type']==='multiple_answers_question','privacy question no longer requires a universal sequence');
assert(JSON.parse(q5['data-choice-hints'])['always-train'].includes('permission')||JSON.parse(q5['data-choice-hints'])['always-train'].includes('Permission'),'specific misconception hint present');

console.log(results.join('\n'));
});
