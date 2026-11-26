const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { test } = require('node:test');
const read = i => fs.readFileSync(path.join(__dirname, '..', 'lessons', 'lesson-' + i + '.html'), 'utf8');
const decode = s => s.replace(/&amp;/g,'&').replace(/&#x27;/g,"'").replace(/&quot;/g,'"');
function activity(html,i) {
  const start=html.indexOf('id="step-'+i+'-5"');
  const end=html.indexOf('<aside class="lesson-feedback"',start);
  assert.ok(start>=0 && end>start, 'application boundary');
  return html.slice(start,end);
}
function cards(s,kind) {
  return [...s.matchAll(new RegExp('<article class="scenario-card '+kind+'"[^>]*data-program="([^"]+)"[^>]*>[\\s\\S]*?<\\/article>','g'))];
}
const cases = ['HVAC (Heating, Ventilation and Air Conditioning)','Electrical Wiring','Other career program'];
test('career choices and dedicated interactive cards',()=>{
  for(const [i,selectId,kind] of [[1,'program-scenario-select','program-scenario-card'],[3,'media-program-select','media-audit-card']]){
    const s=activity(read(i),i);
    const select=s.match(new RegExp('<select[^>]*id="'+selectId+'"[^>]*>[\\s\\S]*?<\\/select>'))[0];
    const opts=[...select.matchAll(/<option value="(\d+)">([^<]+)<\/option>/g)];
    const deck=cards(s,kind);
    assert.equal(opts.length,18);
    assert.equal(deck.length,18);
    for(let j=0;j<18;j++){
      assert.equal(Number(opts[j][1]),j+1);
      assert.equal(decode(opts[j][2]),decode(deck[j][1]));
    }
    assert.deepEqual(deck.slice(-3).map(m=>decode(m[1])),cases);
    const names=new Set();
    for(const m of deck.slice(-3)){
      const card=m[0];
      for(const group of new Set([...card.matchAll(/name="([^"]+)"/g)].map(q=>q[1]))){
        assert.ok(!names.has(group),'unique radio group');
        names.add(group);
      }
      if(i===1){
        assert.equal((card.match(/class="scenario-check"/g)||[]).length,3);
        assert.equal((card.match(/<textarea/g)||[]).length,1);
        assert.equal((card.match(/class="scenario-exemplar"/g)||[]).length,1);
        assert.equal((card.match(/data-correct="\[&quot;1&quot;\]"/g)||[]).length,3);
      } else {
        const fields=[...card.matchAll(/<fieldset class="audit-question" data-correct="([^"]+)">([\s\S]*?)<\/fieldset>/g)];
        assert.equal(fields.length,4);
        fields.forEach(q=>{
          const values=[...q[2].matchAll(/type="radio"[^>]*value="([^"]+)"/g)].map(v=>v[1]);
          assert.equal(values.length,4);
          assert.ok(values.includes(q[1]));
        });
        const imgs=[...card.matchAll(/src="data:image\/svg\+xml,([^"]+)" alt="([^"]+)"/g)];
        assert.equal(imgs.length,2);
        imgs.forEach(m=>{assert.ok(decodeURIComponent(m[1]).startsWith('<svg '));assert.ok(decodeURIComponent(m[1]).endsWith('</svg>'));assert.ok(m[2].length>15);});
      }
    }
  }
});
test('HVAC, Electrical Wiring, Other represented in other applications',()=>{
  for(const i of [4,5,6,7]){
    const s=activity(read(i),i);
    cases.forEach(n=>assert.ok(s.includes(n),'lesson '+i+' lacks '+n));
  }
});
test('bias evidence is not a supplied verdict',()=>{
  const s=activity(read(4),4);
  const start=s.indexOf('Program Case File Matrix');
  const table=s.slice(start,s.indexOf('</tbody>',start));
  assert.ok(table.includes('Fictional case evidence'));
  assert.ok(!table.includes('Required Action'));
  assert.ok(!table.includes('Stop &amp; Re-evaluate'));
  assert.ok(table.includes('9 of 10 known service concerns'));
  assert.ok(table.includes('4 of 10 on older equipment'));
});
