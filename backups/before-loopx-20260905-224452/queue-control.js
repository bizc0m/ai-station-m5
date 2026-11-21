(async () => {
  const form = document.getElementById('queue-form');
  const list = document.querySelector('.tasks');
  const notice = document.createElement('p'); notice.setAttribute('role','status'); notice.className='queue-message';form.after(notice);
  const style=document.createElement('style');style.textContent='.queue-actions,.queue-config{display:grid;gap:8px;margin-top:12px}.queue-config{grid-template-columns:1fr 1fr}.queue-config label{font-size:12px}.queue-result{white-space:pre-wrap;overflow-wrap:anywhere;max-height:360px;overflow:auto;font-size:12px}.queue-message{color:#9a6a11;margin:8px 0}button:disabled{opacity:.55;cursor:default}.task.review{border-left-color:#386fa4}@media(max-width:760px){.compose,.queue-config{grid-template-columns:1fr}.compose>*{grid-column:1!important}}';document.head.append(style);
  async function api(url,options){const response=await fetch(url,{cache:'no-store',...options});const data=await response.json();if(!response.ok)throw new Error(data.error||'Erreur serveur');return data;}
  function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
  let caps;
  try{caps=await api('/queue/capabilities');}catch(error){notice.textContent=error.message;return;}
  if(caps.model_error)notice.textContent=caps.model_error;
  const note=el('p','Choisis l’agent, le modèle et le dossier, puis Exécuter. Une exécution à la fois sur M5. Les réponses des agents sont à vérifier.');note.style.marginBottom='12px';form.before(note);
  function config(container,values={},suffix='nouvelle tâche'){
    const fields={};const box=el('div',undefined,'queue-config');
    box.style.gridColumn='1 / -1';
    function field(name,label,node){const wrap=el('label',label);node.name=name;node.setAttribute('aria-label',label+' · '+suffix);wrap.append(node);box.append(wrap);fields[name]=node;return node;}
    const machine=field('machine','Machine',el('select'));
    for(const m of caps.machines){const o=el('option',m.label);o.value=m.id;o.disabled=!m.available;machine.append(o);}machine.value=values.machine||'M5';
    const agent=field('agent','Agent',el('select'));
    for(const a of caps.agents){const o=el('option',a.label+(a.available?'':' · absent'));o.value=a.id;o.disabled=!a.available;agent.append(o);}agent.value=values.agent||'codex';if(!agent.value)agent.value='codex';
    const modelWrap=el('label','Modèle');box.append(modelWrap);
    function changeModel(saved=''){
      const local=['aider','ollama'].includes(agent.value);let model=el(local?'select':'input');model.name='model';model.setAttribute('aria-label','Modèle · '+suffix);
      if(local){const empty=el('option','Choisir un modèle installé');empty.value='';model.append(empty);for(const name of caps.models){const o=el('option',name);o.value=name;model.append(o);}}
      else model.placeholder=agent.value==='opencode'?'Défaut configuré ou provider/modèle':'Modèle configuré par défaut';
      model.value=saved;modelWrap.replaceChildren(document.createTextNode('Modèle'),model);fields.model=model;
    }
    agent.addEventListener('change',()=>changeModel());changeModel(values.model||'');
    container.append(box);return fields;
  }
  form.elements.agent.remove();
  const project=el('input');project.name='project';project.placeholder='Chemin du projet sur M5';project.setAttribute('aria-label','Chemin du projet sur M5');project.style.gridColumn='1 / -1';form.querySelector('textarea').after(project);
  const composeConfig=config(form);
  form.querySelector('button').before(composeConfig.agent.closest('.queue-config'));
  const drafts=new Map();const configs=new Map();const resultReaders=new Map();
  let signature='',refreshing=false,fetchError=false;
  const labels={pending:'En attente',doing:'En cours',blocked:'Bloquée',review:'À vérifier',done:'Terminée'};
  async function refresh(){
    if(refreshing)return;refreshing=true;
    try{
      const data=await api('/queue/state');if(fetchError){notice.textContent='';fetchError=false;}const updated=JSON.stringify(data);
      if(updated===signature){for(const [id,read] of resultReaders){const details=list.querySelector('details[data-id="'+id+'"]');if(details?.open)await read();}return;}
      for(const [id,fields] of configs)drafts.set(id,Object.fromEntries(Object.entries(fields).map(([key,node])=>[key,node.value])));
      const opened=new Set(Array.from(list.querySelectorAll('details[open]')).map(n=>n.dataset.id));
      signature=updated;list.replaceChildren();configs.clear();resultReaders.clear();
      const counts={};const order={doing:0,pending:1,blocked:2,review:3,done:4};
      const tasks=[...data.tasks].sort((a,b)=>(order[a.status]??5)-(order[b.status]??5)||b.priority-a.priority);
      const busy=tasks.some(t=>t.status==='doing'&&t.run);
      for(const task of tasks){
        counts[task.status]=(counts[task.status]||0)+1;
        const card=el('article',undefined,'task '+task.status);card.append(el('div',`${task.id} · ${labels[task.status]||task.status} · P${task.priority}`,'task-top'),el('h2',task.title),el('p',task.notes||''),el('div',`${task.agent||'À choisir'} · ${task.machine||'M5'} · ${task.model||'modèle par défaut'} · ${task.project||'Projet à préciser'}`,'meta'));
        const actions=el('div',undefined,'queue-actions');
        if(['pending','blocked'].includes(task.status)){
          const values={...task,...drafts.get(task.id)};const fields=config(actions,values,task.id);
          const path=el('input');path.value=values.project||'';path.placeholder='Chemin du projet sur M5';path.setAttribute('aria-label','Projet '+task.id);fields.project=path;configs.set(task.id,fields);
          const button=el('button',task.run?'Relancer':'Exécuter');button.type='button';button.disabled=busy;
          button.addEventListener('click',async()=>{button.disabled=true;notice.textContent='Démarrage de '+task.id+'…';try{const payload={id:task.id,...Object.fromEntries(Object.entries(fields).map(([key,node])=>[key,node.value]))};await api('/queue/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});notice.textContent=task.id+' envoyé à '+fields.agent.value+' sur '+fields.machine.value;await refresh();}catch(error){notice.textContent=error.message;button.disabled=false;}});
          actions.append(path,button);
        }
        if(task.status==='doing'&&task.run){
          const stop=el('button',task.run.cancel_requested?'Arrêt demandé…':'Arrêter');stop.type='button';stop.disabled=!!task.run.cancel_requested;
          stop.addEventListener('click',async()=>{try{await api('/queue/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:task.id})});await refresh();}catch(error){notice.textContent=error.message;}});actions.append(stop);
        }
        if(task.run){
          const details=el('details');details.dataset.id=task.id;const output=el('pre','Chargement…','queue-result');details.append(el('summary','Résultat / journal'),output);
          async function read(){try{const data=await api('/queue/result?id='+encodeURIComponent(task.id));let text=data.text;try{const parsed=JSON.parse(text);text=parsed.summary||text;}catch(_){}output.textContent=text;}catch(error){output.textContent=error.message;}}
          resultReaders.set(task.id,read);details.addEventListener('toggle',()=>{if(details.open)read();});if(opened.has(task.id))details.open=true;actions.append(details);
          if(task.run.error)actions.append(el('p',task.run.error,'queue-message'));
        }
        if(task.status==='review'){
          const validate=el('button','Valider le résultat');validate.type='button';validate.addEventListener('click',async()=>{try{await api('/queue/validate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:task.id})});await refresh();}catch(error){notice.textContent=error.message;}});actions.append(validate);
        }
        for(const a of task.attachments||[]){const link=el('a',a.name,'attachment');link.href='/open-path?path='+encodeURIComponent(a.path);actions.append(link);}
        const events=el('ul');for(const event of(task.events||[]).slice(-3))events.append(el('li',`${event.at} · ${event.text}`));card.append(actions,events);list.append(card);
      }
      const counter=document.querySelector('.counts');counter.replaceChildren();for(const state of['pending','doing','blocked','review','done'])counter.append(el('span',`${labels[state]} ${counts[state]||0}`,'pill'));
      document.querySelector('.sub').textContent='Agents M5 · états et résultats actualisés toutes les 3 s';
    }catch(error){notice.textContent=error.message;fetchError=true;}finally{refreshing=false;}
  }
  await refresh();setInterval(refresh,3000);
})();
