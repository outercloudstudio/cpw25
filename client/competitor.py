import random

def argmax(v, max_val=999999):
    i = 0
    max = -9999999
    for j in range(len(v)):
        if v[j] > max and v[j] <= max_val:
            i = j
            max = v[j]
    return i

def argmin(v, min_val=0):
    i = 0
    min = 9999999
    for j in range(len(v)):
        if v[j] < min and v[j] >= min_val:
            i = j
            min = v[j]
    return i

class Competitor:
    username = "aREALp1n3c0n3!1" # Change this!

    def __init__(self):
        # initialize a counter for the round number
        self.round_number = 0
        self.shield_rounds = [-999, -999, -999]

    def play_turn(self, controller):
        self.round_number += 1

        team_health = [controller.get_my_bot_health(i) for i in range(3)]
        op_health = [controller.get_opponent_bot_health(i) for i in range(3)]
        op_shield = [controller.get_opponent_previous_action(i)["type"] == "shield" for i in range(3)]
        for i in range(3):
            if op_shield[i] and op_health[i] > 0:
                self.shield_rounds[i] = self.round_number - 1
            if self.round_number - self.shield_rounds[i] <= 2:
                op_health[i] += controller.SHIELD_HEALTH # Effective health for frequent shielders

        max_team_health_bot = argmax(team_health)
        for bot in range(3):
            op_ammo = [controller.get_opponent_bot_ammo(i) for i in range(3)]
            max_ammo = max(op_ammo)

            cur_health = controller.get_my_bot_health(bot)
            if max_ammo >= 1 and cur_health < controller.INITIAL_HEALTH and max_team_health_bot != bot:
                controller.shield(bot)
                continue

            min_health_bot = argmin(op_health, 1)
            min_health = op_health[min_health_bot]
            min_health_shield = (self.round_number - self.shield_rounds[min_health_bot]) <= 3

            my_ammo = controller.get_my_bot_ammo(bot)
            no_ammo = my_ammo == 0
            low_ammo = my_ammo < 2
            easy_target = min_health == 1 and not min_health_shield
            if no_ammo or (not easy_target and low_ammo):
                controller.load(bot)
            else:
                attack_ammount = min(my_ammo, min_health)
                controller.attack(bot, min_health_bot, attack_ammount)
                op_health[min_health_bot] -= attack_ammount
