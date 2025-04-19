import random


class Competitor:
    username = "Outer Cloud"  # Change this!

    def __init__(self):
        self.state = "load_initial"
        # self.log = open('log.txt', 'w')
        # self.log.write('\n===========')

    def play_turn(self, controller):
        # self.log.write('\n' + self.state)

        for bot in range(3):
            if self.state == "load_initial" or self.state == "load_second":
                controller.load(bot)

            if self.state == "fire":
                target_bot = 0

                while controller.get_opponent_bot_health(target_bot) <= 0:
                    target_bot += 1

                    if target_bot == 2:
                        break

                controller.attack(bot, target_bot, 2)

        if self.state == "load_initial":
            self.state = "load_second"
        elif self.state == "load_second":
            self.state = "fire"
        elif self.state == "fire":
            self.state = "load_initial"

        