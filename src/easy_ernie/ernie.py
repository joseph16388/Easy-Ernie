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
        self.BDUSS_BFESS = BDUSS_BFESS
        self.header = {
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
            'Cookie': f'BDUSS_BFESS={self.BDUSS_BFESS};'
        }
    
    def getSign(self) -> str:
        data = requests.get(f'https://api.hack-er.cn/ernie/acs_token?BAIDUID={self.BAIDUID}',).json()
        return data.get('data')
    
    def checkRequest(self) -> None:
        if self.request.status_code != 200:
            raise Exception('请求失败,请检查网络')
        
        try:
            self.request.json()
        except:
            raise Exception('请求失败,响应格式错误')
        
        if self.request.json().get('msg') == '请先登录':
            raise Exception('请求失败,请先登录')
        elif self.request.json().get('msg') == '用户访问被限制':
            raise Exception('请求失败,用户访问被限制')

    def get(self, url: str) -> requests:
        self.request = requests.get(url, headers=self.header)
        self.checkRequest()
        return self.request
    
    def post(self, url: str, data: dict) -> requests:
        self.header['Content-Length'] = str(len(data))
        self.request = requests.post(url, headers=self.header, json=data)
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
        return data.get('data').get('sessions')

    def newConversation(self, name: str) -> str:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'sessionName': name,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        ).json()
        return data.get('data').get('sessionId')
    
    def deleteConversation(self, sessionId: str) -> bool:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/delete',
            {
                'sessionId': sessionId,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        ).json()
        return True if data.get('code') == 0 else False

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
        return data.get('data').get('currentChatId')

    def askStream(self, question: str, sessionId: str, parentChatId: str) -> Generator:
        self.post(
            'https://yiyan.baidu.com/eb/chat/check',
            {
                'text': question,
                'timestamp': getTimestamp(),
                'deviceType': 'pc'
            }
        )

        sign = self.getSign()
        self.header['Acs-Token'] = sign
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
                'sign': sign
            }
        ).json()
        botChatId = data.get('data').get('botChat').get('id')
        botParentChatId = data.get('data').get('botChat').get('parent')

        fullAnswer = ''
        pattern = r'<img[^>]*\ssrc=[\'"]([^\'"]+)[\'"][^>]*\s/>'
        urls = []
        sentenceId = 0
        while True:
            sign = self.getSign()
            self.header['Acs-Token'] = sign
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
            data = data.get('data')
            sentenceId = data.get('sent_id')
            content = data.get('content')
            
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

            if data.get('stop') == 1 or data.get('is_end') == 1:
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
        for item in self.askStream(question, sessionId, parentChatId):
            result = item
        del result['done']
        return result