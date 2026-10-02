import json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
x=json.loads((ROOT/'research/data-stage.json').read_text())
x['observations']=sorted([o for o in x['observations'] if o['date']>='2016-01'],key=lambda o:(o['metric'],o['date']))
for o in x['observations']:
 if o['method']=='环比反推':o['note']='根据后一期月报公布的猪粮比及较上月变化点数反推前期值；原文四舍五入会影响精度。'
 elif o['note']=='Published monthly observation':o['note']='原报告公布的月度猪粮比。'
gaps=[
 ('供给','PSY / MSY / 窝均健仔数','有效产能≈母猪数量×繁殖效率；效率改善可抵消母猪减少。','母猪场生产记录；样本覆盖、品种与时间口径必须一致。','约9—11个月'),
 ('供给','仔猪出生量与仔猪存栏','比母猪头数更接近未来肥猪供给。','全国可比月度出生量、断奶量与成活率。','约5—6个月'),
 ('供给','出栏活重与大猪占比','压栏增重可以让出栏头数下降、肉量仍增加。','育肥猪实测活重、不同体重出栏占比；全国连续样本不足。','当期至数月'),
 ('供给','二次育肥与压栏','先减少当期上市，再增加后期供给；不能视作永久去产能。','二育买入、退出、库存与样本方法。','数周至数月'),
 ('供给','上市养殖企业出栏与资本开支','扩产与集中度提升会改变供给弹性；企业样本不是全国总量。','交易所公告与公司月报，剔除种猪仔猪口径差异。','当期及约1年以上'),
 ('供给','屠宰开工率与白条走货','观察需求承接力度；开工率也受有效产能分母变化影响。','同样本屠宰厂实际开工、订单和销量。','当期'),
 ('成本','月度猪饲料产量','观察养殖活动与饲料需求；自产料和配方变化影响解释。','2021—2025年度值已收集；还需2016—2020年度及连续月度、同口径分类产量。','当期至数月'),
 ('成本','料肉比与全程成活率','直接改变每公斤增重成本和每头可售成本。','同规模、同育肥阶段样本的饲料转化率及成活率。','一个育肥周期'),
 ('成本','玉米地头价与湿粮折价','农户收入还受含水率、品质、烘干与本地收购影响。','地区、标准水分、质量等级、到厂/地头口径分开。','新粮上市季及当期'),
 ('成本','仔猪每头购入价与自繁成本','外购育肥与自繁自养的盈亏线不同。','固定体重仔猪每头价，不用元/公斤价格直接代替。','约5—6个月'),
 ('成本','人工 / 能源 / 运费 / 防疫 / 利息','会移动成本线，也决定持续亏损时的退出速度。','养殖场全成本调查及区域运价、融资成本。','当期及后续产能'),
 ('库存','冻品库存与鲜冻价差','入库吸收现货，出库增加供应；库存数据可能比猪粮比更接近短期压力。','全国或同样本库存吨数、库容分母及库存年龄。','当期至数月'),
 ('库存','储备采购实际成交与投放量','计划量不等于成交量；方向、时间和规模共同决定影响。','储备招标、成交、投放公告的逐笔核验。','当期至数月'),
 ('需求','居民年龄结构与肉类偏好','决定长期消费结构；总量与人均量应分开观察。','人口总量与居民收入年度值已收集；年龄结构和偏好变化仍缺可比序列。','年度结构变化'),
 ('需求','节假日 / 腌腊 / 学校开学','影响消费季节性与备货，但不改变长期产能。','日历与地区消费行为；事件变量不做伪连续数值。','数周至季度'),
 ('需求','猪肉实际消费总量与终端订单','家庭记账和餐饮收入都无法独立代表全部猪肉消费。','包含外食的肉类量、商超销售、团餐和订单量。','当期'),
 ('贸易','人民币汇率 / 海外猪价 / 关税','改变进口到岸成本与进口利润。','同产品、同贸易条款的到岸价、税率与汇率。','进口订单至到港'),
 ('贸易','进口在途与替代肉进口','订单、到港与当期海关进口存在时差。','在途量、冻品报盘、牛禽肉进口量。','约1—3个月'),
 ('政策','环保 / 用地 / 信贷 / 保险 / 扩产约束','改变进入和退出成本，地区执行强度可能不同。','政策发布时间、实施地区与实际执行；逐事件记录。','数月至数年'),
 ('冲击','非洲猪瘟及其他疫病','短期淘汰增加上市、随后有效产能可能下降；隐性损失难统计。','官方疫情事件、淘汰规模、成活率；不能把报告数当实际流行率。','当期及后续周期'),
 ('冲击','高温 / 洪水 / 寒潮 / 运输限制','改变采食、增重、成活、运力及消费。','主产区气象、灾情和交通事件，按地理权重合成。','当期至数月'),
 ('期货','LH各合约结算价 / 成交 / 持仓','预期、流动性与仓位共同影响期货价格。','已有2021、2025部分年度流动性数据；2021年上市后仍缺连续逐合约日行情，上市前没有LH交易数据。','每日'),
 ('期货','基差 / 跨期价差 / 季节性','需同交割地区现货、同日期、同品质；主力切换可能制造跳变。','地区现货与指定合约配对，保留换月规则。','对应交割月份'),
 ('期货','仓单 / 交割 / 保证金与限仓变化','影响可交割供应、资金压力和价格波动。','大商所规则与公告按生效日期整理。','临近交割与政策生效时'),
]
x['gaps']=[dict(group=g,name=n,effect=e,required=r,lag=l,status='未取得可比十年序列') for g,n,e,r,l in gaps]
x['sources']=[{'url':u,'records':sum(o['url']==u for o in x['observations']),'first':min(o['date'] for o in x['observations'] if o['url']==u),'last':max(o['date'] for o in x['observations'] if o['url']==u)} for u in sorted(set(o['url'] for o in x['observations']))]
for c in x['catalog']:
 rows=[o for o in x['observations'] if o['metric']==c['id']]
 c['count']=len(rows);c['historyCount']=sum('2016-01'<=o['date']<='2025-12' for o in rows);c['latest']=rows[-1] if rows else None
 c['expectedHistory']=10 if c['frequency']=='年度' else (40 if c['frequency'].startswith('季度') else 120)
 c['coverageNote']='2025年7月结束原范围，后续单列全部定点企业。' if c['id']=='slaughter' else ('2025年7月启用新统计范围，本版已取得4个历史月份。' if c['id']=='slaughter_all' else ('截至2025年8月；后续联合月报未继续列出，不能当作当前成本。' if c['id'].startswith(('small_','scale_')) or c['id']=='ratio_ndrc' else '缺失期不填充，原表同期值与上月值保留提取方式。'))
