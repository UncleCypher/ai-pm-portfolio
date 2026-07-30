const state = { nodes: [], edges: [], unary: [], pairwise: new Map(), baseline: null, started: false, updatedProbabilities: null, activeRule: null, selectedNode: null, distributionReady: false };
const $ = (id) => document.getElementById(id);
const label = (i) => String.fromCharCode(97 + i);
const edgeKey = (a, b) => a < b ? `${a}-${b}` : `${b}-${a}`;
const maxEdges = (n) => n * (n - 1) / 2;
const randomPotential = (size) => Array.from({ length: size }, () => BigInt(1 + Math.floor(Math.random() * 9)));
function combinations(n) { const all=[]; for(let i=0;i<n;i++) for(let j=i+1;j<n;j++) all.push([i,j]); return all; }
function shuffle(values) { for(let i=values.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [values[i],values[j]]=[values[j],values[i]]; } return values; }

function createNodes(n) {
  state.nodes = Array.from({ length:n }, (_, i) => label(i));
  state.edges = [];
  state.unary = state.nodes.map(() => randomPotential(2));
  state.pairwise = new Map(); state.selectedNode=null; state.distributionReady=false;
  state.started=false; state.baseline=null; state.updatedProbabilities=null; state.activeRule=null;
  render();
}
function evaluate(model) {
  const rows=[], n=model.nodes.length;
  for(let mask=0;mask<(1<<n);mask++) {
    const bits=Array.from({length:n},(_,i)=>(mask>>(n-i-1))&1);
    let weight=bits.reduce((p,x,i)=>p*model.unary[i][x],1n);
    model.edges.forEach(([a,b]) => { weight *= model.pairwise.get(edgeKey(a,b))[bits[a]*2+bits[b]]; });
    rows.push({bits,weight});
  }
  const z=rows.reduce((sum,row)=>sum+row.weight,0n);
  return { rows, z, numerators: rows.map(row=>row.weight) };
}
function modelNow() { return {nodes:state.nodes,edges:state.edges,unary:state.unary,pairwise:state.pairwise}; }
function cloneModel() { return { nodes:[...state.nodes], edges:state.edges.map(e=>[...e]), unary:state.unary.map(p=>[...p]), pairwise:new Map([...state.pairwise].map(([k,p])=>[k,[...p]])) }; }
function gcd(a,b) { while(b!==0n) [a,b]=[b,a%b]; return a; }
function formatFraction(numerator,denominator) { if(numerator===0n) return '0'; const divisor=gcd(numerator<0n?-numerator:numerator,denominator); return `${numerator/divisor}/${denominator/divisor}`; }
function absolute(value) { return value<0n?-value:value; }

