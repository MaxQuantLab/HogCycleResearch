import json,re,calendar,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
catalog=[]; observations={}; conflicts=[]
def metric(id,name,group,unit,freq,definition,effect,lag,agency):
 catalog.append(dict(id=id,name=name,group=group,unit=unit,frequency=freq,definition=definition,effect=effect,lag=lag,agency=agency))
def add(id,date,value,url,method='原表',note='',yoy=None,mom=None,priority=1):
 if value is None:return
 key=(id,date); rec=dict(metric=id,date=date,value=float(value),url=url,method=method,note=note,yoy=yoy,mom=mom,_priority=priority)
 if key in observations:
  old=observations[key]
  if old['value']!=rec['value']: conflicts.append(dict(metric=id,date=date,old=old['value'],new=rec['value'],oldSource=old['url'],newSource=url))
  if old['_priority']>=priority:return
 observations[key]=rec
def m(id,name,group='价格',unit='元/公斤',freq='月度',definition='',effect='',lag='当期',agency='农业农村部 / 全国畜牧总站'):
 metric(id,name,group,unit,freq,definition,effect,lag,agency)
m('hog','生猪集贸价格',definition='全国500个县集贸市场与采集点月均价格。不是期货交割地区现货价。',effect='现货价格基准；与出场价分开比较。')
m('pork','猪肉集贸零售价格',definition='全国500个县县乡集贸市场猪肉平均价格。',effect='消费端价格；传导通常慢于生猪价格。')
m('piglet','仔猪价格',definition='全国500个县集贸市场仔猪平均价格，元/公斤；并非固定15公斤仔猪每头报价。',effect='反映补栏意愿，也影响外购仔猪育肥成本。',lag='约5—6个月')
for id,name in [('corn','玉米集贸价格'),('meal','豆粕集贸价格'),('feed','育肥猪配合饲料价格')]:
 m(id,name,'成本',definition='全国500个县集贸市场监测价格；玉米含流通环节，不能直接当作农户地头收购价。',effect='成本下降可缓解亏损，也可能延缓退出。',lag='当期及后续育肥周期')
for id,name in [('chicken','鸡肉集贸价格'),('beef','牛肉集贸价格'),('lamb','羊肉集贸价格'),('egg','鸡蛋集贸价格')]:m(id,name,'需求',definition='全国集贸市场月均价；用于观察替代食品价格，不代表实际猪肉消费量。',effect='相对价格改变消费者选择，影响方向取决于替代关系。')
m('ratio_mara','猪粮比 · 集贸口径','成本','倍',definition='生猪集贸均价 ÷ 玉米集贸均价，优先采用月报公布值。',effect='衡量相对价格与养殖压力，不能单独判断估值或买点。')
m('hog_farm','生猪出场价格 · 发改委',definition='发改委价格监测中心全国代表性养殖场出场价格。',effect='用于发改委猪粮比，不能与集贸玉米混算。',agency='国家发展改革委')
m('gilt','二元母猪销售价格',definition='发改委全国二元母猪销售价格，元/公斤。',effect='补栏与扩产意愿的价格信号。',lag='约10个月及以上',agency='国家发展改革委')
for id,name,definition,agency in [('white','白条猪批发价 · 全国','全国200个重点农产品批发市场白条猪价格。','农业农村部'),('city_white','白条猪批发价 · 36城','36个大中城市批发市场白条猪平均价格。','商务部'),('lean','精瘦肉零售价 · 36城','36个大中城市精瘦肉平均零售价格。','国家发展改革委'),('leg','后腿肉零售价 · 36城','36个大中城市后腿肉零售价格；历史品种标准有调整。','商务部')]:m(id,name,definition=definition,effect='观察从养殖到消费端的价格传导；不同部位不可直接拼接。',agency=agency)
m('ratio_ndrc','猪粮比 · 发改委','成本','倍',definition='全国生猪出场价 ÷ 全国玉米批发价。与集贸口径独立展示。',effect='政策监测指标；预警不等于立刻反转。',agency='国家发展改革委')
m('sows','能繁母猪存栏','供给','万头',definition='季度末为国家统计局调查值；其余月份为农业农村部定点监测推算值。',effect='未来供给的领先指标，必须结合繁殖效率。',lag='通常约9—11个月',agency='国家统计局 / 农业农村部')
m('inventory','生猪存栏','供给','万头','季度',definition='季度末生猪存栏，包含各年龄段。',effect='供给蓄水池；不能全部理解为近期可出栏猪。',lag='分年龄约0—6个月',agency='国家统计局')
m('outbound_ytd','累计生猪出栏','供给','万头','季度累计',definition='年初至季度末累计出栏，不能跨年连续相加。',effect='已兑现供应量。',agency='国家统计局')
m('pork_ytd','累计猪肉产量','供给','万吨','季度累计',definition='年初至季度末累计猪肉产量，不能与全年值直接同比。',effect='比单看出栏头数更接近肉的实际供应。',agency='国家统计局')
for id,name,scope in [('slaughter','规模以上定点屠宰量','年屠宰量2万头以上企业'),('slaughter_all','全部定点屠宰量','全部生猪定点屠宰企业')]:
 m(id,name,'供给','万头',definition=scope+'。2025年7月发生统计范围变化，两个序列不拼接。',effect='屠宰端供应兑现，亦受需求和行业集中度影响。',agency='农业农村部')
