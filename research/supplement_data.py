"""Append verified annual observations; idempotent and reproducible from numeric facts."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
x=json.loads((root/'research/data-stage.json').read_text())
feed_urls=[
 'https://www.nahs.org.cn/dt/xwlb/202202/t20220211_397140.htm',
 'https://www.chinafeed.org.cn/hyfx/hyfx_erji/202302/t20230214_418333.htm',
 'https://www.chinafeed.org.cn/hyfx/cyhg/202606/t20260617_472824.htm',
 'https://www.chinafeed.org.cn/hyfx/cyhg/202606/t20260617_472819.htm',
 'https://www.chinafeed.org.cn/hyfx/202602/t20260209_469703.htm']
population_urls=[
 'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1901393.html',
 'https://www.ndrc.gov.cn/fgsj/tjsj/jjsjgl1/202301/t20230131_1348088.html',
 'https://app.www.gov.cn/govdata/gov/202403/01/512478/article.html',
 'https://www.stats.gov.cn/sj/zxfb/202502/t20250228_1958817.html',
 'https://www.stats.gov.cn/sj/zxfbhjd/202602/t20260228_1962662.html']
income_urls=[population_urls[0],
 'https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1901715.html',
 'https://www.stats.gov.cn/sj/zxfb/202401/t20240116_1946622.html',population_urls[3],
 'https://www.stats.gov.cn/sj/zxfb/202601/t20260119_1962321.html']
future_url='https://www.investor.org.cn/zczx/qwzx/qhjysfb_1/202601/t20260112_885032.shtml'
def append(id,name,group,unit,definition,effect,agency,values,urls,method='原表',note=''):
 x['catalog']=[c for c in x['catalog'] if c['id']!=id]
 x['observations']=[o for o in x['observations'] if o['metric']!=id]
 x['catalog'].append(dict(id=id,name=name,group=group,unit=unit,frequency='年度',definition=definition,effect=effect,lag='年度结构变化',agency=agency))
 for (year,value),url in zip(values.items(),urls):
  x['observations'].append(dict(metric=id,date=f'{year}-12',value=value,url=url,method=method,note=note,yoy=None,mom=None))
def years(values):return dict(zip(range(2021,2026),values))
append('pigfeed_annual','全年猪饲料产量','成本','万吨','全国饲料工业统计猪饲料产量；不包含全部养殖场自产自用饲料。','观察商业饲料需求与养殖活动；配方、体重及工业料渗透率变化影响解释，不能等同比例推算猪存栏。','中国饲料工业协会 / 农业农村部',years([13076.5,13597.5,14975.2,14391.3,16639.4]),feed_urls,note='年度原始发布值；2023、2024报告网页迁移至2026目录，统计年度按报告标题识别。')
append('industrialfeed_annual','全年工业饲料总产量','成本','万吨','全国工业饲料产量，包含猪、禽、水产及其他饲料；不是猪饲料量。','观察饲料原料总需求，需结合动物种类结构与配方。','中国饲料工业协会 / 农业农村部',years([29344.3,30223.4,32162.7,31503.1,34225.3]),feed_urls,note='年度原始发布值；2023、2024报告网页迁移至2026目录。')
append('population_annual','年末全国人口','需求','万人','大陆31省区市和现役军人人口；不包括港澳台居民和外籍人员。','人口总量影响长期需求，人均消费、年龄和偏好也会变化。','国家统计局',years([141260,141175,140967,140828,140489]),population_urls,method='官方发布 / 官方转载',note='统计公报及政府转载的年末值，保留当年发布版本。')
append('income_annual','居民人均可支配收入','需求','元/人/年','全国居民人均可支配收入名义年度值；不是实际收入，也不是猪肉消费预算。','购买力影响需求结构，但收入增长不必然增加猪肉数量。','国家统计局',years([35128,36883,39218,41314,43377]),income_urls)
for id,name,values in [('lh_daily_volume_annual','LH全年日均成交量',{2021:2.5,2025:7.4}),('lh_daily_oi_annual','LH全年日均持仓量',{2021:6.0,2025:21.3}),('lh_volume_annual','LH全年成交量',{2025:1799.3})]:
 append(id,name,'期货','万手','大商所生猪期货全部合约年度报告值；日均持仓不是年末持仓，不代表LH2611或实时市场。','观察品种参与度与流动性；成交或持仓增加不能单独判断多空方向。','大连商品交易所（投保中心官方转载）',values,[future_url]*len(values),method='交易所官方转载',note='2026年1月8日上市五周年报告；2022—2024未取得，全年成交量2021也未取得。年度落点为统计年12月，不是发布日。')
(root/'research/data-stage.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
print('新增7指标、25条观测；部分期货年份保持缺失。')
