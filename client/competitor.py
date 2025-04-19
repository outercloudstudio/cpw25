import random

def get_bots_alive(controller):
    alive = 0

    for bot in range(3):
        if controller.get_my_bot_health(controller, bot):
            alive += 1

    return alive

def get_total_ammo(controller):
    ammo = 0

    for bot in range(3):
        if controller.get_my_bot_health(controller, bot) > 0:
            ammo += controller.get_my_bot_ammo(controller, bot)

    return ammo

def get_target(controller):
    target_bot = 0

    while controller.get_opponent_bot_health(target_bot) <= 0:
        target_bot += 1

        if target_bot == 2:
            break

class Competitor:
    username = "Mcafee Antiviru"  # Change this!

    def __init__(self):
        self.log = open('log.txt', 'w')
        self.log.write('\n===========')

    def play_turn(self, controller):
        try:
            ammo = get_total_ammo(controller)

            if ammo < 6:
                for bot in range(3):
                    controller.load(bot)
            else:
                target = get_target(controller)

                for bot in range(3):
                    controller.attack(bot, target, controller.get_my_bot_ammo(bot))
        except Exception as e:
            self.log.write('\n' + str(e))