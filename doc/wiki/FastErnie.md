## askStream
```python
def askStream(self, question: str) -> Generator
```
1. 功能: 流提问.
2. 返回示例:
```python
{'answer': '我画好了，欢迎对我提出反馈和建议，帮助我快速进步。', 'urls': ['http://eb118-file.cdn.bcebos.com/upload/F09A18443610CE467F76C5F67E4340B0?x-bce-process=style/wm_ai'], 'chatId': '78059153', 'done': False}

{'answer': '\n', 'urls': [], 'chatId': '78059153', 'done': False}

{'answer': '你可以完整描述你的需求来继续作画，如：“帮我画一枝晶莹剔透的牡丹花”。', 'urls': [], 'chatId': '78059153', 'done': False}

{'answer': '我画好了，欢迎对我提出反馈和建议，帮助我快速进步。\n你可以完整描述你的需求来继续作画，如：“帮我画一枝晶莹剔透的牡丹花”。', 'urls': ['http://eb118-file.cdn.bcebos.com/upload/F09A18443610CE467F76C5F67E4340B0?x-bce-process=style/wm_ai'], 'chatId': '78059153', 'done': True}
```
## ask
```python
def ask(self, question: str) -> dcit
```
1. 功能: 提问.
2. 返回示例:
```python
{'answer': '我画好了，欢迎对我提出反馈和建议，帮助我快速进步。\n你可以完整描述你的需求来继续作画，如：“帮我画一枝晶莹剔透的牡丹花”。', 'urls': ['http://eb118-file.cdn.bcebos.com/upload/F09A18443610CE467F76C5F67E4340B0?x-bce-process=style/wm_ai'], 'chatId': '78059153'}
```
## close
```python
close(self) -> bool
```
1. 功能: 关闭.
2. 返回示例:
```python
True
```