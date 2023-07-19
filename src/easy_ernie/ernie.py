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
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Acs-Token': '',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Content-Type': 'application/json',
            'Cookie': f'BDUSS_BFESS={BDUSS_BFESS};',
            'Host': 'yiyan.baidu.com',
            'Origin': 'https://yiyan.baidu.com',
            'Referer': 'https://yiyan.baidu.com/',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
        }
    
    def getAcsToken(self) -> str:
        data = requests.get(f'https://api.hack-er.cn/ernie/acs_token?BAIDUID={self.BAIDUID}',).json()
        return data['data']
    
    def checkRequest(self) -> None:
        if self.request.status_code != 200:
            raise Exception('请求失败,检查网络')
        
        try:
            data = self.request.json()
        except:
            raise Exception('请求失败,响应格式错误')
        
        if data['code'] != 0:
            raise Exception(f'请求失败,{data["msg"]}')

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
                'deviceType': 'pc',
                'pageSize': 1000,
                'timestamp': getTimestamp()
            }
        ).json()
        return data['data']['sessions']

    def newConversation(self, name: str) -> str:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'deviceType': 'pc',
                'plugins': [],
                'sessionName': name,
                'timestamp': getTimestamp()
            }
        ).json()
        return data['data']['sessionId']
    
    def deleteConversation(self, sessionId: str) -> bool:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/delete',
            {
                'deviceType': 'pc',
                'sessionId': sessionId,
                'timestamp': getTimestamp()
            },
            check=False
        ).json()
        return True if data['code'] == 0 else False

    def renameConversation(self, sessionId: str, name: str) -> bool:
        self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'deviceType': 'pc',
                'sessionId': sessionId,
                'sessionName': name,
                'timestamp': getTimestamp()
            }
        )
        return True
    
    def getConversationHistory(self, sessionId: str) -> Union[None, dict]:
        data = self.post(
            'https://yiyan.baidu.com/eb/chat/history',
            {
                'deviceType': 'pc',
                'pageSize': 2000,
                'sessionId': sessionId,
                'timestamp': getTimestamp(),
            }
        ).json()
        chats = data['data']['chats']
        if not chats:
            return None
        histories = []
        for chat in chats.values():
            histories.append({
                'id': chat['id'],
                'role': chat['role'],
                'text': chat['message'][0]['content']
            })
        return {
            'histories': histories,
            'currentChatId': str(data['data']['currentChatId'])
        }

    def askStream(self, question: str, sessionId: str, parentChatId: str) -> Generator:
        self.post(
            'https://yiyan.baidu.com/eb/chat/checkAndBan',
            {
                'deviceType': 'pc',
                'text': question,
                'timestamp': getTimestamp(),
            }
        )

        acsToken = self.getAcsToken()
        self.session.headers['Acs-Token'] = acsToken
        data = self.post(
            'https://yiyan.baidu.com/eb/chat/new',
            {
                'code': 0,
                'deviceType': 'pc',
                'jt': '',
                'msg': '',
                'parentChatId': parentChatId,
                'pluginInfo': [],
                'plugins': [],
                'sessionId': sessionId,
                'sign': acsToken,
                'text': question,
                'timestamp': getTimestamp(),
                'type': 10
            }
        ).json()
        botChatId = data['data']['botChat']['id']
        botParentChatId = data['data']['botChat']['parent']

        imagePattern = r'<img[^>]*\ssrc=[\'"]([^\'"]+)[\'"][^>]*\s/>'
        sentenceId = 0
        stop = 0
        while True:
            acsToken = self.getAcsToken()
            self.session.headers['Acs-Token'] = acsToken
            data = self.post(
                'https://yiyan.baidu.com/eb/chat/query',
                {
                    'chatId': botChatId,
                    'deviceType': 'pc',
                    'parentChatId': botParentChatId,
                    'sentenceId': sentenceId,
                    'sessionId': sessionId,
                    'sign': acsToken,
                    'stop': stop,
                    'timestamp': getTimestamp(),
                }
            ).json()

            data = data['data']
            sentenceId = data['sent_id']
            stop = data['stop']
            answer = data['content']
            if answer.strip():
                answer = re.sub(imagePattern, '', answer)
                answer = answer.replace('<br>', '\n')
                answer = answer.strip()
                yield {
                    'answer': answer,
                    'urls': re.findall(imagePattern, data['content']),
                    'botChatId': botChatId,
                    'done': False
                }

            if data['is_end'] == 1:
                break

        fullAnswer = data['tokens_all']
        fullAnswer = re.sub(imagePattern, '', fullAnswer)
        fullAnswer = fullAnswer.replace('<br>', '\n')
        fullAnswer = fullAnswer.strip()
        yield {
            'answer': fullAnswer,
            'urls': re.findall(imagePattern, fullAnswer),
            'botChatId': botChatId,
            'done': True
        }

    def ask(self, question: str, sessionId: str='', parentChatId: str='') -> dict:
        result = {}
        for data in self.askStream(question, sessionId, parentChatId):
            result = data
        del result['done']
        return result