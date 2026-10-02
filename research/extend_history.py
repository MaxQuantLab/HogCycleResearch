"""Add verified 2016–2020 observations without fabricating missing periods.

Run after supplement_data.py and before finalize_data.py. Idempotent: existing
newer observations are preserved. Raw source caches are ignored by git.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
x=json.loads((ROOT/'research/data-stage.json').read_text())
rows={(o['metric'],o['date']):o for o in x['observations']}
def add(id,date,value,url,method='原表',note='',yoy=None,mom=None):
 if (id,date) not in rows:
  rows[id,date]=dict(metric=id,date=date,value=float(value),url=url,method=method,note=note,yoy=yoy,mom=mom)

urls={2016:'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1899428.html',2017:'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1899855.html',2018:'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1900241.html',2019:'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1900640.html',2020:'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1901004.html'}
annual={
 'pork_annual':[5299,5340,5404,4255,4113],
 'inventory_annual':[43504,43325,42817,31041,40650],
 'outbound_annual':[68502,68861,69382,54419,52704],
 'beef_annual':[717,726,644,667,672],
 'lamb_annual':[459,468,475,488,492],
 'poultry_annual':[1888,1897,1994,2239,2361],
 'meat_annual':[8364,8431,8517,7649,7639],
 'eggs_annual':[3095,3070,3128,3309,3468],
 'income_annual':[23821,25974,28228,30733,32189],
 'corn_annual':[4391,4317.8,5146.6,5215,5213],
 'restaurant_annual':[35799,39644,42716,46721,39527],
}
for id,values in annual.items():
 for y,v in zip(range(2016,2021),values):
  u=urls[y]
  if id=='corn_annual' and y>=2019:u='https://www.stats.gov.cn/xxgk/jd/sjjd2020/'+('202001/t20200119_1764894.html' if y==2019 else '202012/t20201211_1808749.html')
  add(id,f'{y}-12',v,u,note='当年原始发布版本；2018年起农业普查修订可能改变历史基数，跨年按值计算的增速不等同官方可比同比。'+('原公报万吨×0.2换算亿斤。' if id=='corn_annual' and y<=2018 else ''))
  if id in ['inventory_annual','outbound_annual','pork_annual']:
   add({'inventory_annual':'inventory','outbound_annual':'outbound_ytd','pork_annual':'pork_ytd'}[id],f'{y}-12',v,u,note='四季度末存栏 / 1—12月累计；当年原始发布版本。')
for y in range(2016,2021):
 d=f'{y}-12';a=rows['pork_annual',d];b=rows['outbound_annual',d]
 add('carcass_proxy',d,round(a['value']/b['value']*1000,2),a['url'],'计算值','产量÷出栏×1000；不是活重；原始发布版本可能修订。')

# Original MoA monthly reports. Values are read from the national monthly
# narrative, never from regional sections or weekly chart tables.
pdfs=json.loads((ROOT/'research/history-pdf-urls.json').read_text())
monthly=[
 ('2016-05',16,[20.45,30.97,51.01,1.97,3.00,10.38]),
 ('2016-06',17,[20.41,31.29,52.39,2.03,3.06,10.06]),
 ('2017-01',15,[18.22,28.95,41.01,1.90,3.09,9.59]),
 ('2017-04',18,[16.00,26.59,42.97,1.85,3.00,8.63]),
 ('2017-11',19,[14.47,24.77,30.89,1.94,3.00,7.44]),
 ('2017-12',14,[15.07,25.11,30.50,1.95,3.02,7.74]),
 ('2018-02',0,[14.06,24.98,29.84,2.01,3.01,7.00]),
 ('2018-07',5,[12.02,20.40,24.27,None,2.99,5.93]),
 ('2019-01',21,[13.12,23.16,22.00,2.06,3.05,6.36]),
 ('2019-02',22,[12.55,22.55,23.04,2.05,3.03,6.13]),
 ('2020-04',20,[33.70,52.96,98.95,2.14,3.15,15.72]),
]
for d,i,values in monthly:
 for id,v in zip(['hog','pork','piglet','corn','feed','ratio_mara'],values):
  if v is not None:add(id,d,v,pdfs[i],note='农业农村部农产品供需形势分析月报；全国500个集贸市场月均值。')
u='https://sannong.cntv.cn/2016/02/29/ARTIlQShASw0r1HfjJ4RFviT160229.shtml'
for id,v in [('hog',17.62),('pork',27.66),('piglet',32.18),('corn',2.10),('meal',3.08),('feed',3.08),('egg',10.10),('beef',63.38),('lamb',57.66),('ratio_mara',8.39)]:add(id,'2016-01',v,u,'官方报告转载','央视三农转载农业部2016年1月价格监测报告，统计期不是转载日期。')
u='https://www.nahs.org.cn/jcyj/jghq/202011/t20201116_364925.htm'
for id,v in [('hog',31.40),('pork',49.91),('piglet',93.99),('corn',2.50),('meal',3.40),('feed',3.31),('egg',9.41),('beef',85.49),('lamb',81.35)]:add(id,'2020-10',v,u,note='原报告公布的2020年10月全国月均价格。')

# Extract exact previous-year / previous-month columns from national tables.
# Includes 2020 values reported in 2021 tables and 2019 in 2020 tables.
price_ids={'仔猪':'piglet','生猪':'hog','活猪':'hog','猪肉':'pork','玉米':'corn','豆粕':'meal','育肥猪配合饲料':'feed','牛肉':'beef','羊肉':'lamb','鸡蛋':'egg'}
files=list((ROOT/'research').glob('month-*.txt'))+list((ROOT/'research').glob('nahs-click-*.txt'))+list((ROOT/'research').glob('oldmonth-*.txt'))
for p in files:
 t=p.read_text();match=re.search(r'(202[01])年(\d{1,2})月全国畜产品',t);u=re.search(r'https?://[^)\s]+',t)
 if not match or not u:continue
 y,m=map(int,match.groups());d=f'{y}-{m:02d}';prev=f'{y-1}-12' if m==1 else f'{y}-{m-1:02d}'
 for label,id in price_ids.items():
  r=re.search(r'^L\d+: '+label+r'\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',t,re.M)
  if not r:continue
  for date,v,method,note in [(d,r[1],'原表','原报告月均价格。'),(f'{y-1}-{m:02d}',r[2],'原表同期值','原表去年同期栏；不是根据同比百分比反推。'),(prev,r[3],'原表上月值','原表上月栏；不是插值。')]:
   if date<'2021-01':add(id,date,v,u[0],method,note)
 r=re.search(r'本月猪粮比价为\s*([\d.]+)',t)
 if r and d<'2021-01':add('ratio_mara',d,r[1],u[0],note='原报告公布的月度猪粮比。')
for d in sorted({date for id,date in rows if id=='hog' and date<'2021-01'}):
 if ('corn',d) in rows and ('ratio_mara',d) not in rows:
  a,b=rows['hog',d],rows['corn',d]
  add('ratio_mara',d,round(a['value']/b['value'],2),a['url'],'计算值','同统计期全国集贸生猪月均价÷玉米月均价；四舍五入可能不同于原公布比值。玉米来源：'+b['url'])

# Keep the head-count series separate from the old 400-county growth rates.
u='https://www.stats.gov.cn/xxgk/jd/sjjd2020/202004/t20200420_1764929.html'
add('sows','2020-03',3381,u,note='一季度末国家统计局调查值。')
add('sows','2019-12',3080,u,'计算值','2020一季度末3381万头减去原文公布的较上年末增加301万头。')
add('sows_annual','2019-12',3080,u,'计算值','3381−301；来自次年一季度官方报告的年末基数，早期旧监测推算值不拼接。')
add('sows','2020-06',3629,'https://jhs.moa.gov.cn/gzdt/202007/t20200724_6349325.htm',note='二季度末全国能繁母猪存栏，农业农村部原文。')
add('sows','2020-09',3822,'https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202010/t20201019_1794686.html',note='三季度末国家统计局调查值。')
u='https://nyncj.changde.gov.cn/zhdt/gsnnydt/content_810110'
for id in ['sows','sows_annual']:add(id,'2020-12',4161,u,'官方报告转载','政府农业农村部门转载，明确引用国家统计局年末值；不使用文中其他旧监测基数。')

x['history']=['2016-01','2025-12'];x['observations']=sorted(rows.values(),key=lambda o:(o['metric'],o['date']))
(ROOT/'research/data-stage.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
print(json.dumps({'oldObservations':sum(o['date']<'2021-01' for o in rows.values()),'oldHogMonths':sum(o['metric']=='hog' and o['date']<'2021-01' for o in rows.values())},ensure_ascii=False))