for c in x['catalog']:
 if c['id'].startswith('lh_'):c['coverageNote']='仅有部分年度，缺失年份不连线、不补值；全品种年度流动性不代表指定合约实时行情。'
 elif c['frequency']=='年度':c['coverageNote']=f"2016—2025已收集{c['historyCount']}/10期；年度落点为12月，不代表发布日期。缺失年度不补值，原始发布版本可能修订。"
 if c['id'] in ['sows','sows_annual']:c['coverageNote']+=' 2016—2018未取得与现行头数口径可比的存栏值；旧400县监测主要公布增减幅，2018年样本调整，不拼接为头数。'
 if c['id'].startswith('lh_'):c['coverageNote']+=' 生猪期货2021年上市，2016—2020无LH交易数据。'
assert len(set((o['metric'],o['date']) for o in x['observations']))==len(x['observations'])
assert all(o['url'].startswith('https://') and 0<len(o['date'])==7 for o in x['observations'])
assert all(o['date']<='2026-08' for o in x['observations'])
(ROOT/'dist/data.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
(ROOT/'dist/data.js').write_text('window.HOG_DATA = '+json.dumps(x,ensure_ascii=False,separators=(',',':'))+';\n')
cats={c['id']:c for c in x['catalog']}
with (ROOT/'dist/observations.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['指标代码','指标名称','分类','统计期','值','单位','频率','提取方式','备注','原表同比','原表环比','来源链接'])
 for o in x['observations']:
  c=cats[o['metric']];w.writerow([o['metric'],c['name'],c['group'],o['date'],o['value'],c['unit'],c['frequency'],o['method'],o['note'],o['yoy'],o['mom'],o['url']])
with (ROOT/'dist/indicator-catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['指标代码','指标名称','分类','单位','频率','定义','影响机制','通常时滞','发布单位','历史观测数','覆盖说明'])
 for c in x['catalog']:w.writerow([c['id'],c['name'],c['group'],c['unit'],c['frequency'],c['definition'],c['effect'],c['lag'],c['agency'],c['historyCount'],c['coverageNote']])
 for g in x['gaps']:w.writerow(['',g['name'],g['group'],'','待核验',g['required'],g['effect'],g['lag'],'',0,g['status']])
print(json.dumps({'observations':len(x['observations']),'metrics':len(x['catalog']),'gaps':len(x['gaps']),'sources':len(x['sources']),'annualComplete':sum(c['frequency']=='年度' and c['historyCount']==10 for c in x['catalog'])},ensure_ascii=False))
