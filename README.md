# 起床游戏

一个基于Python和OpenAI GPT的创意小游戏，模拟了线下小学生玩的无厘头游戏“起床”。在这个游戏中，玩家通过描述行动，并通过GPT来判断行动的难度并执行。每一回合的行动结果都会影响游戏的进程，直到一方玩家阵亡为止。

## 安装

确保你已经安装了以下Python库：

- pandas
- openai
- re
- csv
- random
- json
- ast

如果你没有安装，可以通过以下命令进行安装:

```bash
pip install pandas openai
```

## 配置
创建一个名为 config.py 的文件，并添加以下内容，用你的OpenAI API的密钥替换 your_openai_api_key_here：

```python
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_API_BASE = "https://api.openai.com"  # 如果有自定义的API基地址，否则不用填写
```

## 运行
在配置好所有依赖库和API密钥后，你可以通过运行 main.py 来启动游戏。

```bash
python main.py
```

## 许可
该项目采用MIT许可证。有关详细信息，请参见LICENSE文件。

## Todo
- 问题1：api不稳定 偶有握手错误
Error on retry 1: HTTP code 524 from API 详见第四次测试
- 问题2：GPT结算方式有问题 
偶尔错误更新状态（语义理解有误）//影响小 用新处理模式解决？
易出现返回格式错误问题 (问题较大 容易导致游戏中断 或许使用重试机制解决)
GPT常把骰子掷出点数作为伤害值 这并不合理
- 问题3：GPT生成内容有时并不有趣
可能的解决方法：
inworld.ai GameMaster角色创建 https://docs.inworld.ai/docs/tutorial-basics/core-description/ 
工具 inky https://indienova.com/indie-game-development/writing-interactive-fiction-with-inky/ 
选择：RPG的终极玩法 https://mp.weixin.qq.com/s/X3vcol3V5DOXaKeeu5ppUA 
来自Bita的好主意：改组为卡牌游戏


