import sys
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'http://asp.xpgtv.com'

    headers = {
        "User-Agent": "okhttp/3.12.11"
    }

    def homeContent(self, filter):
        data = self.fetch(f"{self.host}/api.php/v2.vod/androidtypes", headers=self.headers).json()
        
        classes = []
        filters = {}
        
        for item in data['data']:
            type_id = str(item["type_id"])
            classes.append({"type_name": item["type_name"], "type_id": type_id})
            
            # 为每个分类构建过滤器
            filter_list = []
            
            # 添加分类筛选
            if item.get('classes') and len(item['classes']) > 0 and item['classes'][0] != '':
                class_options = [{"n": "全部", "v": "all"}]
                class_options.extend([{"n": cls, "v": cls} for cls in item['classes']])
                filter_list.append({
                    "key": "class",
                    "name": "类型",
                    "value": class_options
                })
            
            # 添加地区筛选
            if item.get('areas') and len(item['areas']) > 0 and item['areas'][0] != '':
                area_options = [{"n": "全部", "v": "all"}]
                area_options.extend([{"n": area, "v": area} for area in item['areas']])
                filter_list.append({
                    "key": "area",
                    "name": "地区",
                    "value": area_options
                })
            
            # 添加年份筛选
            if item.get('years') and len(item['years']) > 0 and item['years'][0] != '':
                year_options = [{"n": "全部", "v": "all"}]
                year_options.extend([{"n": year, "v": year} for year in item['years']])
                filter_list.append({
                    "key": "year",
                    "name": "年份",
                    "value": year_options
                })
            
            # 添加排序筛选（通用）
            filter_list.append({
                "key": "sortby",
                "name": "排序",
                "value": [
                    {"n": "最新", "v": "time"},
                    {"n": "最热", "v": "hits"},
                    {"n": "评分", "v": "score"}
                ]
            })
            
            filters[type_id] = filter_list

        return {
            "class": classes,
            "filters": filters
        }

    def homeVideoContent(self):
        # 获取首页视频内容
        home_video_data = self.fetch(f"{self.host}/api.php/v2.main/androidhome", headers=self.headers).json()
        videos = []
        for section in home_video_data['data']['list']:
            videos.extend(self.getlist(section['list']))
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        # 构建请求参数 - 注意参数名与JS代码保持一致
        params = {
            "page": pg,
            "type": tid
        }
        
        # 添加过滤参数 - 使用 extend 而不是 filters
        if extend.get('area') and extend['area'] != 'all':
            params["area"] = extend['area']
        if extend.get('year') and extend['year'] != 'all':
            params["year"] = extend['year']
        if extend.get('class') and extend['class'] != 'all':
            params["class"] = extend['class']
        if extend.get('sortby') and extend['sortby'] != 'all':
            params["sortby"] = extend['sortby']
        
        # 过滤空参数
        filtered_params = {k: v for k, v in params.items() if v}
        
        try:
            rsp = self.fetch(f'{self.host}/api.php/v2.vod/androidfilter10086', 
                            headers=self.headers, 
                            params=filtered_params).json()
            
            return {
                'list': self.getlist(rsp['data']),
                'page': int(pg),
                'pagecount': 9999,
                'limit': 90,
                'total': 999999
            }
        except Exception as e:
            print(f"分类数据获取失败: {e}")
            return {
                'list': [],
                'page': int(pg),
                'pagecount': 1,
                'limit': 90,
                'total': 0
            }

    def detailContent(self, ids):
        try:
            video_id = ids[0] if isinstance(ids, list) else ids
            rsp = self.fetch(f'{self.host}/api.php/v3.vod/androiddetail2?vod_id={video_id}', 
                            headers=self.headers).json()
            v = rsp['data']
            
            vod = {
                'vod_id': v.get('id') or video_id,
                'vod_name': v.get('name', ''),
                'vod_pic': v.get('pic', ''),
                'vod_year': v.get('year', ''),
                'vod_area': v.get('area', ''),
                'vod_lang': v.get('lang', ''),
                'type_name': v.get('className', ''),
                'vod_actor': v.get('actor', ''),
                'vod_director': v.get('director', ''),
                'vod_content': v.get('content', ''),
                'vod_remarks': v.get('updateInfo') or v.get('score', ''),
                'vod_play_from': '小苹果',
                'vod_play_url': '#'.join([f"{i['key']}${i['url']}" for i in v['urls']]) if v.get('urls') else ''
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"详情数据获取失败: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg='1'):
        try:
            from urllib.parse import quote
            rsp = self.fetch(f'{self.host}/api.php/v2.vod/androidsearch10086?page={pg}&wd={quote(key)}', 
                            headers=self.headers).json()
            
            return {
                'list': self.getlist(rsp['data']),
                'page': int(pg),
                'pagecount': 9999,
                'limit': 90,
                'total': 999999
            }
        except Exception as e:
            print(f"搜索失败: {e}")
            return {
                'list': [],
                'page': int(pg),
                'pagecount': 1,
                'limit': 90,
                'total': 0
            }

    def playerContent(self, flag, id, vipFlags):
        header = {
            'user_id': 'XPGBOX',
            'token2': 'XFxIummRrngadHB4TCzeUaleebTX10Vl/ftCvGLPeI5tN2Y/liZ5tY5e4t8=',
            'version': 'XPGBOX com.phoenix.tv1.5.5',
            'hash': '524f',
            'screenx': '2331',
            'user-agent': 'okhttp/3.12.11',
            'token': 'VkxTyy6Krh4hd3lrQySUCJlsDYzzxxBbttphr3DiQNhmJkwoyEEm2YEu8qcOFGz2SmxGbIaSC91pa+8+VE9+SPQjGWY/wnqwKk1McYhsGyVVvHRAF0B1mD7922ara1o3k/EwZ1xyManr90EeUSxI7rPOLBwX5zeOri31MeyDfBnIdhckWld4V1k2ZfZ3QKbN',
            'timestamp': '1749174636',
            'screeny': '1121',
        }
        
        final_url = id
        if 'http' not in id:
            final_url = f"http://c.xpgtv.net/m3u8/{id}.m3u8"
            
        return {"parse": 0, "jx": 0, "url": final_url, "header": json.dumps(header)}

    def localProxy(self, param):
        pass

    def getlist(self, data):
        if not data:
            return []
            
        videos = []
        for vod in data:
            # 优先显示更新信息
            if vod.get('updateInfo'):
                remarks = f"更新至{vod.get('updateInfo')}"
            # 如果评分为0.0，尝试显示其他字段
            elif vod.get('score') in ['0.0', '0', ''] or not vod.get('score'):
                # 按优先级显示其他字段
                if vod.get('year'):
                    remarks = vod.get('year')
                elif vod.get('area'):
                    remarks = vod.get('area')
                elif vod.get('lang'):
                    remarks = vod.get('lang')
                elif vod.get('className'):
                    remarks = vod.get('className')
                else:
                    remarks = ''
            else:
                # 正常显示评分
                remarks = vod['score']
            
            videos.append({
                "vod_id": str(vod['id']),  # 转换为字符串，与JS代码一致
                "vod_name": vod['name'],
                "vod_pic": vod['pic'],
                "vod_remarks": remarks
            })

        return videos