for id,scope in [('small','散养'),('scale','规模养殖')]:
 for suffix,label in [('cost','每头成本'),('profit','每头净利润'),('revenue','每头产值')]:m(id+'_'+suffix,scope+label,'成本','元/头',definition='发改委成本收益调查口径，成本含现金、实物、劳动力、土地等全部要素；净利润采用原表四舍五入值。',effect='利润影响扩产、补栏、退出；不等于某一家企业的现金成本。',lag='当期利润 → 后续产能',agency='国家发展改革委')
for id,name in [('imports','进口猪肉量'),('offal_imports','进口猪杂碎量'),('exports','出口猪肉量'),('offal_exports','出口猪杂碎量')]:m(id,name,'贸易','万吨',definition='海关统计，猪肉与猪杂碎分开列示；累计值不混入月度序列。',effect='改变国内可用供应；杂碎不是猪肉替代的等量口径。',agency='海关总署')
patterns=[('sows','能繁[殖]?母猪存栏'),('inventory','生猪存栏'),('outbound_ytd','生猪出栏'),('pork_ytd','猪肉产量'),('slaughter','规模以上生猪定点屠宰企业屠宰量'),('slaughter_all','生猪定点屠宰企业屠宰量'),('gilt','全国二元母猪销售价格'),('piglet','全国仔猪价格'),('hog_farm','全国生猪出场价格'),('city_white','36个大中城市批发市场白条猪价格'),('white','全国批发市场白条猪价格'),('lean','精瘦肉'),('leg','后腿肉'),('pork','县乡集贸市场猪肉零售价格'),('ratio_ndrc','猪粮比价'),('small_revenue','散养生猪每头产值'),('small_cost','散养生猪每头成本'),('small_profit','散养生猪每头净利润'),('scale_revenue','规模养殖生猪每头产值'),('scale_cost','规模养殖生猪每头成本'),('scale_profit','规模养殖生猪每头净利润'),('offal_imports','进口猪杂碎'),('offal_exports','出口猪杂碎'),('imports','进口猪肉'),('exports','出口猪肉')]
for p in sorted((ROOT/'research').glob('product-*.txt'))+sorted((ROOT/'research').glob('supplement-*.txt')):
 text=p.read_text(); url=re.search(r'https?://[^)\s]+',text)
 if not url:continue
 for line in text.splitlines():
  mt=re.match(r'^L\d+: (?:(?:生产|价格|消费|进出口|成本收益)\s*\|\s*)?\d+\s*\|\s*([^|]+?)\s*\|\s*(-?[\d.]+)(.*)',line)
  if not mt:continue
  label,v,tail=mt.groups(); ym=re.search(r'(202[1-6])年(\d{1,2})月',label)
  if '累计' in label or re.search(r'年1[-—]',label):continue
  q=re.search(r'(202[1-6])年(?:前)?([1234一二三四])季度',label)
  if ym:date=ym[1]+'-'+ym[2].zfill(2)
  elif '上半年' in label:date=re.search(r'(202[1-6])年',label)[1]+'-06'
  elif '前三季度' in label:date=re.search(r'(202[1-6])年',label)[1]+'-09'
  elif q: date=q[1]+'-'+str(int(q[2]) *3 if q[2].isdigit() else ('一二三四'.index(q[2])+1)*3).zfill(2)
  elif re.search(r'(202[1-6])年',label):date=re.search(r'(202[1-6])年',label)[1]+'-12'
  else:continue
  for id,pat in patterns:
   if re.search(pat,label):
    vals=[x.strip() for x in tail.split('|')][1:]
    mom=vals[0] if len(vals)>0 else None; yoy=vals[1] if len(vals)>1 else None
    method='官方表转载' if p.name.startswith('supplement') else '原表'
    add(id,date,v,url[0],method=method,note=('非季末定点监测推算；'+label if id=='sows' and date[-2:] not in ['03','06','09','12'] else label),mom=mom,yoy=yoy,priority=3);break
