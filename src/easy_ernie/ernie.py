# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Generator, Union
import time
import requests
import re

def getTimestamp():
    return int(time.time() * 1000)

class Ernie:
    def __init__(self, BAIDUID: str, BDUSS_BFESS: str):
        self.BAIDUID = BAIDUID
        self.session = requests.Session()
        self.session.headers = {
            'Host': 'yiyan.baidu.com',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
            'Content-Type': 'application/json',
            'Acs-Token': '',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
            'sec-ch-ua-platform': '"macOS"',
            'Accept': '*/*',
            'Origin': 'https://yiyan.baidu.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://yiyan.baidu.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cookie': f'BDUSS_BFESS={BDUSS_BFESS};'
        }
    
    def getSign(self) -> str:
        data = requests.get(f'https://api.hack-er.cn/ernie/acs_token?BAIDUID={self.BAIDUID}',).json()
        return data['data']
    
    def checkRequest(self) -> None:
        if self.request.status_code != 200:
            raise Exception('请求失败,请检查网络')
        
        try:
            self.request.json()
        except:
            raise Exception('请求失败,响应格式错误')
        
        if self.request.json()['code'] != 0:
            raise Exception(f'请求失败,{self.request.json()["msg"]}')

    def get(self, url: str, check=True) -> requests:
        self.request = self.session.get(url)
        if check:
            self.checkRequest()
        return self.request
    
    def post(self, url: str, data: dict, check=True) -> requests:
        self.session.headers['Content-Length'] = str(len(data))
        self.request = self.session.post(url, json=data)
        if check:
            self.checkRequest()
        return self.request
    
    def getConversation(self) -> Union[None, list]:
        data = self.post(
            f'https://yiyan.baidu.com/eb/session/list',
            {
                'pageSize': 1000,
                'deviceType': 'pc',
                'timestamp': getTimestamp()
            }
        ).json()
        return data['data']['sessions']

    def newConversation(self, name: str) -> str:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'sessionName': name,
                'timestamp': getTimestamp(),
                'deviceType': 'pc',
                'plugins': []
            }
        ).json()
        return data['data']['sessionId']
    
    def deleteConversation(self, sessionId: str) -> bool:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/delete',
            {
                'sessionId': sessionId,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            },
            False
        ).json()
        return True if data['code'] == 0 else False

    def renameConversation(self, sessionId: str, name: str) -> bool:
        self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'sessionId': sessionId,
                'sessionName': name,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        )
        return True
    
    def getParentChatId(self, sessionId: str) -> Union[None, str]:
        data = self.post(
            'https://yiyan.baidu.com/eb/chat/history',
            {
                'sessionId': sessionId,
                'pageSize': 2000,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        ).json()
        return data['data']['currentChatId']

    def askStream(self, question: str, sessionId: str, parentChatId: str) -> Generator:
        self.post(
            'https://yiyan.baidu.com/eb/chat/checkAndBan',
            {
                'text': question,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        )

        sign = self.getSign()
        self.session.headers['Acs-Token'] = sign
        data = self.post(
            'https://yiyan.baidu.com/eb/chat/new',
            {
                'sessionId': sessionId,
                'text': question,
                'parentChatId': parentChatId,
                'type': 10,
                'timestamp': getTimestamp(),
                'deviceType': 'pc',
                'code': 0,
                'msg': '',
                'jt': '',
                'sign': sign,
                'pluginInfo': [],
                'plugins': []
            }
        ).json()
        botChatId = data['data']['botChat']['id']
        botParentChatId = data['data']['botChat']['parent']

        fullAnswer = ''
        pattern = r'<img[^>]*\ssrc=[\'"]([^\'"]+)[\'"][^>]*\s/>'
        urls = []
        sentenceId = 0
        while True:
            sign = self.getSign()
            self.session.headers['Acs-Token'] = sign
            data = self.post(
                'https://yiyan.baidu.com/eb/chat/query',
                {
                    'chatId': botChatId,
                    'parentChatId': botParentChatId,
                    'sentenceId': sentenceId,
                    'sessionId': '',
                    'stop': 0,
                    'timestamp': getTimestamp(),
                    'deviceType': 'pc',
                    'sign': sign
                }
            ).json()
            data = data['data']
            sentenceId = data['sent_id']
            content = data['content']
            
            if content.strip():
                fullAnswer += content
                content = re.sub(pattern, '', content)
                content = content.replace('<br>', '\n')
                content = content.strip()

                yield {
                    'answer': content,
                    'urls': urls,
                    'sessionId': sessionId,
                    'botChatId': botChatId,
                    'done': False
                }

            if data['stop'] == 1 or data['is_end'] == 1:
                break
        
        urls.extend(re.findall(pattern, fullAnswer))
        fullAnswer = re.sub(pattern, '', fullAnswer)
        fullAnswer = fullAnswer.replace('<br>', '\n')
        fullAnswer = fullAnswer.strip()
        
        yield {
            'answer': fullAnswer,
            'urls': urls,
            'sessionId': sessionId,
            'botChatId': botChatId,
            'done': True
        }

    def ask(self, question: str, sessionId: str='', parentChatId: str='') -> dict:
        result = {}
        for data in self.askStream(question, sessionId, parentChatId):
            result = data
        del result['done']
        return result