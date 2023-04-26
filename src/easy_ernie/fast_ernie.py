# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Generator
from ernie import Ernie

class FastErnie:
    def __init__(self, BAIDUID: str, BDUSS_BFESS: str):
        self.ernie = Ernie(BAIDUID, BDUSS_BFESS)
        self.sessionId = ''
        self.parentChatId = 0

    def askStream(self, question: str) -> Generator:
        if not self.sessionId:
            self.sessionId = self.ernie.newConversation(question)
        for item in self.ernie.askStream(question, self.sessionId, self.parentChatId):
            self.parentChatId = item.get('chatId')
            yield item

    def ask(self, question: str) -> dict:
        if not self.sessionId:
            self.sessionId = self.ernie.newConversation(question)
        data = self.ernie.ask(question, self.sessionId, self.parentChatId)
        self.parentChatId = data.get('chatId')
        return data
    
    def close(self) -> bool:
        if self.ernie.deleteConversation(self.sessionId):
            self.sessionId = ''
            self.parentChatId = 0
            return True
        return False