price_ids={'仔猪':'piglet','生猪':'hog','猪肉':'pork','玉米':'corn','豆粕':'meal','育肥猪配合饲料':'feed','鸡肉':'chicken','牛肉':'beef','羊肉':'lamb','鸡蛋':'egg'}
for p in sorted((ROOT/'research').glob('month-*.txt'))+sorted((ROOT/'research').glob('nahs-click-*.txt')):
 text=p.read_text(); title=re.search(r'(202[1-6])年(\d{1,2})月全国畜产品',text); u=re.search(r'https?://[^)\s]+',text)
 if not title or not u:continue
 date=title[1]+'-'+title[2].zfill(2); year=int(title[1]); url=u[0]
 for label,id in price_ids.items():
  row=re.search(r'^L\d+: '+label+r'\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',text,re.M)
  if row:
   add(id,date,row[1],url,priority=4)
   if year>=2022:add(id,str(year-1)+'-'+title[2].zfill(2),row[2],url,'原表同期值','来自原表“去年同期”栏，不是反推或插值',priority=2)
   prev=(f'{year-1}-12' if title[2]=='1' else f'{year}-{int(title[2])-1:02d}')
   add(id,prev,row[3],url,'原表上月值','来自原表“上月”栏',priority=2)
  else:
   pats=[r'全国'+('(?:生猪|活猪)' if id=='hog' else label)+r'平均价格(?:为)?\s*([\d.]+)元',r'全国'+label+r'价格(?:为)?\s*([\d.]+)元']
   if id=='feed':pats.append(r'全国育肥猪配合饲料、肉鸡配合饲料和蛋鸡配合饲料价格分别为\s*([\d.]+)元')
   for pat in pats:
    val=re.search(pat,text)
    if val:add(id,date,val[1],url,priority=4);break
 ratio=re.search(r'本月猪粮比价为\s*([\d.]+)',text)
 if ratio:add('ratio_mara',date,ratio[1],url,priority=4)
for r in json.loads((ROOT/'research/ratio-existing.json').read_text()):
 if r['ratio'] is not None:add('ratio_mara',r['date'],r['ratio'],r['url'],'环比反推' if r['method']=='Reconstructed' else '原表',r['note'],priority=1)
# 完整年度数据独立存储，不把季度累计量当作单季度量。
annual_values={
 'sows_annual':('年末能繁母猪','供给','万头',[4329,4390,4142,4078,3961]),
 'inventory_annual':('年末生猪存栏','供给','万头',[44922,45256,43422,42743,42967]),
 'outbound_annual':('全年生猪出栏','供给','万头',[67128,69995,72662,70256,71973]),
 'pork_annual':('全年猪肉产量','供给','万吨',[5296,5541,5794,5706,5938]),
 'poultry_annual':('全年禽肉产量','需求','万吨',[2380,2443,2563,2660,2837]),
 'beef_annual':('全年牛肉产量','需求','万吨',[698,718,753,779,801]),
 'lamb_annual':('全年羊肉产量','需求','万吨',[514,525,531,518,496]),
 'meat_annual':('全年猪牛羊禽肉产量','供给','万吨',[8887,9227,9641,9663,10072]),
 'eggs_annual':('全年禽蛋产量','需求','万吨',[3409,3456,3563,3588,3498]),
 'corn_annual':('全年玉米产量','成本','亿斤',[5451,5544,5776.8,5898.3,6024.7]),
 'soy_annual':('全年大豆产量','成本','亿斤',[328,406,416.8,413.0,418.1]),
 'hog_ppi':('生猪生产者价格同比','价格','%',[ -35.1,-9.8,-14.0,9.0,-11.2]),
 'corn_ppi':('玉米生产者价格同比','成本','%',[25.5,2.7,1.6,-14.1,-3.8]),
}
for id,(name,group,unit,values) in annual_values.items():
 m(id,name,group,unit,'年度',definition='国家统计局当年年度农业生产报告公布值；保留各年原始发布版本。年度值标在12月，不是12月单月值。',effect='供需与生产成本的年度结构指标，不能代替短期交易信号。',agency='国家统计局')
 for y,v in enumerate(values,2021):
  txt=(ROOT/f'research/annual-{y}.txt').read_text();url=re.search(r'https?://[^)\s]+',txt)[0]
  add(id,f'{y}-12',v,url,note='年度值；历年原始发布版本可能存在后续修订。',priority=5)
