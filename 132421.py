import os
import random
import re
import sys
import time
import logging
from urllib.parse import urlparse, parse_qs
import requests  # type: ignore
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup  # 确保导入BeautifulSoup
import asyncio

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    def __init__(self):
        self.ck列表 = []
        self.分享码列表 = []
        self.助力信号 = 'True'
        self.sk列表 = []
        self.用户代理列表 = []
        self.所有打印列表 = []
        self.dewu_dutoken = None  # 初始化dewu_dutoken属性

    def 加载环境变量(self):
        env_str = os.getenv("dewu_x_auth_token")
        if env_str:
            self.ck列表 += env_str.replace("&", "\n").split("\n")

        # 加载dewu_dutoken
        env_str = os.getenv("dewu_dutoken")
        if env_str:
            self.dewu_dutoken = env_str  # 将值赋给类属性
        
        env_str = os.getenv("dewu_help_signal")
        if env_str:
            self.助力信号 = env_str

        env_str = os.getenv("dewu_sk")
        if env_str:
            self.sk列表 = env_str.replace("&", "\n").split("\n")

        env_str = os.getenv("dewu_user_agent")
        if env_str:
            self.用户代理列表 = env_str.replace("&", "\n").split("\n")

config = Config()
config.加载环境变量()

class 得物环境:
    def __init__(self):
        self.ck_名称 = "dewuCK"
        self.is_promise_all = True
        self.ua_默认 = "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv)"
        self.用户列表 = []

    @staticmethod
    def 日志(消息):
        print(消息)

    def 添加用户(self, 用户):
        self.用户列表.append(用户)

class 任务:
    def __init__(self, 字符串):
        数据 = 字符串.split("#")
        self.索引 = 0  # 用户索引
        self.ck = 数据[0]  # Cookie
        self.du_token = 数据[1] if len(数据) > 1 else ""
        self.sk = 数据[2] if len(数据) > 2 else ""
        self.ua = 得物环境.ua_默认

    def 请求(self, 方法, url, body=None):
        头部 = {
            "Host": "app.dewu.com",
            "x-auth-token": f"Bearer {self.ck}",
            "duToken": self.du_token,
            "User-Agent": self.ua
        }

        if 方法.lower() == 'get':
            响应 = requests.get(url, headers=头部)
        else:
            响应 = requests.post(url, headers=头部, json=body)

        return 响应.json()

    async def 用户初始化(self):
        url = "https://app.dewu.com/hacking-tree/v1/user/init"
        数据 = {
            "keyword": "",
            "source": "wotab04",
            "koc": 0,
            "ffOfflineFlag": "",
            "keywordType": 0
        }
        结果 = self.请求("POST", url, 数据)
        得物环境.日志(f"账号[{self.索引}] 初始化: {结果}")

async def 运行任务(得物环境):
    await asyncio.gather(*(用户.用户初始化() for 用户 in 得物环境.用户列表))

# 主逻辑
得物环境 = 得物环境()

# 这里需要添加用户数据，例如：
用户数据 = [
    "your_ck_value#your_du_token#your_sk_value",  # 替换为实际的用户数据格式
]

for idx, 用户 in enumerate(用户数据):
    任务实例 = 任务(用户)
    得物环境.添加用户(任务实例)


