# scrapy-national_data

抓取内容：中国数据官网-月度数据 http://data.stats.gov.cn/easyquery.htm?cn=A01

分析网站：
  
ajax请求json数据，请求url不变，只改变请求参数，构造参数有两种方式（getTree,QueryData);
  
该站不检查Cookie,只限制ip访问频率，且封禁ip时间较长；

抓取结果：

