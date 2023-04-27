![Release](https://img.shields.io/badge/Release-0.1.3-blue)
---
## 介绍
简洁的调用文心一言的WebAPI
## 需求
1. 语言: Python3.8+.
2. 包: requests.
3. 其他: 文心一言账户.
## 安装
pip3 install easy-ernie
## Cookie
![图片1](https://s1.ax1x.com/2023/04/26/p9KDUYR.md.png)
1. 访问[文心一言](https://yiyan.baidu.com).
2. 打开开发者工具.
3. 找到应用程序(Application).
4. 在左侧点击存储(Storage)-Cookies-https://yiyan.baidu.com.
5. 在列表中点击BAIDUID.
6. 复制下方Cookie Value的值.
7. BDUSS_BFESS同理.
## 使用
```python
from easy_ernie import FastErnie

if __name__ == '__main__':
    fastErnie = FastErnie('BAIDUID', 'BDUSS_BFESS')
    print(fastErnie.ask('你好'))
```
更多方法查看[Wiki](https://github.com/XiaoXinYo/Easy-Ernie/wiki).
## Acs-Token
由于文心一言的Acs-Token算法中的参数不定时的变化,所以包里调用了API.感兴趣的可以联系我.
## 感谢
灵感来源自[acheong08](https://github.com/acheong08),[ls233](https://github.com/lss233).