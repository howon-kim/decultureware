import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';
import { webcrypto } from 'node:crypto';
const source = readFileSync(new URL('../feedback.js', import.meta.url), 'utf8');
function fixture(lang = 'ko') {
  const listeners = {};
  const state = { payload: { app:'bananacal', kind:'bug', platform:'ios', version:'2.0', email:'test@example.com', message:'Keep this draft', website:'' }, calls:[], resets:0 };
  const button = { disabled:true, textContent:'' }, fields = {disabled:false};
  const status = {textContent:'',dataset:{},focus(){}};
  const form = {
    action:'https://site.example/api/feedback.php',
    querySelector: s => s==='fieldset' ? fields : button,
    addEventListener: (name, cb) => listeners[name] = cb,
    reportValidity: () => true,
    setAttribute(){}, removeAttribute(){}, reset(){state.resets++;}
  };
  state.respond = async () => ({ok:true,status:200,json:async()=>({ok:true})});
  vm.runInNewContext(source, {
    document:{documentElement:{lang}, querySelector:()=>form, getElementById:()=>status},
    FormData: class { constructor(){return Object.entries(state.payload);} },
    crypto:webcrypto, Uint8Array, AbortController, setTimeout, clearTimeout,
    fetch: async (url, options) => {state.calls.push(JSON.parse(options.body));return state.respond();}
  });
  return {state,button,fields,status, submit:()=>listeners.submit({preventDefault(){}}),input:()=>listeners.input()};
}
for (const lang of ['en','ko']) {
  const f=fixture(lang);
  f.state.respond=async()=>({ok:false,status:503,json:async()=>({ok:false})});
  await f.submit();
  assert.equal(f.state.resets,0);assert.equal(f.status.dataset.state,'error');assert.equal(f.button.disabled,false);
  const previousID=f.state.calls[0].submission_id;
  f.state.respond=async()=>({ok:true,status:200,json:async()=>({ok:true})});
  await f.submit();
  assert.equal(f.state.calls[1].submission_id,previousID);assert.equal(f.state.resets,1);assert.equal(f.status.dataset.state,'success');
  f.state.respond=async()=>{throw new Error('offline');};await f.submit();
  assert.equal(f.state.resets,1);assert.equal(f.status.dataset.state,'error');
  const failedID=f.state.calls.at(-1).submission_id;
  f.input();await f.submit();assert.notEqual(f.state.calls.at(-1).submission_id,failedID);
  f.state.respond=async()=>({ok:true,status:200,json:async()=>{throw new Error('not JSON');}});await f.submit();
  assert.equal(f.state.resets,1);assert.equal(f.status.dataset.state,'error');
  f.state.respond=async()=>({ok:false,status:429,json:async()=>({ok:false})});await f.submit();assert.match(f.status.textContent,/10/);
  let finish;
  f.state.respond=()=>new Promise(resolve=>finish=resolve);
  const pending=f.submit();const count=f.state.calls.length;
  assert.equal(f.fields.disabled,true);await f.submit();assert.equal(f.state.calls.length,count);
  finish({ok:true,status:200,json:async()=>({ok:true})});await pending;
  assert.equal(f.fields.disabled,false);
}
console.log('PASS: EN/KO success, errors, offline, invalid response, rate limit, double-click, retained draft and stable retry ID');
