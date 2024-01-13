#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request

class Spider(Spider):  # 元类 默认的元类 type  #img (.+?)
	def getName(self):
		return "圣城影视"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"剧集片库":"2",
			"电影片库":"1",
			"纪录片库":"5",
			"动漫片库":"4",
			"综艺片库":"3",
			"短剧片库":"21"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		htmlTxt=self.custom_webReadFile(urlStr='https://sc1080.top/',header=self.header)
		videos = self.custom_list(html=htmlTxt,patternTxt=[r'<div class="module-item-pic"><a href="(?P<url>.+?)" title="(?P<title>.+?)"','<img class="lazy lazyloaded" data-src="(.+?)" '])
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		Url='https://sc1080.top/index.php/vod/show/id/{0}/page/{1}.html'.format(tid,pg)
		htmlTxt=self.custom_webReadFile(urlStr=Url,header=self.header)

		videos = self.custom_list(html=htmlTxt,patternTxt=[r'<div class="module-item-pic"><a href="(?P<url>.+?)" title="(?P<title>.+?)"','<img class="lazy lazyloaded" data-src="(.+?)" '])
		# print(len(videos))
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pg if len(videos)<36 else int(pg)+1
		result['limit'] = len(videos)
		result['total'] = 999999
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		title = aid[0]#片名
		urlId = ''+aid[1]#URL
		logo = aid[2]#封面
		year=''#年份
		area=''
		actor=''
		director=''
		content=''
		vodItems=[]
		typeName=''
		vod_play_from=[]#线路
		vod_play_url=[]#剧集
		htmlTxt=self.custom_webReadFile(urlStr=urlId,header=self.header)
		line=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<div class="module-tab-item tab-item" data-dropdown-value="(.+?)">',Index=1)
		
		if len(line)<1:
			return  {'list': []}
		circuit=self.custom_lineList(Txt=htmlTxt,mark=r'module-blocklist scroll-box scroll-box-y',after='</div>')
		
		vod_play_from=[x for x in line]
		for v in circuit:
			vodItems = self.custom_EpisodesList(html=v,RegexText=r'<a href="(?P<url>.+?)" title=".+?">(?P<title>.+?)</a>')
			joinStr = "#".join(vodItems)
			vod_play_url.append(joinStr)

		temporary=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<a href="/index.php/vod/show/class/(%|\w)+?/id/1.html">(.+?)</a>',Index=2)
		temporary=[i[1] for n, i in enumerate(temporary) if i not in temporary[:n]]
		typeName= "/".join(temporary)
		year=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a class="tag-link" href="/index.php/vod/show/id/1/year/\d{4}.html">(\d{4})</a>',Index=1)
		temporary=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<a class="tag-link" href="/index.php/vod/show/area/(%|\w)+?/id/1.html">(.+?)</a>',Index=2)
		temporary=[i[1] for n, i in enumerate(temporary) if i not in temporary[:n]]
		area= "/".join(temporary)
		temporary=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<span class="slash">/</span><a href="/index.php/vod/search/actor/(%|\w)+?\.html" target="_blank">(.+?)</a>',Index=2)
		temporary=[i[1] for n, i in enumerate(temporary) if i not in temporary[:n]]
		actor= "/".join(temporary)
		temporary=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<span class="slash">/</span><a href="/index.php/vod/search/director/(%|\w)+?\.html" target="_blank">(.+?)</a>',Index=2)
		temporary=[i[1] for n, i in enumerate(temporary) if i not in temporary[:n]]
		director= "/".join(temporary)
		content=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<div class="video-info-item video-info-content vod_content">(.+?)</div>',Index=1)
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":typeName,
			"vod_year":self.custom_removeHtml(txt=year),
			"vod_area":self.custom_removeHtml(txt=area),
			"vod_remarks":'',
			"vod_actor":self.custom_removeHtml(txt=actor),
			"vod_director":self.custom_removeHtml(txt=director),
			"vod_content":self.custom_removeHtml(txt=content)
		}
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = "$$$".join(vod_play_url)
		result = {
			'list':[
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		Url='https://sc1080.top/index.php/vod/search.html?wd={0}'.format(urllib.parse.quote(key))
		htmlTxt=self.custom_webReadFile(urlStr=Url,header=self.header)

		videos = self.custom_list_search(html=htmlTxt)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		parse=1
		jx=0
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = id
		result['jx'] = jx#VIP解析,0=不解析、1=解析
		result["header"] =  {
		"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
		}
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {
		"Referer":"https://sc1080.top/",
		"User-Agent":"User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		"Host":"sc1080.top"
	}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	#分类取结果
	def custom_list(self,html,patternTxt):
		ListRe=re.finditer(patternTxt[0], html, re.M|re.S)
		imgListRe=re.finditer(patternTxt[1], html, re.M|re.S)
		videos = []
		head="https://sc1080.top"
		renew='圣城影视'		
		for vod in ListRe:
			url = vod.group('url')
			title =self.custom_removeHtml(txt=vod.group('title'))
			try:
				img=next(imgListRe).group(1)
			except :
				img='https://agit.ai/lanhaidixingren/Tvbox/raw/branch/master/CoverError.png'
			if len(url) == 0:
				continue
			if len(img)<5:
				img='https://agit.ai/lanhaidixingren/Tvbox/raw/branch/master/CoverError.png'

			videos.append({
				"vod_id":"{0}###{1}###{2}".format(title,head+url,img),
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":renew
			})
		return videos
		#访问网页
	def custom_webReadFile(self,urlStr,header,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		# import ssl
		# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName)
		return html
	#判断是否要调用vip解析
	def custom_ifJx(self,urlTxt):
		Isjiexi=0
		RegexTxt=r'(youku.com|v.qq|bilibili|iqiyi.com)'
		if self.custom_RegexGetText(Text=urlTxt,RegexText=RegexTxt,Index=1)!='':
			Isjiexi=1
		return Isjiexi
	#取剧集区
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	# 取集数
	def custom_EpisodesList(self,html,RegexText):
		ListRe=re.finditer(RegexText, html, re.M|re.S)
		videos = []
		head="https://sc1080.top"
		for vod in ListRe:
			url = vod.group('url')
			title =self.custom_removeHtml(txt=vod.group('title'))
			if len(url) == 0:
				continue
			videos.append(title+"$"+head+url)
		return videos

	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")	
	def custom_list_search(self,html):#搜索页的源码太复杂
		videos = []
		head="https://sc1080.top"

		temporaryList=self.custom_lineList(Txt=html,mark='<div class="module-search-item">',after='</h3>')
		
		for vod in temporaryList:
			img=self.custom_RegexGetText(Text=vod,RegexText=r'data-src="(.+?)"',Index=1)
			title=self.custom_RegexGetText(Text=vod,RegexText=r'alt="(.+?)"',Index=1)
			url=self.custom_RegexGetText(Text=vod,RegexText=r'class="video-serial" href="(.+?)"',Index=1)
			
			if title=='' or url=='':
				continue
			if len(img)<5:
				img='https://agit.ai/lanhaidixingren/Tvbox/raw/branch/master/CoverError.png'
			videos.append({
					"vod_id":"{0}###{1}###{2}".format(title,head+url,img),
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
		return videos
# T=Spider()
# l=T.searchContent(key='柯南',quick='')
# l=T.homeVideoContent()
# l=T.categoryContent(tid='1',pg='1',filter=False,extend='')
# for x in l['list']:
# 	print(x['vod_id'])
# mubiao= '犯罪都市3###https://sc1080.top/index.php/vod/detail/id/599876.html###https://hwk2.ji8cdn.com/img/ximgs/05482358f8ab8e568229af2886ecaedad38a62228cb98c40f00e3a7557c56b171f9e5e77acc16e76dad5550dfe20fe53.jpg'#l['list'][0]['vod_id']
# playTabulation=T.detailContent(array=[mubiao,])
# print(playTabulation)
# vod_play_from=playTabulation['list'][0]['vod_play_from']
# vod_play_url=playTabulation['list'][0]['vod_play_url']
# url=vod_play_url.split('$$$')
# vod_play_from=vod_play_from.split('$$$')[0]
# url=url[0].split('$')
# url=url[1].split('#')[0]
# # print(vod_play_from)
# m3u8=T.playerContent(flag=vod_play_from,id=url,vipFlags=True)
# print(m3u8)