function render() { renderControls(); renderGraph(); renderDistribution(); renderExperiment(); renderIndependenceTable(); }
function renderControls() {
  const n=state.nodes.length;
  $('stat-nodes').textContent=`${n} (${state.nodes.join(', ')})`; $('stat-edges').textContent=state.edges.length; $('stat-states').textContent=`2^${n} = ${2**n}`;
  $('generate-form').querySelectorAll('input,button').forEach(el=>el.disabled=state.started);
  $('finalize-graph').disabled=state.started; $('start-experiment').disabled=state.started || !state.distributionReady;
  $('unfreeze-experiment').classList.toggle('hidden', !state.started);
  $('experiment-status').textContent=state.started ? '实验进行中：原图已冻结；请在下方输入并应用规则。' : '当前处于实验前：可自由修改图结构。';
}
function graphMarkup(nodes, edges, emphasis, height=230, interactive=false) {
  const n=nodes.length,cx=320,cy=height,r=Math.min(135,60+18*n);
  const points=nodes.map((_,i)=>({x:cx+r*Math.cos(-Math.PI/2+i*2*Math.PI/n),y:cy+r*Math.sin(-Math.PI/2+i*2*Math.PI/n)}));
  const edgeMarkup=edges.map(([a,b])=>`<line class="${emphasis && edgeKey(a,b)===emphasis ? 'changed-edge' : 'edge'}" x1="${points[a].x}" y1="${points[a].y}" x2="${points[b].x}" y2="${points[b].y}"/>`).join('');
  return edgeMarkup+points.map((p,i)=>`<g class="${interactive?'interactive-node ':''}${state.selectedNode===i?'selected-node':''}" data-index="${i}"><circle class="node" cx="${p.x}" cy="${p.y}" r="25"/><text class="node-label" x="${p.x}" y="${p.y+1}">${nodes[i]}</text></g>`).join('');
}
function renderGraph() { $('graph').innerHTML=graphMarkup(state.nodes,state.edges,null,230,!state.started); $('graph-caption').textContent=`V = {${state.nodes.join(', ')}}`; }
function renderDistribution() {
  if(!state.distributionReady) { $('normalizer').textContent='待确认图结构'; $('distribution-body').innerHTML='<tr><td colspan="3">请点击节点建立边，然后点击“确认图并生成联合概率分布”。</td></tr>'; return; }
  const {rows,z,numerators}=evaluate(modelNow()); $('normalizer').textContent=`Z = ${z.toString()}`;
  $('distribution-body').innerHTML=rows.map((row,i)=>`<tr><td>${row.bits.map((x,j)=>`${state.nodes[j]}=${x}`).join(', ')}</td><td>${row.weight.toString()}</td><td>${formatFraction(numerators[i],z)}</td></tr>`).join('');
}
function conditionalIndependence(numerators, n, a, b) {
  const groups=new Map();
  numerators.forEach((weight,index)=>{
    let key=''; for(let v=0;v<n;v++) if(v!==a && v!==b) key+=((index>>(n-v-1))&1);
    if(!groups.has(key)) groups.set(key,{ total:0n, joint:[[0n,0n],[0n,0n]] });
    const group=groups.get(key), xa=(index>>(n-a-1))&1, xb=(index>>(n-b-1))&1;
    group.total+=weight; group.joint[xa][xb]+=weight;
  });
  let maximumNumerator=0n, maximumDenominator=1n;
  groups.forEach(({total,joint})=>{
    if(total===0n) return;
    const pa=[joint[0][0]+joint[0][1],joint[1][0]+joint[1][1]], pb=[joint[0][0]+joint[1][0],joint[0][1]+joint[1][1]];
    for(let x=0;x<2;x++) for(let y=0;y<2;y++) {
      const difference=absolute(joint[x][y]*total-pa[x]*pb[y]), denominator=total*total;
      if(difference*maximumDenominator>maximumNumerator*denominator) { maximumNumerator=difference; maximumDenominator=denominator; }
    }
  });
  return { independent: maximumNumerator===0n, maximumNumerator, maximumDenominator };
}
function conditionalDependenceEdges(numerators,n) { return combinations(n).filter(([a,b])=>!conditionalIndependence(numerators,n,a,b).independent); }
function renderIndependenceTable() {
  if(!state.distributionReady) { $('independence-body').innerHTML='<tr><td colspan="6">确认图结构后生成检验结果。</td></tr>'; $('independence-summary').textContent='待确认图结构'; return; }
  const original=state.started ? state.baseline : modelNow();
  const base=evaluate(original), updated=state.updatedProbabilities || base.numerators;
  const updatedEdges=state.updatedProbabilities ? conditionalDependenceEdges(updated,state.nodes.length) : original.edges;
  let independentCount=0;
  const rows=combinations(state.nodes.length).map(([a,b])=>{
    const before=conditionalIndependence(base.numerators,state.nodes.length,a,b), after=conditionalIndependence(updated,state.nodes.length,a,b);
    if(after.independent) independentCount++;
    const originalHasEdge=original.edges.some(([x,y])=>edgeKey(x,y)===edgeKey(a,b));
    const updatedHasEdge=updatedEdges.some(([x,y])=>edgeKey(x,y)===edgeKey(a,b));
    const tag=(value)=>`<span class="${value?'yes':'no'}">${value?'是':'否'}</span>`;
    return `<tr><td>${state.nodes[a]} — ${state.nodes[b]}</td><td>${tag(originalHasEdge)}</td><td>${tag(before.independent)}</td><td>${tag(updatedHasEdge)}</td><td>${tag(after.independent)}</td><td>${formatFraction(after.maximumNumerator,after.maximumDenominator)}</td></tr>`;
  });
  $('independence-body').innerHTML=rows.join('');
  $('independence-summary').textContent=`更新分布：${independentCount} / ${rows.length} 对条件独立`;
}
function populateRuleControls() {
  for(const id of ['if-node','then-node']) $(id).innerHTML=state.nodes.map((x,i)=>`<option value="${i}">${x}</option>`).join('');
  if(state.nodes.length>1) $('then-node').value='1';
}
function renderExperiment() {
  $('experiment-area').classList.toggle('hidden',!state.started);
  if(!state.started) return;
  populateRuleControls();
  $('original-graph').innerHTML=graphMarkup(state.baseline.nodes,state.baseline.edges,null,200);
  if(!state.updatedProbabilities) { $('updated-graph').innerHTML=graphMarkup(state.baseline.nodes,state.baseline.edges,null,200); $('comparison-body').innerHTML=''; $('probability-check').textContent='等待应用规则'; return; }
  const derivedEdges=conditionalDependenceEdges(state.updatedProbabilities,state.nodes.length);
  $('updated-graph').innerHTML=graphMarkup(state.baseline.nodes,derivedEdges,edgeKey(state.activeRule.a,state.activeRule.b),200);
  const base=evaluate(state.baseline), rows=base.rows;
  $('comparison-body').innerHTML=rows.map((row,i)=>{ const delta=state.updatedProbabilities[i]-base.numerators[i], className=delta>0n?'positive':delta<0n?'negative':'neutral', sign=delta>0n?'+':''; return `<tr><td>${row.bits.map((x,j)=>`${state.nodes[j]}=${x}`).join(', ')}</td><td>${formatFraction(base.numerators[i],base.z)}</td><td>${formatFraction(state.updatedProbabilities[i],base.z)}</td><td class="${className}">${sign}${formatFraction(delta,base.z)}</td></tr>`; }).join('');
  $('probability-check').textContent=`Σ P′(x) = ${formatFraction(state.updatedProbabilities.reduce((a,b)=>a+b,0n),base.z)}`;
}

