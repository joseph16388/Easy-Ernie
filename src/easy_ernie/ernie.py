from typing import Generator, Optional
import time
import requests
import re
import json

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
        data = requests.get(f'https://api.hack-er.cn/other/get_ernie_acs_token?BAIDUID={self.BAIDUID}',).json()
        return data['data']

    def checkJson(self, data: str) -> None:
        try:
            data = json.loads(data)
        except:
            raise Exception('请求失败,响应格式错误')

        if data['code'] != 0:
            raise Exception(f'请求失败,{data["msg"]}')

    def checkResponse(self) -> None:
        if self.response.status_code != 200:
            raise Exception('请求失败,检查网络')

        self.checkJson(self.response.text)

    def post(self, url: str, data: dict, stream=False, check=True) -> requests.Response:
        self.session.headers['Content-Length'] = str(len(data))
        self.response = self.session.post(url, json=data, stream=stream)
        if not stream and check:
            self.checkResponse()
        return self.response
    
    def getConversation(self) -> Optional[list]:
        data = self.post(
            f'https://yiyan.baidu.com/eb/session/list',
            {
                'deviceType': 'pc',
                'pageSize': 1000,
                'timestamp': getTimestamp()
            }
        ).json()
        return data['data']['sessions']

    def newConversation(self, sessionName: str) -> str:
        data = self.post(
            'https://yiyan.baidu.com/eb/session/new',
            {
                'deviceType': 'pc',
                'plugins': [],
                'sessionName': sessionName,
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

    def getConversationDetail(self, sessionId: str) -> Optional[dict]:
        conversations = self.getConversation()
        if not conversations:
            return None
        base = {}
        for conversation in conversations:
            if conversation['sessionId'] == sessionId:
                base = conversation
                break
        if not base:
            return None

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
        histories = []
        chats = sorted(chats.values(), key=lambda data: data['createTime'])
        for chat in chats:
            histories.append({
                'id': chat['id'],
                'role': chat['role'],
                'text': chat['message'][0]['content'],
                'createTime': chat['createTime'],
            })
        currentChatId = data['data']['currentChatId']
        return {
            'base': base,
            'histories': histories,
            'currentChatId': str(currentChatId) if currentChatId else '0'
        }

    def askStream(self, question: str, sessionId: str='', sessionName: str='', parentChatId: str='0') -> Generator:
        acsToken = self.getAcsToken()
        self.session.headers['Acs-Token'] = acsToken
        self.session.headers['Accept'] = 'text/event-stream, application/json'
        data = self.post(
            'https://yiyan.baidu.com/eb/chat/conversation/v2',
            {
                'code': 0,
                'deviceType': 'pc',
                'jt': '',
                'msg': '',
                'parentChatId': parentChatId,
                'pluginInfo': [],
                'plugins': [],
                'sessionId': sessionId,
                'sessionName': sessionName,
                'sign': acsToken,
                'text': question,
                'timestamp': getTimestamp(),
                'type': 10
            },
            stream=True,
            check=False
        )

        imagePattern = r'<img[^>]*\ssrc=[\'"]([^\'"]+)[\'"][^>]*\s/>'
        for line in data.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')
            if line.startswith('event:'):
                event = line[6:]
                continue
            elif not line.startswith('data:'):
                self.checkJson(line)

            data = line[5:]
            self.checkJson(data)
            data = json.loads(data)
            data = data['data']
            if event == 'major':
                sessionId = data['createSessionResponseVoCommonResult']['data']['sessionId']
                botChatId = data['createChatResponseVoCommonResult']['data']['botChat']['id']
            elif event == 'message':
                done = data['is_end']
                if done == 0:
                    answer = data['content']
                    urls = re.findall(imagePattern, answer)
                    answer = re.sub(imagePattern, '', answer)
                    answer = answer.replace('<br>', '\n')
                    yield {
                        'answer': answer,
                        'urls': urls,
                        'sessionId': sessionId,
                        'botChatId': botChatId,
                        'done': False
                    }
                else:
                    answer = data['tokens_all']
                    urls = re.findall(imagePattern, answer)
                    answer = re.sub(imagePattern, '', answer)
                    answer = answer.replace('<br>', '\n')
                    answer = answer.strip()
                    yield {
                        'answer': answer,
                        'urls': urls,
                        'sessionId': sessionId,
                        'botChatId': botChatId,
                        'done': True
                    }

    def ask(self, question: str, sessionId: str='', sessionName: str='', parentChatId: str='0') -> dict:
        result = {}
        for data in self.askStream(question, sessionId, sessionName, parentChatId):
            result = data
        del result['done']
        return result