m('consumption_annual','家庭人均猪肉消费量','需求','公斤/人/年','年度',definition='居民家庭调查记账口径，不等于包含全部外食、损耗及库存变动的全国猪肉总消费。',effect='观察家庭购买结构；不能据此单独推断总需求。',agency='国家统计局')
for id in ['imports','offal_imports','exports','offal_exports']:
 base=next(c for c in catalog if c['id']==id)
 m(id+'_annual',base['name'].replace('量','')+' · 全年','贸易','万吨','年度',definition='海关1—12月累计量，年度原始发布版本。',effect=base['effect'],agency='海关总署')
for y in range(2021,2026):
 p=ROOT/f'research/product-{y}-12.txt'
 if y==2025:p=ROOT/'research/supplement-2025-12.txt'
 tx=p.read_text();url=re.search(r'https?://[^)\s]+',tx)[0]
 v=re.search(r'居民家庭人均猪肉消费量[^|]+\|\s*([\d.]+)',tx)
 if v:add('consumption_annual',f'{y}-12',v[1],url,'官方表转载' if y==2025 else '原表',priority=5)
 for id,pat in [('imports','进口猪肉'),('offal_imports','进口猪杂碎'),('exports','出口猪肉'),('offal_exports','出口猪杂碎')]:
  v=re.search(r'1-12月累计'+pat+r'[^|]+\|\s*([\d.]+)',tx)
  if v:add(id+'_annual',f'{y}-12',v[1],url,'官方表转载' if y==2025 else '原表',priority=5)
# 2026年上半年官方数据。同比使用原报告，避免修订版本不一致。
u='https://www.stats.gov.cn/sj/sjjd/202607/t20260716_1964140.html'
for id,v,yoy in [('sows',3780,'-6.5%'),('inventory',42491,'0.1%'),('outbound_ytd',37246,'1.7%'),('pork_ytd',3119,'3.3%')]:add(id,'2026-06',v,u,note='2026年上半年；存栏为二季度末值，出栏及产量为1—6月累计。',yoy=yoy,priority=5)
m('carcass_proxy','平均每头猪肉产出 · 推算','供给','公斤/头','年度',definition='全年猪肉产量÷全年生猪出栏×1000。属于总量比值代理，非全国实测出栏活重；不用于推算育肥天数。',effect='揭示头数与肉量可能分化；也受统计范围和结构变化影响。',agency='根据国家统计局数据计算')
m('availability_annual','库存调整前猪肉可供量','供给','万吨','年度',definition='全年猪肉产量+全年进口猪肉-全年出口猪肉。不包含冻品库存变化，不等于实际消费量。',effect='观察总供给及进口边际影响，库存会改变当期可用量。',agency='根据国家统计局 / 海关数据计算')
for y in range(2021,2026):
 d=f'{y}-12';a=observations[('pork_annual',d)];b=observations[('outbound_annual',d)]
 add('carcass_proxy',d,round(a['value']/b['value']*1000,2),a['url'],'计算值','产量÷出栏×1000；不是活重。',priority=5)
 if ('imports_annual',d) in observations and ('exports_annual',d) in observations:
  v=a['value']+observations[('imports_annual',d)]['value']-observations[('exports_annual',d)]['value']
  add('availability_annual',d,round(v,2),a['url'],'计算值','来源还包括对应年份进口、出口指标所链接的海关联合发布表。',priority=5)
m('restaurant_annual','全年餐饮收入','需求','亿元','年度',definition='全国餐饮服务名义收入，包含价格和服务结构变化；不是猪肉消费量。',effect='反映外食活动变化，不能把收入增长等同肉类消费量增长。',agency='国家统计局')
restaurant_urls=['https://app.www.gov.cn/govdata/gov/202201/17/480817/article.html','https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202301/t20230117_1892127.html','https://www.stats.gov.cn/sj/zxfb/202402/t20240228_1947915.html','https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202501/t20250117_1958327.html','https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202601/t20260119_1962323.html']
for y,v,url in zip(range(2021,2026),[46895,43941,52890,55718,57982],restaurant_urls):add('restaurant_annual',f'{y}-12',v,url,note='全年名义收入；统计调查范围及基期可能修订。',priority=5)
# 原始日期、来源与口径均随数据保留；不填充不可获得的观测。
for c in catalog:
 rows=sorted([r for (id,d),r in observations.items() if id==c['id']],key=lambda r:r['date'])
 c['count']=len(rows); c['historyCount']=sum('2021-01'<=r['date']<='2025-12' for r in rows)
 c['latest']=rows[-1] if rows else None
 for r in rows:r.pop('_priority',None)
out={'asOf':'2026-10-02','history':['2021-01','2025-12'],'catalog':catalog,'observations':list(observations.values()),'conflicts':conflicts}
(ROOT/'research/data-stage.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('观察值',len(observations),'指标',len(catalog))
for c in catalog:print(c['id'],c['count'],c['historyCount'],c['latest']['date'] if c['latest'] else '-')