$('generate-form').addEventListener('submit', (event) => {
  event.preventDefault(); const n=Number($('node-count').value);
  if(!Number.isInteger(n)||n<2||n>10) { $('edit-message').textContent='请输入合法的节点数（2–10）。'; return; }
  createNodes(n); $('edit-message').textContent='节点已确认。请在图中依次点击两个节点建立边。';
});
$('graph').addEventListener('click',(event)=>{
  if(state.started) return;
  const node=event.target.closest('.interactive-node'); if(!node) return;
  const index=Number(node.dataset.index);
  if(state.selectedNode===null) { state.selectedNode=index; $('edit-message').textContent=`已选择节点 ${state.nodes[index]}，请点击第二个节点。`; renderGraph(); return; }
  if(state.selectedNode===index) { state.selectedNode=null; $('edit-message').textContent='已取消选择。'; renderGraph(); return; }
  const a=state.selectedNode,b=index,key=edgeKey(a,b),edgeIndex=state.edges.findIndex(([x,y])=>edgeKey(x,y)===key);
  if(edgeIndex>=0) { state.edges.splice(edgeIndex,1); state.pairwise.delete(key); $('edit-message').textContent=`已删除边 ${state.nodes[a]}—${state.nodes[b]}。`; }
  else { state.edges.push(a<b?[a,b]:[b,a]); state.pairwise.set(key,randomPotential(4)); $('edit-message').textContent=`已添加边 ${state.nodes[a]}—${state.nodes[b]}。`; }
  state.selectedNode=null; state.distributionReady=false; state.updatedProbabilities=null; render();
});
$('finalize-graph').addEventListener('click',()=>{ state.distributionReady=true; state.updatedProbabilities=null; $('edit-message').textContent='图结构已确认，已生成精确联合概率分布。'; render(); });
$('start-experiment').addEventListener('click',()=>{ state.baseline=cloneModel(); state.started=true; state.updatedProbabilities=null; state.activeRule=null; $('edit-message').textContent='原图已冻结。'; render(); });
$('unfreeze-experiment').addEventListener('click',()=>{ state.started=false; state.baseline=null; state.updatedProbabilities=null; state.activeRule=null; $('edit-message').textContent='已解冻，可继续生成或编辑图结构。'; render(); });
$('apply-rule').addEventListener('click',()=>{
  const a=Number($('if-node').value),b=Number($('then-node').value),av=Number($('if-value').value),bv=Number($('then-value').value);
  if(a===b) { $('rule-description').textContent='IF 与 THEN 必须选择不同的变量。'; return; }
  const base=evaluate(state.baseline), next=Array(base.numerators.length).fill(0n),n=state.nodes.length;
  base.numerators.forEach((weight,index)=>{ const aValue=(index>>(n-a-1))&1; if(aValue!==av) next[index]+=weight; else { const destination=(index & ~(1<<(n-b-1))) | (bv<<(n-b-1)); next[destination]+=weight; } });
  state.updatedProbabilities=next; state.activeRule={a,b,av,bv};
  $('rule-description').textContent=`已应用 IF ${state.nodes[a]}=${av} THEN ${state.nodes[b]}=${bv}：所有满足条件的状态质量被迁移到 B=${bv} 的对应状态。`;
  renderExperiment(); renderIndependenceTable();
});
createNodes(5);
