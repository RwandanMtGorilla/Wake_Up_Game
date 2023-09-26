from config import OPENAI_API_KEY,OPENAI_API_BASE
import pandas as pd
import openai
import re
import csv
import random
import json
import ast

# 初始化OpenAI客户端
openai.api_key = OPENAI_API_KEY
try:
    openai.api_base = OPENAI_API_BASE
except NameError:
    print("OPENAI_API_BASE is not defined, using default value.")

# 定义文件名变量

MAX_RETRIES = 3
def call_openai_api(sys_prompt,prompt):
    for retry in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",  # gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4000,
                temperature=0.5,
                timeout=20  # 设置超时时间为60秒
            )
            return response
        except Exception as e:
            if retry < MAX_RETRIES - 1:  # 如果不是最后一次重试，打印错误并继续
                print(f"Error on retry {retry + 1}: {e}. Retrying...")
            else:  # 如果是最后一次重试，抛出异常
                print(f"Max retries reached. Error: {e}")
                raise



def roll_dice():
    return random.randint(0, 50)+random.randint(0, 50)+50


def judge_turn():
    player1n = roll_dice()
    print(f"Player1 Rolled dice value: {player1n}\n")
    player2n = roll_dice()
    print(f"Player2 Rolled dice value: {player2n}\n")
    if player1n > player2n:
        print(f"Player1: \n")
        return 1
    elif player1n < player2n:
        print(f"Player2: \n")
        return 2
    else:
        print("It's a tie!\n")
        judge_turn()



def update_player_status(player1, player2, action_description, max_retries=3):
    retry_count = 0

    while retry_count < max_retries:
        sys_prompt = """
            根据以下的游戏描述，请为两名玩家更新状态。
            描述可能会提到玩家失去生命值、获得物品、更改地点等情况。
        """

        prompt = f"""
            请为以下游戏描述更新玩家状态：
            Player1 current status: {player1.__dict__}
            Player2 current status: {player2.__dict__}
            Description of recent action: '{action_description}'

            请更新并返回玩家的新状态。(请按照相同的格式回复Player1 current status以及Player2 current status,无需多余描述)
        """
        # ...

        response = call_openai_api(sys_prompt, prompt)

        if 'content' in response['choices'][0]['message']:
            updated_status = response['choices'][0]['message']['content']
        else:
            print(f"Unexpected response format from OpenAI API: {response}")
            retry_count += 1
            continue

        print(f"Updated status from API: \n{updated_status}")  # Add this line

        try:
            # Split the lines and filter the relevant ones containing status info
            lines = [line.strip() for line in updated_status.split("\n") if line.startswith("Player")]

            if len(lines) < 2:
                raise ValueError(f"Expected at least 2 lines but got {len(lines)}")

            # Only consider the last two lines
            lines = lines[-2:]

            # Extract status strings using regex
            pattern = re.compile(r"Player\d current status: (\{.*?\})")
            player1_status_str = pattern.search(lines[0]).group(1)
            player2_status_str = pattern.search(lines[1]).group(1)

            # Replace single quotes with double quotes for valid JSON parsing
            player1_status_str = player1_status_str.replace("'", '"')
            player2_status_str = player2_status_str.replace("'", '"')

            # Load the string as JSON
            player1_status = json.loads(player1_status_str)
            player2_status = json.loads(player2_status_str)

            # Update player status
            player1.__dict__.update(player1_status)
            player2.__dict__.update(player2_status)

            return player1, player2  # Exit the function successfully
        except Exception as e:
            print(f"Error updating player status: {e}")

            retry_count += 1

    return None, None  # Return None, None if all retries failed



def is_player_dead(player):
    return player.health <= 0




def get_action_difficulty(action, player1_status, player2_status):
    pattern = re.compile(r"-?\s*Analyse: (.*?)\s*-?\s*Criticize: (.*?)\s*-?\s*Difficulty:.*?(\d+)", re.DOTALL)
    # 创建一个提示，描述玩家的状态和他们想要执行的行动
    sys_prompt = f"""
        正在进行一场游戏，你作为裁判需要结合玩家的行动和双方玩家当前状态 根据现实中这个行动的难度以及这个行动对玩家多大程度有益，分析并判定一个1-100的难度值(作为参考 起床难度:3；抢劫武器店获得武器难度50；祈祷神明让自己直接获得胜利难度:100)
        你的回复应当始终按照以下格式返回结果：
        - Analyse: 思考行动玩家想要做什么，分析当前各玩家状态，并得出难度结论以及难度数值(如果玩家状态不满足行动需求，例如:不在同一地点时近战攻击另一位玩家；或没有物品时使用物品。将大幅增加难度)。
        - Criticize: 思考当前设置难度值的不足之处，并给出批评。
        - Difficulty: 必须是纯数字(例如:30)。
            """
    prompt = f"""
        正在进行一场游戏，你作为裁判需要结合玩家的行动和双方玩家当前状态 根据现实中这个行动的难度以及这个行动对玩家多大程度有益，分析并判定一个1-100的难度值(作为参考 起床难度:3；抢劫武器店获得武器难度50；祈祷神明让自己直接获得胜利难度:100)
        Player1 status: {player1_status}
        Player2 status: {player2_status}
        Player action: '{action}'
        
        你的回复应当始终按照以下格式返回结果：
        - Analyse: 思考行动玩家想要做什么，分析当前各玩家状态，并得出难度结论以及难度数值。
        - Criticize: 思考当前设置难度值的不足之处，并给出批评。
        - Difficulty: 必须是纯数字(例如:30)。
        """
    # 调用API
    response = call_openai_api(sys_prompt,prompt)

    if 'content' in response['choices'][0]['message']:
        generated_text = response['choices'][0]['message']['content']
    else:
        print(f"Unexpected response format from OpenAI API: {response}")
        return 50

    match = pattern.search(generated_text)
    if match:
        print(f"Successfully generated text:\n{generated_text}")
        Analyse = match.group(1).strip()
        criticize = match.group(2).strip()
        difficulty = int(match.group(3))

    else:
        print(f"An error occurred while parsing the generated text:\n{generated_text}")
        return 120

    return difficulty


def generate_action_description(action, difficulty, dice_value, player1_status, player2_status):
    sys_prompt = """
        你正在为一场游戏生成生动的描述。基于玩家的行动、难度和掷骰子的结果，请描述接下来会发生什么。
        提示：骰子值越高，行动越成功，效果越强，并可能会有额外增益。反之，则可能发生意外或效果减弱。(如果是攻击，请估算伤害点数)
    """
    action_outcome = "行动成功" if dice_value > difficulty else "行动失败"

    prompt = f"""
        请为以下游戏情境生成描述：
        Player1 status: {player1_status}
        Player2 status: {player2_status}
        Player action: '{action}'
        Difficulty needed: {difficulty}
        Dice rolled: {dice_value}
        Action Outcome: {action_outcome}

        根据上述情境，简要描述故事中本回合将发生的情况。
    """

    response = call_openai_api(sys_prompt, prompt)

    if 'content' in response['choices'][0]['message']:
        generated_text = response['choices'][0]['message']['content']
    else:
        print(f"Unexpected response format from OpenAI API: {response}")
        return "An error occurred."

    return generated_text.strip()

#



