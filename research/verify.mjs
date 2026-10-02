import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),A=require('../dist/analytics.js');
const D=JSON.parse(fs.readFileSync('dist/data.json','utf8')),html=fs.readFileSync('dist/index.html','utf8');
assert.equal(D.catalog.length,62);assert.equal(D.observations.length,1850);
assert.deepEqual(D.history,['2016-01','2025-12']);
assert.equal(D.observations.filter(o=>o.date<'2021-01').length,311);
assert.equal(new Set(D.observations.map(o=>o.metric+'|'+o.date)).size,D.observations.length);
const catalog=Object.fromEntries(D.catalog.map(c=>[c.id,c]));
for(const o of D.observations){assert.ok(catalog[o.metric]);assert.match(o.date,/^(201[6-9]|202[0-6])-(0[1-9]|1[0-2])$/);assert.ok(o.date<='2026-08');assert.ok(Number.isFinite(o.value));assert.match(o.url,/^https:\/\//);if(!o.metric.includes('profit')&&!o.metric.endsWith('_ppi'))assert.ok(o.value>=0);}
assert.equal(A.series(D,'ratio_mara').filter(o=>o.date>='2021-01'&&o.date<='2025-12').length,59);
assert.equal(A.series(D,'ratio_mara').find(o=>o.date==='2024-10'),undefined);
assert.ok(A.series(D,'slaughter').every(o=>o.date<'2025-07'));
assert.ok(A.series(D,'slaughter_all').every(o=>o.date>='2025-07'));
for(const id of ['pork_annual','inventory_annual','outbound_annual','beef_annual','lamb_annual','poultry_annual','meat_annual','eggs_annual','income_annual','corn_annual','restaurant_annual','carcass_proxy'])assert.deepEqual(A.series(D,id).map(o=>o.date),Array.from({length:10},(_,i)=>(2016+i)+'-12'));
for(const c of D.catalog)assert.equal(c.expectedHistory,c.frequency==='年度'?10:c.frequency.startsWith('季度')?40:120);
assert.ok(A.series(D,'sows').every(o=>o.date>='2019-12'));
assert.equal(A.series(D,'hog').find(o=>o.date==='2016-01').value,17.62);
assert.equal(A.series(D,'ratio_mara').find(o=>o.date==='2017-01').value,9.59);
assert.equal(A.series(D,'pork_annual').find(o=>o.date==='2020-12').value,4113);
assert.deepEqual(A.series(D,'pigfeed_annual').map(o=>o.value),[13076.5,13597.5,14975.2,14391.3,16639.4]);
assert.deepEqual(A.series(D,'lh_daily_oi_annual').map(o=>o.date),['2021-12','2025-12']);
assert.equal(A.segments(A.series(D,'lh_daily_oi_annual'),12).length,2);
assert.equal(A.series(D,'population_annual').at(-1).value,140489);
assert.equal(A.series(D,'income_annual').at(-1).value,43377);
assert.equal(A.shift('2021-11',3),'2022-02');assert.equal(A.shift('2024-02',-12),'2023-02');
const idx=A.prepare(D,'hog','corn','history','index');assert.equal(idx.baseline,'2016-01');assert.equal(idx.a[0].plot,100);assert.equal(idx.b[0].plot,100);assert.equal(idx.pairs.length,67);
const lagged=A.prepare(D,'sows','hog','all','raw',10);for(const p of lagged.pairs){assert.equal(A.shift(p.sourceDate,10),p.date);assert.equal(p.y,A.series(D,'hog').find(o=>o.date===p.date).value);}
const yoy=A.prepare(D,'hog','corn','all','yoy');for(const r of yoy.a){const prev=A.series(D,'hog').find(o=>o.date===A.shift(r.date,-12));assert.ok(prev);assert.ok(Math.abs(r.plot-(r.value/prev.value-1)*100)<1e-10);}
assert.ok(A.prepare(D,'scale_profit','small_profit','history','index').error);
assert.ok(A.prepare(D,'corn_ppi','','history','yoy').error);
assert.equal(A.pearson(Array.from({length:11},(_,i)=>({x:i,y:i}))),null);
assert.equal(A.pearson(Array.from({length:12},(_,i)=>({x:i,y:2*i+3}))),1);
assert.equal(A.pearson(Array.from({length:12},(_,i)=>({x:i,y:-2*i}))),-1);
assert.equal(A.pearson(Array.from({length:12},(_,i)=>({x:1,y:i}))),null);
assert.equal(A.segments([{date:'2021-01'},{date:'2021-02'},{date:'2021-04'}]).length,2);
assert.deepEqual(A.future(10680,10,1,-500),{value:170880,margin:17088,leverage:10,pnl:-8000,tickValue:80});
assert.throws(()=>A.future(10680,10,.5,-500));assert.throws(()=>A.future(10681,10,1,-500));assert.throws(()=>A.future(10680,0,1,-500));
// Minimal DOM adapter validates initialization and shared interaction state.
// This is not a browser visual QA or supported WebMCP context.
class Element{constructor(tag,attrs){this.tagName=tag;this.attrs=attrs;this.id=attrs.id;this.dataset={};Object.entries(attrs).filter(([k])=>k.startsWith('data-')).forEach(([k,v])=>this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v);this.value=attrs.value||'';this.checked='checked'in attrs;this.hidden='hidden'in attrs;this.classes=new Set((attrs.class||'').split(/\s+/));this.classList={toggle:(c,on)=>on?this.classes.add(c):this.classes.delete(c)};this.events={};this.innerHTML='';this.textContent='';}setAttribute(k,v){this.attrs[k]=v;}removeAttribute(k){delete this.attrs[k];}addEventListener(k,fn){this.events[k]=fn;}}
const elements=[];for(const match of html.matchAll(/<([a-z][\w-]*)\b([^>]*)>/gi)){const attrs={};for(const m of match[2].matchAll(/([\w-]+)(?:="([^"]*)")?/g))attrs[m[1]]=m[2]??'';elements.push(new Element(match[1],attrs));}
const nodes=new Map(elements.filter(e=>e.id).map(e=>[e.id,e]));
for(const [id,n]of nodes)if(n.tagName==='select'){const body=html.match(new RegExp('<select id="'+id+'"[^>]*>([\\s\\S]*?)</select>'))?.[1];const o=body?.match(/<option(?: value="([^"]*)")?[^>]*>([^<]*)/);if(o)n.value=o[1]??o[2];}
const select=s=>elements.filter(e=>s.split(',').some(q=>q.startsWith('.')?e.classes.has(q.slice(1)):q.startsWith('[')?Object.hasOwn(e.attrs,q.slice(1,-1)):e.tagName===q));
const registered=new Map(),events={};const location={hash:''};
const document={getElementById:id=>nodes.get(id),querySelectorAll:select,querySelector:s=>select(s)[0],modelContext:{registerTool:(tool)=>{registered.set(tool.name,tool);}}};
const window={HOG_DATA:D,HogAnalytics:A,addEventListener:(k,fn)=>events[k]=fn,scrollTo:()=>{}};
const context=vm.createContext({window,document,location,history:{replaceState:(_,__,hash)=>location.hash=hash},URL,Blob,AbortController,console});
vm.runInContext(fs.readFileSync('dist/app.js','utf8'),context);
assert.match(nodes.get('kpis').innerHTML,/11.36/);assert.match(nodes.get('overview-chart').innerHTML,/<svg/);assert.match(nodes.get('heatmap').innerHTML,/2024-10/);assert.match(nodes.get('heatmap').innerHTML,/2016-01/);assert.match(nodes.get('heatmap').innerHTML,/2026-12/);assert.equal((nodes.get('heatmap').innerHTML.match(/data-date=/g)||[]).length,132);assert.match(nodes.get('future-result').innerHTML,/170,880/);assert.equal(registered.size,2);assert.match(nodes.get('pigfeed-bars').innerHTML,/16,639\.4/);assert.match(nodes.get('overview-coverage').textContent,/12项年度/);
for(const id of ['overview-period','trajectory-period','lab-period'])assert.equal(nodes.get(id).value,'all');
assert.match(nodes.get('hog-trend').innerHTML,/2026-08/);assert.match(nodes.get('overview-chart').innerHTML,/2026-08/);
elements.find(e=>e.dataset.pair==='hog,corn,index').onclick();assert.equal(nodes.get('lab-period').value,'all');
for(const id of ['sows-trend','hog-trend','pork-trend'])assert.match(nodes.get(id).innerHTML,/<svg/);
assert.equal((nodes.get('pork-trend').innerHTML.match(/class="chart-point"/g)||[]).length,10);
assert.equal((nodes.get('sows-trend').innerHTML.match(/class="chart-point"/g)||[]).length,A.series(D,'sows').length);
assert.equal((nodes.get('hog-trend').innerHTML.match(/class="chart-point"/g)||[]).length,A.series(D,'hog').length);
assert.match(nodes.get('pork-trend-note').textContent,/全年总量/);
nodes.get('sows-trend').onclick({target:{closest:()=>({dataset:{hit:'0'}})}});assert.match(nodes.get('sows-trend-detail').innerHTML,/https:/);
nodes.get('trajectory-period').value='2026';nodes.get('trajectory-period').onchange();assert.match(nodes.get('hog-trend').innerHTML,/<svg/);assert.match(nodes.get('pork-trend').innerHTML,/没有已收集观测/);
nodes.get('trajectory-period').value='2024';nodes.get('trajectory-period').onchange();assert.equal((nodes.get('pork-trend').innerHTML.match(/class="chart-point"/g)||[]).length,1);
nodes.get('trajectory-period').value='history';nodes.get('trajectory-period').onchange();
nodes.get('overview-period').value='2026';elements.find(e=>e.dataset.scope==='ratio_ndrc').onclick();assert.match(nodes.get('overview-chart').innerHTML,/没有已收集观测/);
nodes.get('catalog-group').value='期货';nodes.get('catalog-group').events.change();assert.match(nodes.get('catalog-result').textContent,/显示 6 项/);assert.ok(nodes.get('catalog').innerHTML.includes('data-inspect'));
nodes.get('catalog-group').value='';nodes.get('catalog-search').value='不存在xyz';nodes.get('catalog-search').events.input();assert.match(nodes.get('catalog').innerHTML,/没有匹配指标/);
nodes.get('table-year').value='2024';nodes.get('table-year').onchange();assert.match(nodes.get('table-count').textContent,/11 条/);assert.equal(nodes.get('next-page').disabled,true);
const tool=registered.get('configure_indicator_comparison');assert.equal(tool.annotations.readOnlyHint,false);assert.equal(tool.inputSchema.additionalProperties,false);
const configured=tool.execute({a:'sows',b:'hog',period:'all',mode:'raw',lag:10});assert.equal(configured.lag,10);assert.ok(configured.pairs>12);assert.equal(window.HogSite.readState().a,'sows');assert.equal(nodes.get('explore').hidden,false);
const before=JSON.stringify(window.HogSite.readState());assert.throws(()=>tool.execute({a:'made-up',lag:10}));assert.equal(JSON.stringify(window.HogSite.readState()),before);assert.throws(()=>tool.execute({a:'sows',unknown:true}));
const read=registered.get('read_indicator_observations');assert.equal(read.execute({metricIds:['pork_annual'],period:'history'})[0].observations.length,10);assert.equal(read.execute({metricIds:['hog'],period:'2016'})[0].observations[0].value,17.62);assert.equal(read.annotations.readOnlyHint,true);const result=read.execute({metricIds:['pork_annual','corn_annual'],period:'2025'});assert.equal(result[0].observations.length,1);assert.equal(result[0].observations[0].value,5938);assert.throws(()=>read.execute({metricIds:['bad']}));assert.equal(JSON.stringify(window.HogSite.readState()),before);
assert.equal(window.HogSite.downloadCsv(A.series(D,'ratio_mara').filter(o=>o.date.startsWith('2024'))).split('\r\n').length,12);
for(const m of html.matchAll(/(?:src|href)="([^"#]+)"/g)){if(!/^(https:|data:)/.test(m[1]))assert.ok(fs.existsSync('dist/'+m[1]),'Missing asset '+m[1]);}
assert.equal(new Set(elements.filter(e=>e.id).map(e=>e.id)).size,elements.filter(e=>e.id).length);
console.log(JSON.stringify({status:'passed',metrics:D.catalog.length,observations:D.observations.length,sources:D.sources.length,pairs:idx.pairs.length,lagPairs:lagged.pairs.length,checks:'Data integrity, exact calendar alignment, missing periods, annual coverage, correlation math, futures calculations, app initialization, filtering, pagination, CSV, and shared tool state',limitations:'Visual browser QA and a supported WebMCP browser context unavailable; DOM and registry checks use an adapter.'},null,2));