class 得物:
    浇水克数: int = 40  # 每次浇水克数
    剩余克数: int = 1800  # 最后浇水剩余不超过的克数

    def __init__(self, x_auth_token, 索引):
        self.索引 = 索引
        self.浇水克数 = self.浇水克数
        self.剩余克数 = self.剩余克数
        self.session = requests.Session()
        用户代理 = config.用户代理列表[索引]
        应用版本 = re.search(r'pp/([0-9]+\.[0-9]+\.[0-9]+)', 用户代理).group(1)
        sk = config.sk列表[索引]

        # 初始化请求头，包括dewu_dutoken
        self.headers = {
            'appVersion': 应用版本,
            'User-Agent': 用户代理,
            'x-auth-token': x_auth_token,
            'uuid': '0000000000000000',
            'SK': sk,
            'dewu_dutoken': config.dewu_dutoken  # 直接将dewu_dutoken添加到请求头中
        }

        self.tree_id = 0
        self.任务完成数量 = 0
        self.累计任务列表 = []
        self.任务字典列表 = []
        self.is_team_tree = False
        self.dutoken = config.dewu_dutoken  # 在这里访问dewu_dutoken        

    def 我的打印(self, *参数, sep=' ', end='\n', **kwargs):
        输出 = sep.join(map(str, 参数)) + end
        config.所有打印列表.append(输出)
        logging.info(输出.strip())

    def 发送通知消息(self, 标题):
        try:
            from notify import send  # type: ignore # 导入青龙通知文件

            if not 标题:
                logging.warning('通知标题为空，无法发送通知。')
                return

            send(标题, ''.join(config.所有打印列表))
        except ImportError as e:
            logging.error('模块导入失败！请检查notify模块是否存在。错误信息:', exc_info=e)
        except Exception as e:
            logging.error(f'发送通知消息失败！错误信息: {str(e)}')

    def 重试请求(self, 请求函数, *args, 重试次数=3, **kwargs):
        for i in range(重试次数):
            try:
                return 请求函数(*args, **kwargs)
            except requests.RequestException as e:
                if i < 重试次数 - 1:
                    logging.warning(f'请求失败，正在重试 ({i + 1}/{重试次数})... 错误: {e}')
                    time.sleep(2)  # 等待后重试
                else:
                    logging.error(f'请求失败，已达到最大重试次数. 错误: {e}')
                    raise

    # 获得url参数中键为key的值
    def 获取url键值(self, url, key):
        解析的url = urlparse(url)
        查询参数 = parse_qs(解析的url.query)
        _字典 = {k: v[0] if len(v) == 1 else v for k, v in 查询参数.items()}
        键值 = _字典.get(key)
        return 键值

    # 其他方法...

    # 种树奖品
    def 树的信息(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/target/info'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200:
            名称 = 响应字典.get('data').get('name')
            等级 = 响应字典.get('data').get('level')
            return 名称, 等级
        self.我的打印(响应字典.get('msg'))
        return '', ''

    # 判断是否是团队树
    def 判断是否是团队树(self):
        url = 'https://app.dewu.com/hacking-tree/v1/team/info'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('data').get('show') is True and 响应字典.get('data').get('teamTreeId'):
            self.is_team_tree = True

    # 领潮金币签到
    def 签到(self):
        url = 'https://app.dewu.com/hacking-game-center/v1/sign/sign'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200:
            self.我的打印(f"签到成功！")
            return
        self.我的打印(f"签到失败！ {响应字典.get('msg')}")

    # 水滴7天签到
    def 水滴签到(self):
        url = 'https://app.dewu.com/hacking-tree/v1/sign/sign_in'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200:
            self.我的打印(f"签到成功,获得{响应字典.get('data').get('Num')}g水滴")
            return
        self.我的打印(f"签到失败！ {响应字典.get('msg')}")

    # 领取气泡水滴
    def 领取气泡水滴(self):
        临时数量 = -1  # 用于判断两次浇水，奖励是否有变化
        倒计时 = 0
        获取信号 = False
        for _ in range(50):
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            响应 = self.重试请求(self.session.get, url, headers=self.headers)
            响应字典 = 响应.json()
            if 响应字典.get('code') != 200:
                self.我的打印(f"获取气泡水滴信息失败! {响应字典}")
                return
            数据 = 响应字典.get('data')
            可领取 = 数据.get('receivable')
            if 可领取 is True:  # 判断今天是否可领取
                if 数据.get('dailyExtra'):  # 第一次领取时
                    水滴数量 = 数据.get('dailyExtra').get('totalDroplet')
                else:  # 第二次领取时
                    水滴数量 = 数据.get('onlineExtra').get('totalDroplet')
                if 临时数量 == 水滴数量 or 获取信号:
                    self.我的打印(f"当前可领取气泡水滴{水滴数量}g")
                    url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/receive'
                    响应 = self.重试请求(self.session.post, url, headers=self.headers)
                    响应字典 = 响应.json()
                    if 响应字典.get('code') != 200:
                        倒计时 += 60
                        if 倒计时 > 60:  # 已经等待过60s，仍未领取成功，退出
                            self.我的打印(f"领取气泡水滴失败! {响应字典}")
                            return
                        self.我的打印(f'等待{倒计时}秒后领取')
                        time.sleep(倒计时)
                        continue
                    self.我的打印(f"领取气泡水滴成功! 获得{响应字典.get('data').get('totalDroplet')}g水滴")
                    倒计时 = 0  # 领取成功，重置等待时间
                    continue
                临时数量 = 水滴数量
                self.我的打印(f'当前气泡水滴{水滴数量}g，未满，开始浇水')
                if not self.浇水():  # 浇水失败
                    获取信号 = True  # 给出直接领取信号
                time.sleep(0.5)
                continue  # 浇水成功后查询信息
            # 今天不可领取了，退出
            水滴数量 = 响应字典.get('data').get('dailyExtra').get('totalDroplet')
            self.我的打印(f"{响应字典.get('data').get('dailyExtra').get('popTitle')}，已经积攒{水滴数量}g水滴!")
            return

    # 浇水充满气泡水滴
    def 浇水充满气泡水滴(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            响应 = self.重试请求(self.session.get, url, headers=self.headers)
            响应字典 = 响应.json()
            count = 响应字典.get('data').get('dailyExtra').get('times')
            if not count:
                self.我的打印(f"气泡水滴已充满，明日可领取{响应字典.get('data').get('dailyExtra').get('totalDroplet')}g")
                return
            for _ in range(count):
                if not self.浇水():  # 无法浇水时退出
                    return
                time.sleep(0.5)

    # 领取木桶水滴,200秒满一次,每天领取3次
    def 领取木桶水滴(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/get_generate_droplet'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"领取木桶水滴失败! {响应字典}")
            return
        self.我的打印(f"领取木桶水滴成功! 获得{响应字典.get('data').get('droplet')}g水滴")

    # 判断木桶水滴是否可以领取
    def 判断木桶水滴(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/generate_info'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('data').get('currentDroplet') == 100:
            self.我的打印(f"今天已领取木桶水滴{响应字典.get('data').get('getTimes')}次")
            self.领取木桶水滴()
            return True
        return False

    # 获取助力码
    def 获取分享码(self):
        url = 'https://app.dewu.com/hacking-tree/v1/keyword/gen'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"获取助力码失败! {响应字典}")
            return
        关键字描述 = 响应字典.get('data').get('keywordDesc').replace('\n', '')
        self.我的打印(f"获取助力码成功! {关键字描述}")

    # 获得当前水滴数
    def 获取水滴数量(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/init'
        _json = {"keyword": ""}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        数据 = 响应字典.get('data')
        if 数据:
            水滴数量 = 数据.get('droplet')
            return 水滴数量
        self.我的打印(f'获得当前水滴数出错 {响应字典}')
        return '获取失败'

    # 领取累计任务奖励
    def 领取累计任务奖励(self, 条件):
        url = 'https://app.dewu.com/hacking-tree/v1/task/extra'
        _json = {'condition': 条件}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"领取累计任务奖励失败! {响应字典}")
            return
        self.我的打印(f"领取累计任务奖励成功! 获得{响应字典.get('data').get('num')}g水滴")

    # 领取任务奖励
    def 领取任务奖励(self, 分类, 任务_id, 任务类型):
        time.sleep(0.2)
        url = 'https://app.dewu.com/hacking-tree/v1/task/receive'
        _json = {'classify': 分类, 'taskId': 任务_id, 'taskType': 任务类型}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"领取任务奖励失败! {响应字典}")
            return
        self.我的打印(f"领取任务奖励成功! 获得{响应字典.get('data').get('num')}g水滴")

    # 领取浇水奖励
    def 领取浇水奖励(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_watering_reward'
        _json = {'promote': ''}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"领取浇水奖励失败! {响应字典}")
            return
        self.我的打印(f"领取浇水奖励成功! 获得{响应字典.get('data').get('currentWateringReward').get('rewardNum')}g水滴")

    # 领取等级奖励
    def 领取等级奖励(self):
        for _ in range(20):
            url = 'https://app.dewu.com/hacking-tree/v1/tree/get_level_reward'
            _json = {'promote': ''}
            响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
            响应字典 = 响应.json()
            if 响应字典.get('code') != 200 or 响应字典.get('data') is None:
                self.我的打印(f"领取等级奖励失败! {响应字典.get('msg')}")
                return
            等级 = 响应字典.get('data').get('levelReward').get('showLevel') - 1
            奖励数量 = 响应字典.get('data').get('currentLevelReward').get('rewardNum')
            self.我的打印(f"领取{等级}级奖励成功! 获得{奖励数量}g水滴")
            if 响应字典.get('data').get('levelReward').get('isComplete') is False:
                return
            time.sleep(1)

    # 浇水
    def 浇水(self):
        if self.is_team_tree:  # 如果是团队树，使用团队浇水
            return self.团队浇水()
        url = 'https://app.dewu.com/hacking-tree/v1/tree/watering'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"浇水失败! {响应字典}")
            return False
        self.我的打印(f"成功浇水{self.浇水克数}g")
        if 响应字典.get('data').get('nextWateringTimes') == 0:
            self.我的打印('开始领取浇水奖励')
            time.sleep(1)
            self.领取浇水奖励()
        return True

    # 团队浇水
    def 团队浇水(self):
        url = 'https://app.dewu.com/hacking-tree/v1/team/tree/watering'
        _json = {"teamTreeId": self.tree_id}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"浇水失败! {响应字典}")
            return False
        self.我的打印(f"成功浇水{self.浇水克数}g")
        if 响应字典.get('data').get('nextWateringTimes') == 0:
            self.我的打印('开始领取浇水奖励')
            time.sleep(1)
            self.领取浇水奖励()
        return True

    # 多次执行浇水，领取浇水奖励
    def 执行领取浇水奖励(self):
        for _ in range(20):
            url = 'https://app.dewu.com/hacking-tree/v1/tree/get_tree_info'
            响应 = self.重试请求(self.session.get, url, headers=self.headers)
            响应字典 = 响应.json()
            if 响应字典.get('code') != 200:
                self.我的打印(f"获取种树进度失败! {响应字典}")
                return
            count = 响应字典.get('data').get('nextWateringTimes')  # 获取浇水奖励还需要的浇水次数
            if 响应字典.get('data').get('wateringReward') is None or count <= 0:  # 没有奖励时退出
                return
            for _ in range(count):
                if not self.浇水():  # 无法浇水时退出
                    return

    # 浇水直到少于指定克数
    def 浇水直到少于(self):
        水滴数量 = self.获取水滴数量()
        if 水滴数量 > self.剩余克数:
            count = int((水滴数量 - self.剩余克数) / self.浇水克数)
            for _ in range(count + 1):
                if not self.浇水():  # 无法浇水时退出
                    return

    # 提交任务完成状态
    def 提交任务完成状态(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/commit'
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200:
            return True
        return False

    # 获取任务列表
    def 获取任务列表(self):
        # 请求第一个任务列表的URL
        url1 = 'https://app.dewu.com/hacking-tree/v1/task/list'
        响应1 = self.重试请求(self.session.get, url1, headers=self.headers)
        响应字典1 = 响应1.json()
        
        # 请求第二个活动列表的URL
        url2 = 'https://app.dewu.com/hacking-ad/v1/activity/compound/list'
        响应2 = self.重试请求(self.session.get, url2, headers=self.headers)
        响应字典2 = 响应2.json()
        
        # 处理第一个URL的响应
        if 响应字典1.get('code') == 200:
            self.任务完成数量 = 响应字典1.get('data').get('userStep')  # 任务完成数量
            self.累计任务列表 = 响应字典1.get('data').get('extraAwardList')  # 累计任务列表
            self.任务字典列表 = 响应字典1.get('data').get('taskList')  # 任务列表
            
            # 处理第二个URL的响应
            if 响应字典2.get('code') == 200:
                self.活动列表 = 响应字典2.get('data').get('activityList')  # 活动列表
                return True

        return False  # 如果有任一请求失败，返回False

    # 水滴大放送任务步骤1
    def 任务获取(self, 任务_id, 任务类型):
        url = 'https://app.dewu.com/hacking-task/v1/task/obtain'
        _json = {'taskId': 任务_id, 'taskType': 任务类型}
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200 and 响应字典.get('status') == 200:
            return True
        return False

    # 浏览任务开始且等待16s，任务类型有变化，浏览15s会场会变成16
    def 任务提交准备(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/pre_commit'
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        if 响应字典.get('code') == 200 and 响应字典.get('status') == 200:
            return True
        return False

    # 执行任务
    def 执行任务(self):
        self.获取任务列表()  # 刷新任务列表
        for 任务字典 in self.任务字典列表:
            if 任务字典.get('isReceiveReward') is True:  # 今天不能进行操作了，跳过
                continue
            if 任务字典.get('rewardCount') >= 3000:  # 获取水滴超过3000的，需要下单，跳过
                continue
                
            分类 = 任务字典.get('classify')
            任务_id = 任务字典.get('taskId')
            任务类型 = 任务字典.get('taskType')
            任务名称 = 任务字典.get('taskName')
            
            btd = self.获取url键值(任务字典.get('jumpUrl'), 'btd')
            btd = int(btd) if btd else btd  # 如果btd存在 转换为整数类型
            spu_id = self.获取url键值(任务字典.get('jumpUrl'), 'spuId')
            spu_id = int(spu_id) if spu_id else spu_id  # 如果spuId存在 转换为整数类型

            # 处理已完成的任务
            if 任务字典.get('isComplete') is True:  
                if 任务名称 == '领40g水滴值' and not 任务字典.get('receivable'):  
                    continue  # 已领取过40g水滴，跳过
                self.我的打印(f'开始任务：{任务名称}')
                self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            self.我的打印(f'★开始任务：{任务名称}')
            
            # 签到任务
            if 任务名称 == '完成一次签到':  
                self.签到()
                数据 = {'taskId': 任务_id, 'taskType': str(任务类型)}
                if self.提交任务完成状态(数据):
                    self.领取任务奖励(分类, 任务_id, 任务类型)
                    continue

            # 领取水滴任务
            if 任务名称 == '领40g水滴值':  
                self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            # 收集水滴
            if 任务名称 == '收集一次水滴生产':
                if self.判断木桶水滴():
                    self.领取任务奖励(分类, 任务_id, 任务类型)
                else:
                    self.我的打印('当前木桶水滴未达到100g，下次来完成任务吧！')
                continue

            # 浏览任务
            if 任务名称 == '浏览【我】的右上角星愿森林入口':
                _json = {"action": 任务_id}
                url = 'https://app.dewu.com/hacking-tree/v1/user/report_action'
                响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
                响应字典 = 响应.json()
                if 响应字典.get('code') == 200:
                    self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            # 处理各种模式匹配的任务
            if any(re.match(模式, 任务名称) for 模式 in ['参与1次上上签活动', '从桌面组件访问许愿树', '参与1次拆盲盒', '去.*']):
                _json = {'taskId': 任务_id, 'taskType': str(任务类型)}
                self.提交任务完成状态(_json)
                self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            if any(re.match(模式, 任务名称) for 模式 in ['.*收藏.*']):
                _json = {'taskId': 任务_id, 'taskType': str(任务类型), 'btd': btd, 'spuId': spu_id}
                self.提交任务完成状态(_json)
                self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            if any(re.match(模式, 任务名称) for 模式 in ['.*订阅.*', '.*逛一逛.*', '逛逛.*活动']):
                _json = {'taskId': 任务_id, 'taskType': str(任务类型), 'btd': btd}
                self.提交任务完成状态(_json)
                self.领取任务奖励(分类, 任务_id, 任务类型)
                continue

            if any(re.match(模式, 任务名称) for 模式 in ['.*逛逛.*']):
                _json = {'taskId': 任务_id, 'taskType': 任务类型, 'btd': btd}
                if self.任务提交准备(_json):
                    self.我的打印(f'开始“逛逛”任务，动态访问目标网址...')                    
                    
                    # 替换为实际目标网址，通常来自于任务字典的 URL
                    目标网址 = 任务字典.get('目标网址', 'https://prd-otel-h5-public.dewu.com/api/traces')  # 实际替换
                    
                    响应 = self.重试请求(self.session.get, 目标网址)
                    self.我的打印(f'访问目标网址，响应状态：{响应.status_code}')
                    time.sleep(2)  # 每次访问间隔2秒

                    # 动态生成滚动 URL
                    滚动URL = f'{目标网址}/scroll?offset={{}}'  # 使用实际目标网址进行格式化
                    
                    for i in range(5):  # 假设滚动5次
                        响应滚动 = self.重试请求(self.session.get, 滚动URL.format(i * 10))
                        
                        if 响应滚动.status_code == 404:
                            self.我的打印(f'向下滚动第{i + 1}次，响应状态：404，无法访问此链接，停止滚动')
                            break  # 在接收到404状态后停止滚动

                        self.我的打印(f'向下滚动第{i + 1}次，响应状态：{响应滚动.status_code}')
                        time.sleep(2)  # 再次等待

                    # 提交完成状态
                    _json = {'taskId': 任务_id, 'taskType': str(任务类型), 'btd': btd}
                    if self.提交任务完成状态(_json):
                        self.领取任务奖励(分类, 任务_id, 任务类型)
                    else:
                        self.我的打印('领取任务奖励失败，请刷新任务列表')
                        self.获取任务列表()  # 尝试刷新任务列表
                    continue
            
            if any(re.match(模式, 任务名称) for 模式 in ['浏览.*s']):
                _json = {'taskId': 任务_id, 'taskType': 任务类型, 'btd': btd}
                if self.任务提交准备(_json):
                    self.我的打印(f'等待16秒')
                    for i in range(16):  # 直接等待16秒
                        time.sleep(1)  # 每秒一次反馈
                        self.我的打印(f'剩余等待时间：{16 - i}秒')
                    _json = {'taskId': 任务_id, 'taskType': str(任务类型),
                             'activityType': None, 'activityId': None,
                             'taskSetId': None, 'venueCode': None,
                             'venueUnitStyle': None, 'taskScene': None,
                             'btd': btd}
                    self.提交任务完成状态(_json)  # 提交完成状态
                    self.领取任务奖励(分类, 任务_id, 任务类型)  # 领取奖励
                    continue

            if any(re.match(模式, 任务名称) for 模式 in ['.*晒图.*']):
                _json = {'taskId': 任务_id, 'taskType': 任务类型}
                if self.任务提交准备(_json):
                    self.我的打印(f'等待16秒')
                    time.sleep(16)
                    _json = {
                        'taskId': 任务_id,
                        'taskType': 任务类型,
                        'activityType': None,
                        'activityId': None,
                        'taskSetId': None,
                        'venueCode': None,
                        'venueUnitStyle': None,
                        'taskScene': None
                    }
                    self.提交任务完成状态(_json)  
                    self.领取任务奖励(分类, 任务_id, 任务类型)
                    continue

            # 完成五次浇灌的任务
            if 任务名称 == '完成五次浇灌':
                count = 任务字典.get('total') - 任务字典.get('curStep')  # 还需要浇水的次数=要浇水的次数-以浇水的次数
                if self.获取水滴数量() < (count * self.浇水克数):
                    self.我的打印(f'当前水滴不足以完成任务，跳过')
                    continue
                for _ in range(count):
                    time.sleep(0.5)
                    if not self.浇水():  
                        break
                else:
                    _json = {'taskId': 任务字典['taskId'], 'taskType': str(任务字典['taskType'])}
                    if self.提交任务完成状态(_json):
                        self.领取任务奖励(分类, 任务_id, 任务类型)  # 领取奖励
                        continue

            if any(re.match(模式, 任务名称) for 模式 in ['.*专场', '.*水滴大放送']):
                if self.任务获取(任务_id, 任务类型):
                    _json = {'taskId': 任务_id, 'taskType': 16}
                    if self.任务提交准备(_json):
                        self.我的打印(f'等待16秒')
                        time.sleep(16)
                        _json = {'taskId': 任务_id, 'taskType': str(任务类型)}
                        self.提交任务完成状态(_json)  
                        self.领取任务奖励(分类, 任务_id, 任务类型)
                        continue

            self.我的打印(f'该任务暂时无法处理，请提交日志给作者！ {任务字典}')

    # 执行累计任务
    def 执行累计任务(self):
        self.获取任务列表()  # 刷新任务列表
        for 任务 in self.累计任务列表:
            if 任务.get('status') == 1:
                self.我的打印(f'开始领取累计任务数达{任务.get("condition")}个的奖励')
                self.领取累计任务奖励(任务.get('condition'))
                time.sleep(1)

    # 水滴投资
    def 水滴投资(self):
        url = 'https://app.dewu.com/hacking-tree/v1/invest/info'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('data').get('isToday') is False:  # 可领取
            self.领取水滴投资()
        else:
            self.我的打印('今日已领取过水滴投资奖励了')
        time.sleep(2)
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('data').get('triggered') is True:  # 可投资
            url = 'https://app.dewu.com/hacking-tree/v1/invest/commit'
            响应 = self.重试请求(self.session.post, url, headers=self.headers)
            响应字典 = 响应.json()
            if 响应字典.get('code') == 200 and 响应字典.get('status') == 200:
                self.我的打印('水滴投资成功，水滴-100g')
                return
            if 响应字典.get("msg") == '水滴不够了':
                self.我的打印(f'水滴投资失败，剩余水滴需超过100g，{响应字典.get("msg")}')
                return
            self.我的打印(f'水滴投资出错！ {响应字典}')
            return
        else:
            self.我的打印('今日已经水滴投资过了！')

    # 领取水滴投资
    def 领取水滴投资(self):
        url = 'https://app.dewu.com/hacking-tree/v1/invest/receive'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        利润 = 响应字典.get('data').get('profit')
        self.我的打印(f"领取水滴投资成功! 获得{利润}g水滴")

    # 获取助力码
    def 获取分享码(self) -> str:
        url = 'https://app.dewu.com/hacking-tree/v1/keyword/gen'
        响应 = self.重试请求(self.session.post, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('status') == 200:
            关键字 = 响应字典.get('data').get('keyword')
            关键字 = re.findall('œ(.*?)œ ', 关键字)
            if 关键字:
                self.我的打印(f'获取助力码成功 {关键字[0]}')
                return 关键字[0]
        self.我的打印(f'获取助力码失败！ {响应字典}')

    # 助力
    def 助力用户(self):
        if config.助力信号 == 'False':
            self.我的打印('助力功能已设置为关闭')
            return
        url = 'https://app.dewu.com/hacking-tree/v1/user/init'
        if self.索引 == 0:
            for 分享码 in config.分享码列表:
                _json = {'keyword': 分享码}
                响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
                响应字典 = 响应.json()
                数据 = 响应字典.get('data')
                if not 数据:
                    continue
                邀请结果 = 数据.get('inviteRes')
                if any(re.match(模式, 邀请结果) for 模式 in ['助力成功', '助力失败，今日已助力过了']):
                    self.我的打印(f'开始助力 {分享码}', end=' ')
                    self.我的打印(邀请结果)
                    return
                time.sleep(random.randint(20, 30) / 10)
        for 分享码 in config.分享码列表:
            self.我的打印(f'开始助力 {分享码}', end=' ')
            _json = {'keyword': 分享码}
            响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
            响应字典 = 响应.json()
            数据 = 响应字典.get('data')
            if not 数据:
                self.我的打印(f'助力异常 {响应字典}')
                continue
            邀请结果 = 数据.get('inviteRes')
            self.我的打印(邀请结果)
            if any(re.match(模式, 邀请结果) for 模式 in ['助力成功', '助力失败，今日已助力过了']):
                return
            time.sleep(random.randint(20, 30) / 10)
        return

    # 领取助力奖励
    def 领取助力奖励(self):
        url = 'https://app.dewu.com/hacking-tree/v1/invite/list'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('status') == 200:
            奖励列表 = 响应字典.get('data').get('list')
            if not 奖励列表:
                return
            for 奖励 in 奖励列表:
                if 奖励.get('status') != 0:  # 为0时才可以领取
                    continue
                被邀请用户ID = 奖励.get('inviteeUserId')
                url = 'https://app.dewu.com/hacking-tree/v1/invite/reward'
                _json = {'inviteeUserId': 被邀请用户ID}
                响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
                响应字典 = 响应.json()
                if 响应字典.get('status') == 200:
                    水滴 = 响应字典.get('data').get('droplet')
                    self.我的打印(f'获得{水滴}g水滴')
                    continue
                self.我的打印(f'领取助力奖励出现未知错误！ {响应字典}')
            return
        self.我的打印(f'获取助力列表出现未知错误！ {响应字典}')
        return

    # 领取合种上线奖励
    def 领取合种上线奖励(self):
        url = f'https://app.dewu.com/hacking-tree/v1/team/sign/list?teamTreeId={self.tree_id}'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('data') is None:
            return
        奖励列表 = 响应字典.get('data', {}).get('list')
        if not 奖励列表:
            return
        for 奖励 in 奖励列表:
            if 奖励.get('isComplete') is True and 奖励.get('isReceive') is False:  # 如果任务完成但是未领取
                url = 'https://app.dewu.com/hacking-tree/v1/team/sign/receive'
                _json = {"teamTreeId": self.tree_id, "day": 奖励.get('day')}
                响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
                响应字典 = 响应.json()
                if 响应字典.get('data').get('isOk') is True:
                    self.我的打印(f'获得{奖励.get("num")}g水滴')
                    continue
                self.我的打印(f'领取合种上线奖励出现未知错误！ {响应字典}')
        return

    def 领取任务奖励(self, 分类, 任务_id, 任务类型):
        url = 'https://app.dewu.com/hacking-tree/v1/task/receive'
        _json = {'classify': 分类, 'taskId': 任务_id, 'taskType': 任务类型}
        
        # 打印请求参数
        self.我的打印(f"领取任务奖励请求参数: {_json}")
        
        响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
        响应字典 = 响应.json()
        
        # 打印返回的完整信息
        self.我的打印(f"领取任务奖励请求返回: {响应字典}")
        
        if 响应字典.get('code') != 200:
            self.我的打印(f"领取任务奖励失败! {响应字典}")
            return
        
        self.我的打印(f"领取任务奖励成功! 获得{响应字典.get('data').get('num')}g水滴")

    # 领取空中水滴
    def 领取空中水滴(self):
        for _ in range(2):
            url = 'https://app.dewu.com/hacking-tree/v1/droplet/air_drop_receive'
            _json = {"clickCount": 20, "time": int(time.time())}
            响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
            响应字典 = 响应.json()
            数据 = 响应字典.get('data')
            if 数据 is not None and 数据.get('isOk') is True:
                self.我的打印(f'获得{响应字典.get("data").get("droplet")}g水滴')
                time.sleep(1)
                continue
            break

    # 点击8个商品获得水滴
    def 点击产品(self):
        产品列表 = [
            {"spuId": 3030863, "timestamp": 1690790735382, "sign": "2889b16b3077c5719288d105a14ffa1e"},
            {"spuId": 4673547, "timestamp": 1690790691956, "sign": "cc3cc95253d29a03fc6e79bfe2200143"},
            {"spuId": 1502607, "timestamp": 1690791565022, "sign": "04951eac012785ccb2600703a92c037b"},
            {"spuId": 2960612, "timestamp": 1690791593097, "sign": "fb667d45bc3950a7beb6e3fa0fc05089"},
            {"spuId": 3143593, "timestamp": 1690791613243, "sign": "82b9fda61be79f7b8833087508d6abe2"},
            {"spuId": 3067054, "timestamp": 1690791639606, "sign": "2808f3c7cf2ededea17d3f70a2dc565d"},
            {"spuId": 4448037, "timestamp": 1690791663078, "sign": "335bc519ee9183c086beb009adf93738"},
            {"spuId": 3237561, "timestamp": 1690791692553, "sign": "5c113b9203a510b7068b3cd0f6b7c25e"},
            {"spuId": 3938180, "timestamp": 1690792014889, "sign": "3841c0272443dcbbab0bcb21c94c6262"}
        ]
        for 产品 in 产品列表:
            url = 'https://app.dewu.com/hacking-tree/v1/product/spu'
            _json = 产品
            响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
            响应字典 = 响应.json()
            if 响应字典.get('data') is None:
                self.我的打印(f'今天已经完成过该任务了！')
                return
            if 响应字典.get('data', {}).get('isReceived') is True:
                self.我的打印(f'获得{响应字典.get("data").get("dropLetReward")}g水滴')
                return
            time.sleep(1)

    # 领取发现水滴
    def 领取发现水滴(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/product/task/seek-receive'
            _json = {"sign": "9888433e6d10b514e5b5be4305d123f0", "timestamp": int(time.time() * 1000)}
            响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
            响应字典 = 响应.json()
            self.我的打印(响应字典)

    # 领取品牌特惠奖励
    def 领取品牌特惠奖励(self):
        开始时间 = time.time()  # 记录开始时间
        持续时间 = 60  # 持续 1 分钟
        
        while True:
            # 检查是否超过 1 分钟
            if time.time() - 开始时间 > 持续时间:
                self.我的打印('已持续运行 1 分钟，结束领取品牌特惠奖励。')
                break

            url = 'https://app.dewu.com/hacking-ad/v1/activity/list?bizId=tree'
            响应 = self.重试请求(self.session.get, url, headers=self.headers)
            响应字典 = 响应.json()
            
            # 检查请求的响应状态
            if 响应字典.get('code') != 200:
                self.我的打印(f'请求失败，状态码: {响应字典.get("code")}, 信息: {响应字典.get("msg")}')
                return

            if 响应字典.get('data') is None:
                self.我的打印('当前没有可以完成的任务！')
                return

            广告列表 = 响应字典.get('data').get('list')

            if 广告列表 is None or len(广告列表) == 0:
                self.我的打印('当前没有可以完成的任务！')
                return

            for 广告 in 广告列表:
                if 广告.get('isReceived') is True:
                    continue
                aid = 广告.get('id')
                url = 'https://app.dewu.com/hacking-ad/v1/activity/receive'
                _json = {"bizId": "tree", "aid": aid}
                响应 = self.重试请求(self.session.post, url, headers=self.headers, json=_json)
                响应字典 = 响应.json()
                
                # 处理返回的状态
                if 响应字典.get('status') != 200:
                    # 针对具体的错误码进行处理
                    if 响应字典.get('code') == 713002003:
                        self.我的打印('领取奖励失败，因为活动 ID 无效。请检查活动是否仍然有效。')
                    else:
                        self.我的打印('领取奖励出现未知错误！', end=' ')
                        self.我的打印(f'错误详情: {响应字典}')
                    continue
                
                水滴奖励 = 响应字典.get("data")
                if 水滴奖励 is not None:
                    if 水滴奖励.get("award") >= 100:
                        self.我的打印(f'获得{水滴奖励.get("award")}g水滴，已达到领取条件。')
                        # 在这里可以添加领取奖励的逻辑
                    else:
                        self.我的打印(f'获得{水滴奖励.get("award")}g水滴，但未达到领取条件。')
                else:
                    self.我的打印('领取奖励时返回的数据无效。')

            # 每两秒刷新一次
            time.sleep(2)

    # 获取种树进度
    def 获取种树进度(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_tree_info'
        响应 = self.重试请求(self.session.get, url, headers=self.headers)
        响应字典 = 响应.json()
        if 响应字典.get('code') != 200:
            self.我的打印(f"获取种树进度失败! {响应字典}")
            return
        self.tree_id = 响应字典.get('data').get('treeId')
        等级 = 响应字典.get('data').get('level')
        当前等级所需浇水水滴 = 响应字典.get('data').get('currentLevelNeedWateringDroplet')
        用户浇水水滴 = 响应字典.get('data').get('userWateringDroplet')
        self.我的打印(f"种树进度: {等级}级 {用户浇水水滴}/{当前等级所需浇水水滴}")

    def 主函数(self):
        字符 = '★★'
        名称, 等级 = self.树的信息()
        水滴数量 = self.获取水滴数量()
        if not (名称 and 等级 and 水滴数量):
            self.我的打印("请求数据异常！")
            return
        self.我的打印(f'目标：{名称}')
        self.我的打印(f'剩余水滴：{水滴数量}')
        self.判断是否是团队树()  # 判断是否是团队树
        self.获取种树进度()  # 获取种树进度
        self.我的打印(f'{字符}开始签到')
        self.水滴签到()  # 签到
        self.我的打印(f'{字符}开始领取气泡水滴')
        self.领取气泡水滴()
        self.我的打印(f'{字符}开始完成每日任务')
        self.执行任务()
        self.我的打印(f'{字符}开始领取累计任务奖励')
        self.执行累计任务()
        self.我的打印(f'{字符}开始领取木桶水滴')
        self.判断木桶水滴()
        self.我的打印(f'{字符}开始多次执行浇水，领取浇水奖励')
        self.执行领取浇水奖励()
        self.我的打印(f'{字符}开始浇水充满气泡水滴')
        self.浇水充满气泡水滴()
        self.我的打印(f'{字符}开始领取合种上线奖励')
        self.领取合种上线奖励()
        self.我的打印(f'{字符}开始领取空中水滴')
        self.领取空中水滴()
        self.我的打印(f'{字符}开始进行水滴投资')
        self.水滴投资()
        self.我的打印(f'{字符}开始点击8个商品获得水滴')
        self.点击产品()
        self.我的打印(f'{字符}开始领取品牌特惠奖励')
        self.领取品牌特惠奖励()
        self.我的打印(f'{字符}开始领取助力奖励')
        self.领取助力奖励()
        self.我的打印(f'{字符}开始领取等级奖励')
        self.领取等级奖励()
        self.我的打印(f'{字符}开始进行浇水直到少于{self.剩余克数}g')
        self.浇水直到少于()
        self.我的打印(f'剩余水滴：{self.获取水滴数量()}')
        time.sleep(1)
        self.获取种树进度()  # 获取种树进度


# 主程序
def 主函数():
    ck数量 = len(config.ck列表)
    if not ck数量:
        logging.error('没有获取到账号！')
        return

    for 索引, ck in enumerate(config.ck列表):
        logging.info(f'*****第{索引 + 1}个账号*****')
        得物(ck, 索引).主函数()
        logging.info('')

if __name__ == '__main__':
    asyncio.run(运行任务(得物环境))    
    主函数()
    sys.exit()