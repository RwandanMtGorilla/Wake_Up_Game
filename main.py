
from GPTapi import call_openai_api,judge_turn,get_action_difficulty,generate_action_description,roll_dice,update_player_status,is_player_dead
import json


class Player:
    def __init__(self, name, health=100, location="Home", inventory=[], status="asleep"):
        self.name = name
        self.health = health
        self.location = location
        self.inventory = inventory
        self.status = status

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

def simulate_turn(player1, player2, action):
    # 1. 评估行动的难度
    difficulty = get_action_difficulty(action, player1.__dict__, player2.__dict__)
    print(f"Action Difficulty: {difficulty}\n")
    # 2. 生成随机数，模拟掷骰子
    dice_value = roll_dice()
    print(f"Rolled dice value: {dice_value}\n")
    # 3. 生成行动描述
    description = generate_action_description(action, difficulty, dice_value, player1.__dict__, player2.__dict__)
    print(f"Action Description:\n{description}\n")
    # 4. 更新玩家状态
    updated_player1, updated_player2 = update_player_status(player1, player2, description)
    # 输出更新后的玩家状态
    print("Updated Player1 Status:", updated_player1)
    print("Updated Player2 Status:", updated_player2)

def game_loop(player1, player2):

    while True:
        flag = judge_turn()
        if flag == 1:
            actor = "Player1"
        if flag == 2:
            actor = "Player2"

        action = f"{actor}: " + input(f"{actor}'s action: ")
        simulate_turn(player1, player2, action)

        if is_player_dead(player2):
            print(f"{player1.name} wins!")
            break
        if is_player_dead(player1):
            print(f"{player2.name} wins!")
            break



def start_game():
    player1 = Player(name="Player1", location="Player1 Home")
    player2 = Player(name="Player2", location="Player2 Home")

    game_loop(player1, player2)

    # 生成游戏总结
    # game_summary = call_openai_api("summarize game", [player1, player2])
    # print(game_summary)
if __name__ == "__main__":
    start_game()
