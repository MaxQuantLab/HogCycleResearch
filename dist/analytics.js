(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.HogAnalytics=api;})(typeof window!=='undefined'?window:globalThis,function(){
 'use strict';
 const monthNumber=d=>{const [y,m]=d.split('-').map(Number);return y*12+m-1;};
 const monthString=n=>Math.floor(n/12)+'-'+String(n%12+1).padStart(2,'0');
 const shift=(d,n)=>monthString(monthNumber(d)+n);
 const inPeriod=(d,p)=>p==='all'?d>='2016-01'&&d<='2026-08':p==='history'?d>='2016-01'&&d<='2025-12':d.startsWith(p+'-');
 const series=(data,id,original=false)=>data.observations.filter(o=>o.metric===id&&(!original||!['环比反推','计算值'].includes(o.method))).sort((a,b)=>a.date.localeCompare(b.date));
 function transformed(rows,mode){if(mode!=='yoy')return rows.map(r=>({...r,plot:r.value}));const map=new Map(rows.map(r=>[r.date,r]));return rows.flatMap(r=>{const prev=map.get(shift(r.date,-12));return prev&&prev.value>0?[{...r,plot:(r.value/prev.value-1)*100,previous:prev.value}]:[];});}
 function prepare(data,a,b,period='history',mode='index',lag=0,original=false){
  const ca=data.catalog.find(c=>c.id===a),cb=data.catalog.find(c=>c.id===b);if(!ca||b&&!cb)throw Error('未知指标');if(!Number.isInteger(lag)||lag<0||lag>12)throw Error('时滞必须为0—12个月整数');if(!['raw','index','yoy'].includes(mode))throw Error('未知展示方式');
  if(mode==='yoy'&&(ca.id.endsWith('_ppi')||cb?.id.endsWith('_ppi')))return {error:'生产者价格同比本身已是百分比变化，请改用原值；不对同比再次计算同比。',a:[],b:[],pairs:[],ca,cb};
  let ar=transformed(series(data,a,original),mode).map(r=>({...r,sourceDate:r.date,date:shift(r.date,lag)})).filter(r=>inPeriod(r.date,period));
  let br=b?transformed(series(data,b,original),mode).filter(r=>inPeriod(r.date,period)).map(r=>({...r,sourceDate:r.date})):[];let baseline=null;
  if(mode==='index'){const bm=new Map(br.map(r=>[r.date,r]));baseline=b?ar.find(r=>bm.has(r.date))?.date:ar[0]?.date;if(!baseline)return {error:'窗口内没有共同统计期，请改选指标、窗口或原值模式。',a:[],b:[],pairs:[],ca,cb};const av=ar.find(r=>r.date===baseline).plot,bv=b?bm.get(baseline).plot:null;if(av<=0||b&&bv<=0||[...ar,...br].some(r=>r.plot<=0))return {error:'序列包含零值或负值，基期指数容易产生误读。请使用原值模式比较成本收益。',a:[],b:[],pairs:[],ca,cb};ar=ar.filter(r=>r.date>=baseline).map(r=>({...r,plot:r.plot/av*100}));br=br.filter(r=>r.date>=baseline).map(r=>({...r,plot:r.plot/bv*100}));}
  const bm=new Map(br.map(r=>[r.date,r]));const pairs=ar.filter(r=>bm.has(r.date)).map(r=>({date:r.date,x:r.plot,y:bm.get(r.date).plot,sourceDate:r.sourceDate}));return {a:ar,b:br,pairs,baseline,ca,cb};
 }
 function pearson(pairs){if(pairs.length<12)return null;const n=pairs.length,mx=pairs.reduce((s,p)=>s+p.x,0)/n,my=pairs.reduce((s,p)=>s+p.y,0)/n;let c=0,vx=0,vy=0;for(const p of pairs){c+=(p.x-mx)*(p.y-my);vx+=(p.x-mx)**2;vy+=(p.y-my)**2;}return vx&&vy?Math.max(-1,Math.min(1,c/Math.sqrt(vx*vy))):null;}
 function segments(rows,maxGap=1){const groups=[];for(const r of rows){const group=groups[groups.length-1];if(!group||monthNumber(r.date)-monthNumber(group[group.length-1].date)>maxGap)groups.push([r]);else group.push(r);}return groups;}
 function future(price,rate,lots,change){if(!Number.isFinite(price)||price<=0||price%5!==0)throw Error('价格须为正数且为5元/吨的整数倍');if(!Number.isFinite(rate)||rate<1||rate>100)throw Error('保证金率须在1%—100%之间');if(!Number.isInteger(lots)||lots<1||lots>10000)throw Error('手数须为1—10000的整数');if(!Number.isFinite(change)||change%5!==0||price+change<0)throw Error('价格变动须为5元/吨的整数倍，变动后价格不能为负');const value=price*16*lots;return {value,margin:value*rate/100,leverage:100/rate,pnl:change*16*lots,tickValue:5*16*lots};}
 return {monthNumber,monthString,shift,inPeriod,series,transformed,prepare,pearson,segments,future};
});
