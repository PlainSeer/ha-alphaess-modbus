class AlphaESSPowerFlow extends HTMLElement {
  constructor(){super();this.attachShadow({mode:'open'});}
  setConfig(config){
    this._stopFlowFrames();this._motions=new Map();
    this.config=config;
    this.shadowRoot.innerHTML=`<style>
      :host{display:block;margin:0;font-family:var(--ha-font-family-body,var(--paper-font-body1_-_font-family,inherit));color:var(--primary-text-color);container-type:inline-size}
      .flow{position:relative;width:100%;aspect-ratio:640/250;min-height:180px;background:transparent}
      svg{display:block;width:100%;height:100%;position:absolute;inset:0}
      .wire{fill:none;stroke-width:2;stroke-linecap:round;opacity:.45}.flow-dot{pointer-events:none}
      .node{font:inherit;color:inherit;background:none;border:0;padding:0;position:absolute;display:flex;align-items:flex-start;transform:translateY(-24.7px);gap:7px;min-width:0;max-width:29%;cursor:pointer;border-radius:6px;outline-offset:3px}
      .node{border-radius:10px;--ha-ripple-color:var(--button-card-ripple-color);--ha-ripple-hover-color:var(--ha-ripple-color,var(--button-card-ripple-hover-color));--ha-ripple-pressed-color:var(--ha-ripple-color,var(--button-card-ripple-pressed-color));--ha-ripple-hover-opacity:var(--button-card-ripple-hover-opacity,0.04);--ha-ripple-pressed-opacity:var(--button-card-ripple-pressed-opacity,0.12)}
      ha-ripple{position:absolute;inset:-6px;border-radius:10px;pointer-events:none}
      .node:focus-visible{outline:2px solid var(--primary-color)}
      .solar{top:16.8%}.grid{top:86%}.ev{top:51.4%}.battery{top:16.8%}.house{top:86%}.solar,.grid,.ev{right:calc(72.03125% + 12px);flex-direction:row-reverse;text-align:right}.battery,.house{left:calc(72.5% + 12px)}
      ha-icon{--mdc-icon-size:26px;width:26px;height:26px;flex:none;color:var(--accent)}
      .node>div{position:relative}
      .node ha-icon{transform:translateY(11.7px)}
      .label{font-size:12px;line-height:1.3;color:var(--secondary-text-color)}
      .value{font-size:14px;font-weight:700;line-height:1.3;white-space:nowrap;color:var(--primary-text-color)}
      .unit{font-size:10.5px;font-weight:600;margin-left:2px;color:var(--secondary-text-color)}
      .direction{position:absolute;top:100%;left:0;font-size:11px;line-height:1.3;color:var(--secondary-text-color);white-space:nowrap}
      .solar .direction,.grid .direction,.ev .direction{left:auto;right:0}
      .ev-link{position:absolute;right:calc(72.03125% + 24px);top:calc(51.4% + 13px);bottom:calc(14% + 13px);width:2px;background:color-mix(in srgb,#9C27B0 45%,transparent);pointer-events:none}.ev-dot{position:absolute;width:6px;height:6px;border-radius:50%;background:#9C27B0;left:50%;transform:translate(-50%,-50%);}
      @container(max-width:360px){.ev-link{right:calc(72.03125% + 22px);top:calc(51.4% + 11px);bottom:calc(14% + 11px)}}
      @media(prefers-reduced-motion:reduce){.flow-dot,.ev-dot{display:none!important}}
      .inverter{fill:var(--secondary-background-color,var(--card-background-color));stroke:var(--divider-color);stroke-width:1.5}
      .inverter-name{fill:var(--primary-text-color);font-family:inherit;font-size:10px}
      .inverter-display{fill:var(--primary-text-color);opacity:.65}
      @container(max-width:360px){.node{gap:4px}ha-icon{--mdc-icon-size:22px;width:22px;height:22px}.node ha-icon{transform:translateY(13.7px)}.direction{font-size:11px}.battery .direction,.house .direction{left:-26px}.solar .direction,.grid .direction,.ev .direction{right:-26px}}
      @media(max-width:899px){.direction{font-size:11px;letter-spacing:0}.battery .direction,.house .direction{left:-26px;right:auto;transform:none}.solar .direction,.grid .direction,.ev .direction{left:auto;right:-26px;transform:none}}
    </style><div class="flow" role="group" aria-label="Live energy flow">
      <svg viewBox="-24 0 640 250" preserveAspectRatio="none" aria-hidden="true">
        <path class="wire" data-wire="solar" stroke="#FFC107" d="M155 42 H170 Q190 42 190 62 V98 Q190 118 210 118 H240"/>
        <circle class="flow-dot" data-dot="solar" r="5" fill="#FFC107" style="display:none"></circle>
        <path class="wire" data-wire="grid" stroke="#009688" d="M240 139 H210 Q190 139 190 159 V195 Q190 215 170 215 H155"/>
        <circle class="flow-dot" data-dot="grid" r="5" fill="#009688" style="display:none"></circle>
        <path class="wire" data-wire="battery" stroke="#4CAF50" d="M355 118 H385 Q405 118 405 98 V62 Q405 42 425 42 H440"/>
        <circle class="flow-dot" data-dot="battery" r="5" fill="#4CAF50" style="display:none"></circle>
        <path class="wire" data-wire="house" stroke="#2196F3" d="M355 139 H385 Q405 139 405 159 V195 Q405 215 425 215 H440"/>
        <circle class="flow-dot" data-dot="house" r="5" fill="#2196F3" style="display:none"></circle>
        <rect class="inverter" x="247" y="48" width="99" height="161" rx="5"/>
        <rect class="inverter-display" x="285" y="166" width="22" height="36" rx="1"/>
        <text class="inverter-name" x="296" y="88" text-anchor="middle">AlphaESS</text>
      </svg>
      ${[['solar','Solar','mdi:solar-power','#FFC107'],['grid','Grid','mdi:transmission-tower','#009688'],['battery','Battery','mdi:battery-medium','#4CAF50'],['house','Load','mdi:home-lightning-bolt','#2196F3']].map(([kind,label,icon,color])=>`<button type="button" class="node ${kind} cursor-interaction" data-kind="${kind}" style="--accent:${color}"><ha-icon icon="${icon}"></ha-icon><div><div class="label">${label}</div><div class="value"><span data-value="${kind}">—</span><span class="unit" data-unit="${kind}"></span></div><div class="direction" data-direction="${kind}"></div></div><ha-ripple></ha-ripple></button>`).join('')}
    </div>`;
    for(const kind of ['solar','grid','battery','house']){if(config.entities?.[kind])continue;this.shadowRoot.querySelector('[data-value='+kind+']').textContent='n/a';this.shadowRoot.querySelector('[data-direction='+kind+']').textContent='Unavailable';}
    const open=el=>{const id=this.entities[el.dataset.kind];if(!id)return;this.dispatchEvent(new CustomEvent('hass-more-info',{detail:{entityId:id},bubbles:true,composed:true}));};
    this.shadowRoot.querySelectorAll('.node').forEach(el=>{el.addEventListener('click',()=>open(el));el.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();open(el);}});});
    const shell=document.createElement('ha-card');
    shell.innerHTML='<h2>Battery &amp; Grid</h2>';
    shell.append(this.shadowRoot.querySelector('.flow'));
    const summary=document.createElement('div');summary.className='summary';
    const fields=[['soc','Battery','mdi:battery-80'],['health','Health','mdi:battery-heart'],['temperature','Battery temp','mdi:thermometer'],['mode','Work mode','mdi:home-lightning-bolt']];
    for(const [key,label,icon] of fields){if(!config.entities?.[key])continue;const b=document.createElement('button');b.type='button';b.className='summary-item';b.innerHTML='<ha-icon icon="'+icon+'"></ha-icon><div data-summary="'+key+'">—</div><small>'+label+'</small>';b.addEventListener('click',()=>this._open(config.entities[key]));summary.append(b);}
    shell.append(summary);this.shadowRoot.append(shell);
    const style=document.createElement('style');style.textContent='ha-card{display:block;overflow:hidden}h2{margin:0;padding:15px 18px;font-size:17px;font-weight:600;border-bottom:1px solid var(--divider-color)}.flow{margin:20px 8px 13px;width:calc(100% - 16px)}.summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;padding:8px 12px 16px}.summary-item{font:inherit;color:inherit;min-width:0;border:0;background:none;text-align:center;padding:8px 0;cursor:pointer}.summary ha-icon{color:var(--primary-color);display:block;margin:0 auto 6px;transform:none}.summary [data-summary]{font-size:16px;font-weight:600;white-space:nowrap}.summary small{display:block;font-size:12px;color:var(--secondary-text-color);margin-top:3px}.summary-item:focus-visible{outline:2px solid var(--primary-color);border-radius:8px}@container(max-width:360px){.battery .direction,.house .direction{left:-26px;right:auto}.solar .direction,.grid .direction{left:auto;right:-26px}}';style.textContent+='@container(max-width:330px){.solar,.grid{right:calc(72.03125% + 6px)}.battery,.house{left:calc(72.5% + 6px)}.node{gap:4px}.node .value{font-size:13px}.unit{margin-left:1px}.summary{gap:3px;padding-left:8px;padding-right:8px}.summary small{font-size:11px}}';this.shadowRoot.append(style);
    if(this._hass)this.hass=this._hass;
  }
  get entities(){return Object.fromEntries(['solar','grid','battery','house'].filter(k=>this.config.entities?.[k]).map(k=>[k,this.config.entities[k]]));}
  set hass(hass){
    this._hass=hass;if(!this.shadowRoot.querySelector('.flow'))return;
    this._renderSummary();
    for(const [kind,id]of Object.entries(this.entities)){
      const state=hass.states[id],raw=state?.state,n=Number(raw);
      const valid=!!state&&!['unknown','unavailable',''].includes(raw)&&Number.isFinite(n);
      const unit=state?.attributes?.unit_of_measurement||'W';
      this.shadowRoot.querySelector(`[data-value="${kind}"]`).textContent=valid?(unit==='W'?(Math.abs(n)/1000).toFixed(2):Math.abs(n).toFixed(2)):'n/a';
      this.shadowRoot.querySelector(`[data-unit="${kind}"]`).textContent=valid?(unit==='W'?'kW':unit):'';
      const direction=this.shadowRoot.querySelector(`[data-direction="${kind}"]`);
      direction.textContent=!valid?'Unavailable':kind==='grid'?(n<0?'Exporting ↓':n>0?'Importing ↑':'Idle'):kind==='battery'?(n<0?'Charging ↓':n>0?'Discharging ↑':'Idle'):kind==='ev'?(n>0?'Charging ←':n===0?'Idle':'Check reading'):'';
      const wire=this.shadowRoot.querySelector(`[data-wire="${kind}"]`);
      const active=valid&&(kind==='ev'?n>0:n!==0)&&['grid','battery','ev'].includes(kind);
      let flowColor=wire.getAttribute('stroke')||'#9C27B0';
      if(kind==='grid'||kind==='battery'){
        flowColor=valid&&n!==0?(n<0?'#4CAF50':'#FF9800'):'var(--secondary-text-color)';
      }
      direction.style.color=active?flowColor:'var(--secondary-text-color)';
      wire.style.animationDuration=this._flowSeconds(n,unit).toFixed(3)+'s';
      wire.style.animationPlayState=valid&&(kind==='ev'?n>0:n!==0)?'running':'paused';
      wire.style.animationDirection=kind==='ev'?'normal':((kind==='grid'||kind==='battery')?n>0:n<0)?'reverse':'normal';
      const dot=this.shadowRoot.querySelector(`[data-dot="${kind}"]`);
      this._queueFlowMotion(kind,wire,dot,kind==='ev');
      const node=this.shadowRoot.querySelector(`[data-kind="${kind}"]`);
      node.setAttribute('aria-label',node.querySelector('.label').textContent+' '+node.querySelector('.value').textContent+' '+direction.textContent);
    }
  }
  _open(entityId){this.dispatchEvent(new CustomEvent('hass-more-info',{detail:{entityId},bubbles:true,composed:true}));}
  _renderSummary(){for(const item of this.shadowRoot.querySelectorAll('[data-summary]')){const key=item.dataset.summary,s=this._hass.states[this.config.entities?.[key]],raw=s?.state;const valid=!!s&&!['unknown','unavailable',''].includes(raw)&&Number.isFinite(Number(raw));let value=valid?String(Number(Number(raw).toFixed(1))):'Unavailable';if(valid){if(key==='mode')value=({'1':'Normal','2':'UPS'})[raw]||raw;else value+=' '+(s.attributes?.unit_of_measurement||'');}item.textContent=value;}}
  _queueFlowMotion(kind,wire,dot,html=false){
    this._motions ||= new Map();
    let m=this._motions.get(kind);
    const moving=wire.style.animationPlayState==='running';
    const direction=wire.style.animationDirection==='reverse'?-1:1;
    if(!m||m.dot!==dot){m={wire,dot,html,phase:0,speed:0,target:0,direction,hasRun:false};this._motions.set(kind,m);}
    if(moving&&!m.hasRun){m.phase=direction<0?1:0;m.hasRun=true;}
    m.moving=moving;m.direction=direction;
    m.target=moving?1/(parseFloat(wire.style.animationDuration)||2):0;
    if(!moving)m.speed=0;
    if(html)dot.hidden=!moving;else dot.style.display=moving?'':'none';
    if(moving&&this.isConnected)this._paintFlowDot(m);
    this._scheduleFlowFrame();
  }
  _advanceFlowMotion(m,dt){
    if(!m.moving)return;
    const decay=Math.exp(-dt/.45);
    const distance=m.target*dt+(m.speed-m.target)*.45*(1-decay);
    m.speed=m.target+(m.speed-m.target)*decay;
    m.phase=((m.phase+m.direction*distance)%1+1)%1;
  }
  _paintFlowDot(m){
    if(m.html){m.dot.style.top=((1-m.phase)*100)+'%';return;}
    if(!m.length)m.length=m.wire.getTotalLength();
    const p=m.wire.getPointAtLength(m.phase*m.length);
    m.dot.setAttribute('cx',p.x);m.dot.setAttribute('cy',p.y);
  }
  _scheduleFlowFrame(){
    if(this._flowFrame||!this.isConnected||document.hidden||this._reduceFlow?.matches||![...(this._motions?.values()||[])].some(m=>m.moving))return;
    this._flowFrame=requestAnimationFrame(t=>{
      this._flowFrame=0;
      const dt=this._flowTime===undefined?0:Math.min(.05,Math.max(0,(t-this._flowTime)/1000));
      this._flowTime=t;
      for(const m of this._motions.values())if(m.moving){this._advanceFlowMotion(m,dt);this._paintFlowDot(m);}
      this._scheduleFlowFrame();
    });
  }
  _stopFlowFrames(){if(this._flowFrame)cancelAnimationFrame(this._flowFrame);this._flowFrame=0;this._flowTime=undefined;}
  connectedCallback(){
    this._reduceFlow=window.matchMedia?.('(prefers-reduced-motion: reduce)');
    this._flowVisibility=()=>{this._stopFlowFrames();this._scheduleFlowFrame();};
    document.addEventListener('visibilitychange',this._flowVisibility);
    this._reduceFlow?.addEventListener?.('change',this._flowVisibility);
    this._scheduleFlowFrame();
  }
  disconnectedCallback(){
    this._stopFlowFrames();
    document.removeEventListener('visibilitychange',this._flowVisibility);
    this._reduceFlow?.removeEventListener?.('change',this._flowVisibility);
  }
  _flowSeconds(value,unit='W'){const watts=Math.abs(Number(value))*(unit==='kW'?1000:1);return Number.isFinite(watts)?Math.max(.8,Math.min(6,6/(1+Math.sqrt(watts/500)))):6;}
  getCardSize(){return 3;}
}
if(!customElements.get('alphaess-power-flow'))customElements.define('alphaess-power-flow',AlphaESSPowerFlow);
