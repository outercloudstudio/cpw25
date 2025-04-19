import random

class Competitor:
    username = "changeme"  # Change this!

    def __init__(self):
        """
        Initialize your code. You can create set any initial values in here.
        """
        # Initialize a counter for the round number
        self.round_number = 0

    def play_turn(self, controller):
        """
        Runs the code for playing your team's turn. Don't change the name or params
        for this method!
        """
        self.round_number += 1

        for bot_id in range(3):
            my_ammo = controller.get_my_bot_ammo(bot_id)
            if my_ammo == 0:
                # Load one ammo
                controller.load(bot_id)
            else:
                # Attack with all of our ammo. More ammo does more damage
                attack_amount = my_ammo
                # Select a random enemy target
                target_id = random.randint(0, 2)
                # Attack!
                controller.attack(bot_id, target_id, attack_amount)

            # We can also shield. When should we do this?
            # controller.shield(bot_id)

        #
        # Check out "client/controller.py" for all available methods
        #
