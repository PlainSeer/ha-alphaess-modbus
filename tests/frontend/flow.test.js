import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
const dom=new JSDOM('<!doctype html><body></body>');
for(const key of ['window','document','HTMLElement','customElements','CustomEvent'])globalThis[key]=dom.window[key];
await import('../../custom_components/alphaess_modbus/frontend/alphaess-power-flow.js');
function fixture(){const card=document.createElement('alphaess-power-flow');card.setConfig({entities:{solar:'sensor.sun',grid:'sensor.grid',battery:'sensor.bat',house:'sensor.load',soc:'sensor.soc'}});return card;}
test('standalone flow registers without any strategy or registry call and contains no EV',()=>{
 const card=fixture();assert.equal(card.shadowRoot.querySelectorAll('.node').length,4);
 assert.equal(card.shadowRoot.querySelector('[data-kind=ev],[data-wire=ev]'),null);
 assert.equal(customElements.get('ll-strategy-dashboard-alphaess-modbus'),undefined);
 assert.deepEqual(Object.keys(card.entities),['solar','grid','battery','house']);
});
test('signed directions, missing values, summary and details use configured entity IDs only',()=>{
 const card=fixture();let opened;card.addEventListener('hass-more-info',e=>opened=e.detail.entityId);
 for(const value of ['-1400','1400','0','unavailable']){
  const states=Object.fromEntries(Object.values(card.entities).map(id=>[id,{state:value,attributes:{unit_of_measurement:'W'}}]));
  states['sensor.soc']={state:'78',attributes:{unit_of_measurement:'%'}};
  card.hass={states,callService:()=>assert.fail('Unexpected service call'),callWS:()=>assert.fail('Unexpected registry request')};
  assert.equal(card.shadowRoot.querySelector('[data-direction=grid]').textContent,value==='unavailable'?'Unavailable':Number(value)<0?'Exporting ↓':Number(value)>0?'Importing ↑':'Idle');
  assert.equal(card.shadowRoot.querySelector('[data-value=battery]').textContent,value==='unavailable'?'n/a':(Math.abs(Number(value))/1000).toFixed(2));
  assert.equal(card.shadowRoot.querySelector('[data-summary=soc]').textContent,'78 %');
 }
 card.shadowRoot.querySelector('[data-kind=grid]').click();assert.equal(opened,'sensor.grid');
 card.hass={states:{}};assert.equal(card.shadowRoot.querySelector('[data-value=grid]').textContent,'n/a');
 assert.equal(card.shadowRoot.querySelector('[data-summary=soc]').textContent,'Unavailable');
});
