import random
import time
import os
import sys
import cmd
import textwrap


## GAME HANDLING ##

def clear_screen():
    # Check if the operating system is Windows
    if os.name == 'nt':
        os.system('cls')  # Use 'cls' to clear the screen on Windows
    else:
        os.system('clear')  # Use 'clear' to clear the screen on Unix/Linux


screen_width = 100  # set screen width to 100


# function to display current character situation including location, health etc
def sitrep():
    zone_name = zonemap.get(myPlayer.location, {}).get(ZONENAME, "Unknown Zone")
    print("Location: " + zone_name + " | Health: " + str(myPlayer.hp) + " | Attack Points: " + str(myPlayer.ap))

    # Count the number of areas solved
    solved_count = sum(1 for solved in solved_places.values() if solved)
    print("Magic Points: " + str(
        myPlayer.mp) + " | Current Weapon: " + myPlayer.equipped_weapon + " | Areas Solved: " + str(solved_count))


##### PLAYER SETUP #####

class Player:
    def __init__(self):
        self.equipped_weapon = "None"  # Weapon Equipped
        self.weapons_inventory = []  # weapons on inventory
        self.special_item_inventory = []  # special items that are on players inventory
        self.special_item_available = ["lighthouse key", "gourda castle key", "restoring liquid"]
        self.name = ""  # player name
        self.hp = 0  # health points
        self.mp = 0  # magic points
        self.ap = 0  # attack points
        self.status_effect = []  # status effects
        self.job = ""  # player class type
        self.location = "c4"  # player starting location, updated based on player movement
        self.num_health_pots = 2  # number of health potions at game start, updates during game
        self.health_pot_heal_amount = 40  # amount health potions increase health points by
        self.gameover = False  # when true, game ends
        self.weapon_mult = 1  # weapon multiplier, updated when new weapon equipped


myPlayer = Player()


class Enemy:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack


##### TITLE SELECTIONS #####

def title_screen_selections():
    option = input("> ")
    if option.lower() == "play":
        start_game()  # starts the game
    elif option.lower() == "help":
        help_menu()  # help menu
    elif option.lower() == "quit":
        sys.exit()  # system exit game

    while option.lower() not in ["play", "help", "quit"]:
        print("Please enter a valid command.")
        option = input("> ")
        if option.lower() == "play":
            start_game()  # starts the game (second attempt)
        elif option.lower() == "help":
            help_menu()  # help menu (second attempt)
        elif option.lower() == "quit":
            sys.exit()  # system exit game (second attempt)


## TITLE SCREEN ##
def title_screen():
    clear_screen()
    print("#############################")
    print("# Welcome to Lithuin Island #")
    print("#############################")
    print("#         - Play -          #")
    print("#         - Help -          #")
    print("#         - Quit -          #")
    print("#############################")
    print("# Game Design - RainyGrinch #")
    print("#  Inspired by - BTONG.ME   #")
    print("#############################")
    title_screen_selections()  # prompt player to select option from title screen


## HELP MENU ##
def help_menu():
    print("#############################")
    print("# Welcome to Lithuin Island #")
    print("#############################")
    print("# Use up, down, left, right #")
    print("#   to move about the map   #")
    print("# type commands into the    #")
    print("# prompt to perform actions #")
    print("#   Use 'look' to inspect   #")
    print("# Good luck, and have fun   #")
    print("#############################")
    print("\n")
    print("Would you like to return to the main title screen, or exit? \n")
    exit_help = input("> ")
    if exit_help.lower() in ["exit", "quit", "leave"]:
        print("Now leaving the game, run the game again when you're ready...")
        sys.exit()
    elif exit_help.lower() in ["return", "play", "title", "title screen", "game"]:
        title_screen()
    else:
        print("Sorry, invalid selection, here's the Help Menu for you again")
        help_menu()


## MAP ##
"""
  A   B   C   D   E
+---+---+---+---+---+
|   |   |   |   |   |   1
+---+---+---+---+---+
|   |   |   |   |   |   2
+---+---+---+---+---+
|   |   |   |   |   |   3
+---+---+---+---+---+
|   |   |   |   |   |   4
+---+---+---+---+---+
|   |   |   |   |   |   5
+---+---+---+---+---+
|   |   |   |   |   |   6
+---+---+---+---+---+
|   |   |   |   |   |   7
+---+---+---+---+---+
"""

# Global Constants
ZONENAME = ""
DESCRIPTION = "description"
EXAMINATION = "examine"
SOLVED = False
ITEM = "item"
ENEMY = "enemy"
UP = "up", "north"
DOWN = "down", "south"
LEFT = "left", "west"
RIGHT = "right", "east"

# variables used to reset player attack or magic points to prevent weapon multiplier stacking
w_ap_reset = 50
w_mp_reset = 20
m_ap_reset = 30
m_mp_reset = 60
p_ap_reset = 20
p_mp_reset = 40

# variable for health points gained from "restoring liquid"
restore_liquid_amount = 70

# dictionary of places, as each is solved, dictionary updates and sitrep function produces updated figures
solved_places = {"a1": False, "b1": False, "c1": False, "d1": False, "e1": False,
                 "a2": False, "b2": False, "c2": False, "d2": False, "e2": False,
                 "a3": False, "b3": False, "c3": False, "d3": False, "e3": False,
                 "a4": False, "b4": False, "c4": False, "d4": False, "e4": False,
                 "a5": False, "b5": False, "c5": False, "d5": False, "e5": False,
                 "a6": False, "b6": False, "c6": False, "d6": False, "e6": False,
                 "a7": False, "b7": False, "c7": False, "d7": False, "e7": False,
                 }

zonemap = {
    "a1": {
        ZONENAME: "WASTELANDa1",
        DESCRIPTION: "It's strange, this land before you. There is no life, nothing to see, just wasteland...",
        EXAMINATION: "This strange wasteland holds no treasure, you'd better return to the main Island",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "",
        DOWN: "a2",
        LEFT: "",
        RIGHT: "b1",
    },
    "b1": {
        ZONENAME: "SEAb1",
        DESCRIPTION: "You're standing on the northern shore of the island, there are no boats or bridges.",
        EXAMINATION: "You hear waves crashing on the beach. There's nothing else to do here",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "",
        DOWN: "b2",
        LEFT: "a1",
        RIGHT: "c1",
    },
    "c1": {
        ZONENAME: "SEAc1",
        DESCRIPTION: "You're standing on the northern shore of the island, there are no boats or bridges.",
        EXAMINATION: "Like the rest of the northern shore, there's not much to be done here.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "",
        DOWN: "c2",
        LEFT: "b1",
        RIGHT: "d1",
    },
    "d1": {
        ZONENAME: "SEAd1",
        DESCRIPTION: "You're standing on the northern shore of the island, there are no boats or bridges.",
        EXAMINATION: "This northern shore has nothing for you to do here.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "",
        DOWN: "d2",
        LEFT: "c1",
        RIGHT: "e1",
    },
    "e1": {
        ZONENAME: "WASTELANDe1",
        DESCRIPTION: "It's strange, this land before you. There is no life, nothing to see, just wasteland...",
        EXAMINATION: "This is a wasteland, there's nothing here. Try heading inland.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "",
        DOWN: "e2",
        LEFT: "d1",
        RIGHT: "",
    },
    "a2": {
        ZONENAME: "SEAa2",
        DESCRIPTION: "You're standing on the western shore of the island, there are no boats or bridges.",
        EXAMINATION: "This western shore is nothing but sea and rocks. Head inland.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "a1",
        DOWN: "a3",
        LEFT: "",
        RIGHT: "b2",
    },
    "b2": {
        ZONENAME: "NORTH WEST DESSERT",
        DESCRIPTION: "Sand spans as far as the eye can see, the odd cactus here and there. The ground tremors lightly.",
        EXAMINATION: "a Giant Sandworm erupts from the ground, and positions itself to attack",
        SOLVED: False,
        ITEM: "Lighthouse Key",
        ENEMY: "Sandworm",
        UP: "b1",
        DOWN: "b3",
        LEFT: "a2",
        RIGHT: "c2",
    },
    "c2": {
        ZONENAME: "NORTH DESSERT",
        DESCRIPTION: "Tiny mounds dot the sand, a thunderous sound is getting louder, as if below the surface...",
        EXAMINATION: "A torrent of Ants explode from the closest mounds! Get ready to fight!",
        SOLVED: False,
        ITEM: "None",
        ENEMY: "Fire Ant Army",
        UP: "c1",
        DOWN: "c3",
        LEFT: "b2",
        RIGHT: "d2",
    },
    "d2": {
        ZONENAME: "NORTH EAST DESSERT",
        DESCRIPTION: "A cool breeze feels refreshing, and something glimmers and twinkles, surrounded by palm trees",
        EXAMINATION: "You take a vial of liquid from the oasis, you can feel it has magical, restorative powers!",
        SOLVED: False,
        ITEM: "Restoring Liquid",
        ENEMY: None,
        UP: "d1",
        DOWN: "d3",
        LEFT: "c2",
        RIGHT: "e2",
    },
    "e2": {
        ZONENAME: "SEAe2",
        DESCRIPTION: "You're standing on the eastern shore of the island, there are no boats or bridges.",
        EXAMINATION: "To the west is the North East Dessert, all other directions lead to nothing.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "e1",
        DOWN: "e3",
        LEFT: "c2",
        RIGHT: "",
    },
    "a3": {
        ZONENAME: "SEAa3",
        DESCRIPTION: "You're standing on the western shore of the island, there are no boats or bridges.",
        EXAMINATION: "West: North East Forest. South: West Beach. And that's about it.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "a2",
        DOWN: "a4",
        LEFT: "",
        RIGHT: "b3",
    },
    "b3": {
        ZONENAME: "NORTH WEST FOREST",
        DESCRIPTION: "Silence... Sticky strands of web dominate the canopy. Cocooned shapes hang from the trees.",
        EXAMINATION: "You look up, and out of the corner of your eye a huge shape scuttles into an attack position...",
        SOLVED: False,
        ITEM: "None",
        ENEMY: "Giant Spider",
        UP: "b2",
        DOWN: "b4",
        LEFT: "a3",
        RIGHT: "c3",
    },
    "c3": {
        ZONENAME: "FARMLANDS",
        DESCRIPTION: "Local Farmers tend to their crops, and a scarecrow stands silently in the field",
        EXAMINATION: "You approach the Scarecrow, and suddenly, its head moves and it stares at you.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: "Scarecrow",
        UP: "c2",
        DOWN: "c4",
        LEFT: "b3",
        RIGHT: "d3",
    },
    "d3": {
        ZONENAME: "NORTH EAST FOREST",
        DESCRIPTION: "This unexplored forest may contain some mystery in the future, but for now, it's just a forest",
        EXAMINATION: "There's nothing going on here at the moment, perhaps the developer will do something later...",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "d2",
        DOWN: "d4",
        LEFT: "c3",
        RIGHT: "e3",
    },
    "e3": {
        ZONENAME: "SEAe3",
        DESCRIPTION: "You're standing on the eastern shore of the island, there are no boats or bridges.",
        EXAMINATION: "Nothing to see here, just the salty air. Try heading inland.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "d2",
        DOWN: "d4",
        LEFT: "c3",
        RIGHT: "e3",
    },
    "a4": {
        ZONENAME: "WEST BEACH",
        DESCRIPTION: "This sandy beach on the western shore of Lithuin Island is great for getting a tan",
        EXAMINATION: "You walk along the beach, dig a few holes, and look under some rocks...",
        SOLVED: False,
        ITEM: "potion",
        ENEMY: None,
        UP: "a3",
        DOWN: "a5",
        LEFT: "",
        RIGHT: "b4",
    },
    "b4": {
        ZONENAME: "PLAINS",
        DESCRIPTION: "Gentle hills, fields of grass, and the occasional horse are all that can be seen here",
        EXAMINATION: "You approach a horse, but you spoke it and it kicks you in the head. Oh well...",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "b3",
        DOWN: "b5",
        LEFT: "a4",
        RIGHT: "c4",
    },
    "c4": {
        ZONENAME: "CENTRAL FOREST",
        DESCRIPTION: "You awoke in the Central Forest. But are you the first, or the last, to do so?",
        EXAMINATION: "There is a fresh mound of dirt",
        SOLVED: False,
        ITEM: "Knife",
        ENEMY: None,
        UP: "c3",
        DOWN: "c5",
        LEFT: "b4",
        RIGHT: "d4",
    },
    "d4": {
        ZONENAME: "CAVE",
        DESCRIPTION: "This cave is dark, and smelly, but goes deep...",
        EXAMINATION: "You call into the cave, your voice echoes back. It's too scary to go any deeper... for now...'",
        ITEM: "Legendary Battle Sword",
        ENEMY: "Cave Troll",
        UP: "d3",
        DOWN: "d5",
        LEFT: "c4",
        RIGHT: "e4",
    },
    "e4": {
        ZONENAME: "WASTELANDe4",
        DESCRIPTION: "Nothing...a landscape of dust and more dust. No point going any further east...",
        EXAMINATION: "Nothing to see here, better head inland",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "e3",
        DOWN: "e5",
        LEFT: "d4",
        RIGHT: "",
    },
    "a5": {
        ZONENAME: "SEAa5",
        DESCRIPTION: "You're standing on the western shore of the island, there are no boats or bridges.",
        EXAMINATION: "Nothing to do here, better head towards the centre of the Island.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "a4",
        DOWN: "a6",
        LEFT: "",
        RIGHT: "b5",
    },
    "b5": {
        ZONENAME: "HORIZON MOUNTAIN",
        DESCRIPTION: "A snow-capped peak that seems to touch the sky, and a treacherous climb...",
        EXAMINATION: "At some point you'll tackle this mountain, but not until the developer has coded it.'",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "b4",
        DOWN: "b6",
        LEFT: "a5",
        RIGHT: "c5",
    },
    "c5": {
        ZONENAME: "LUMBER TOWN",
        DESCRIPTION: "The biggest settlement on the Island, but a low population nonetheless",
        EXAMINATION: "Dreary faced inhabitants shuffle around the dirt street. Maybe this will get coded later...",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "c4",
        DOWN: "c6",
        LEFT: "b5",
        RIGHT: "d5",
    },
    "d5": {
        ZONENAME: "GOURDA CASTLE",
        DESCRIPTION: "Not much is known about Gourda Castle, no one has been in there for decades...",
        EXAMINATION: "A single, giant eye emerges from the darkness... every footstep tumbles the ground...",
        SOLVED: False,
        ITEM: "None",
        ENEMY: "Cyclops",
        UP: "d4",
        DOWN: "d6",
        LEFT: "c5",
        RIGHT: "e5",
    },
    "e5": {
        ZONENAME: "SEAe5",
        DESCRIPTION: "You're standing on the eastern shore of the island, there are no boats or bridges.",
        EXAMINATION: "No boats, no bridges, better head inland again.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "e4",
        DOWN: "e6",
        LEFT: "d5",
        RIGHT: "",
    },
    "a6": {
        ZONENAME: "SEAa6",
        DESCRIPTION: "You're standing on the western shore of the island, there are no boats or bridges.",
        EXAMINATION: "You're getting your bearings on this island now! But this isn't the way, head inland!",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "a5",
        DOWN: "a7",
        LEFT: "",
        RIGHT: "b6",
    },
    "b6": {
        ZONENAME: "LIGHTHOUSE",
        DESCRIPTION: "A tall, red and white striped lighthouse looks over the sea. The door requires a key",
        EXAMINATION: "Do you have the key? No? Then go find it!",
        SOLVED: False,
        ITEM: "Gourda Castle Key",
        ENEMY: "Old Wizard",
        UP: "b5",
        DOWN: "b7",
        LEFT: "a6",
        RIGHT: "c6",
    },
    "c6": {
        ZONENAME: "SWAMP",
        DESCRIPTION: "A green, thick water covers the floor motionlessly, mangrove trees erupt from the silence",
        EXAMINATION: "...buzz....SLAP! That's right, a mosquito made you slap yourself. How do you feel now??!!'",
        SOLVED: False,
        ITEM: "Basic Wand",
        ENEMY: "Skeleton",
        UP: "c5",
        DOWN: "c7",
        LEFT: "b6",
        RIGHT: "d6",
    },
    "d6": {
        ZONENAME: "SOUTH EAST BEACH",
        DESCRIPTION: "This beach is rocky, Gourda Castle looms over it, and bones remain from unlucky travellers",
        EXAMINATION: "Gourda Castle looks huge from here, but there's nothing else of interest.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "d5",
        DOWN: "d7",
        LEFT: "c6",
        RIGHT: "e6",
    },
    "e6": {
        ZONENAME: "SEAe6",
        DESCRIPTION: "You're standing on the eastern shore of the island, there are no boats or bridges.",
        EXAMINATION: "This would be a great place to watch the sunrise...but actually time is weird on the Island.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "e5",
        DOWN: "",
        LEFT: "d6",
        RIGHT: "",
    },
    "a7": {
        ZONENAME: "SEAa7",
        DESCRIPTION: "You're standing on the western shore of the island, there are no boats or bridges.",
        EXAMINATION: "Nice! You're exploring the Island's shore, but it's time to go inland for adventure!",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "a6",
        DOWN: "",
        LEFT: "",
        RIGHT: "b7",
    },
    "b7": {
        ZONENAME: "SOUTH WEST BEACH",
        DESCRIPTION: "A small beach, a nice place to relax after defeating some bosses!",
        EXAMINATION: "It's a lovely place, but there's nothing to see or do here.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "b6",
        DOWN: "",
        LEFT: "a7",
        RIGHT: "",
    },
    "c7": {
        ZONENAME: "SWAMP",
        DESCRIPTION: "A green, thick water covers the floor motionlessly, mangrove trees erupt from the silence",
        EXAMINATION: "It's a swamp, just like the one to the north. You can almost hear the mosquitoes.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "c6",
        DOWN: "",
        LEFT: "",
        RIGHT: "d7",
    },
    "d7": {
        ZONENAME: "SOUTH EAST BEACH",
        DESCRIPTION: "This beach is rocky, Gourda Castle looms over it, and bones remain from unlucky travellers",
        EXAMINATION: "You're on the southern shore of the island, but there's nothing to do here.",
        SOLVED: False,
        ITEM: "None",
        ENEMY: None,
        UP: "d6",
        DOWN: "",
        LEFT: "c7",
        RIGHT: "",
    },
}


## GAME INTERACTIVITY ##


def use_potion():
    if myPlayer.num_health_pots > 0:  # check player has potions
        myPlayer.num_health_pots -= 1  # if yes, remove one potion from player inventory
        myPlayer.hp = myPlayer.hp + myPlayer.health_pot_heal_amount  # increase HP by Potion value
        print(f"You used a Health Potion, increasing your health by {myPlayer.health_pot_heal_amount} and "
              f"you have {myPlayer.num_health_pots} remaining. Health now: {myPlayer.hp}")
    else:
        print(f"You have {myPlayer.num_health_pots} remaining. Health: {myPlayer.hp}")


def use_restoring_liquid():
    if "restoring liquid" in myPlayer.special_item_inventory:  # check player has restoring liquid in inventory
        print("You drink the restoring liquid from the oasis")
        myPlayer.hp += restore_liquid_amount  # add restoring liquid value to HP
        myPlayer.special_item_inventory.remove("restoring liquid")  # remove restoring liquid from inventory
        print(f"You're health points have increased by {restore_liquid_amount} and you feel much better!")
    elif "restoring liquid" not in myPlayer.special_item_inventory:
        print("You don't have any Restoring Liquid.")


def print_location():
    current_location = zonemap[myPlayer.location]  # Fetch the location dictionary
    print("\n" + ("#" * (4 + len(current_location[ZONENAME]))))  # print num of # equivalent to length of zone name
    print("# " + current_location[ZONENAME].upper() + " #")
    print("# " + current_location[DESCRIPTION] + " #")
    print("\n" + ("#" * (4 + len(current_location[ZONENAME]))))


def print_warrior():
    ascii_warrior = [
        "      _,.",
        "    ,` -.)",
        "   ( _/-\\-._",
        "  /,|`--._,-^|            ,",
        "  \\_| |`-._/||          ,'|",
        "    |  `-, / |         /  /",
        "    |     || |        /  /",
        "     `r-._||/   __   /  /",
        " __,-<_     )`-/  `./  /",
        "'  \\   `---'   \\   /  /",
        "    |           |./  /",
        "    /           //  /",
        "\\_/' \\         |/  /",
        " |    |   _,^-'/  /",
        " |    , ``  (\\/  /_",
        "  \\,.->._    \\X-=/^",
        "  (  /   `-._//^`",
        "   `Y-.____(__}",
        "    |     {__)",
        "          ()"
    ]

    for line in ascii_warrior:
        print(line)


def print_mage():
    ascii_mage = [
        "              _,-'|",
        "           ,-'._  |",
        " .||,      |####\\ |",
        "\\.`',/     \\####| |",
        "= ,. =      |###| |",
        "/ || \\    ,-'\#/,'`.",
        "  ||     ,'   `,,. `.",
        "  ,|____,' , ,;' \\| |",
        " (3|\\    _/|/'   _| |",
        "  ||/,-''  | >-'' _,\\\\",
        "  ||'      ==\\ ,-'  ,'",
        "  ||       |  V \\ ,|",
        "  ||       |    |` |",
        "  ||       |    |   \\",
        "  ||       |    \\    \\",
        "  ||       |     |    \\",
        "  ||       |      \\_,-'",
        "  ||       |___,,--)_\\",
        "  ||         |_|   ccc/",
        "  ||        ccc/",
        "  ||                hjm"
    ]

    for line in ascii_mage:
        print(line)


def print_priest():
    ascii_priest = [
        "           .---.",
        "         /` ___|`\\",
        "         |_/    \\|",
        "         (  -/-  )",
        "          \\_ - _/",
        "         .-'|_|'-.",
        "        /         \\",
        "       /     O     \\",
        "      / _____!_____ \\",
        "     /.-------------.\\",
        "     \\|     ,;,     |/",
        "      |     ;;;     |",
        "      |  ;;;;;;;;;  |",
        "      |   `';;;'`   |",
        "      |     ;;;     |",
        "      |     ;;;     |",
        "      |     :::     |",
        "      |     ';'     |",
        "      |             |",
        "     _| _  __   __ _|_",
        "   _/ _  __  ___  __ _\\_",
        " _/ __  ___  _ ___ __ _ \\_"
    ]

    for line in ascii_priest:
        print(line)


def prompt():
    sitrep()
    print("\n" + "==================")
    print("What would you like to do?")
    action = input("> ")
    acceptable_actions = ["move", "go", "travel", "walk", "journey", "run", "quit", "inspect", "examine", "look",
                          "peek", "interact", "equip", "potion", "liquid"]
    while action.lower() not in acceptable_actions:  # check input is in acceptable actions list
        print("Unknown action, please try again \n")
        action = input("> ")
    if action.lower() == "quit":
        sys.exit()
    elif action.lower() in ["move", "go", "travel", "walk", "journey", "run"]:
        player_move()
    elif action.lower() in ["inspect", "examine", "look", "peek", "interact"]:
        player_examine()
    elif action.lower().endswith("potion"):
        use_potion()
    elif action.lower().endswith("liquid"):
        use_restoring_liquid()
    elif action.lower() == "equip":
        player_equip()


def player_equip():
    # define weapon multiplier values
    sword_leg_mult = 2
    sword_mult = 1.5
    knife_leg_mult = 1.5
    knife_mult = 1.2
    wand_leg_mult = 5
    wand_mult = 3

    # reset attack and magic points to prevent weapon multiplier stacking
    if myPlayer.job.lower() == "warrior":
        myPlayer.ap = w_ap_reset
        myPlayer.mp = w_mp_reset
    elif myPlayer.job.lower() == "mage":
        myPlayer.ap = w_ap_reset
        myPlayer.mp = w_mp_reset
    elif myPlayer.job.lower() == "priest":
        myPlayer.ap = p_ap_reset
        myPlayer.mp = p_mp_reset

    # print current items
    print(f"You currently have {myPlayer.weapons_inventory}"
          f"You're current equipped weapon is {myPlayer.equipped_weapon}\n")
    item_to_equip = input("Which item would you like to equip?\n")
    if item_to_equip in myPlayer.special_item_available:
        print("Sorry, this is a special item, try again")
        player_equip()
    else:
        # Equip the item
        if item_to_equip in myPlayer.weapons_inventory:
            myPlayer.equipped_weapon = item_to_equip
            print(f"You have equipped {item_to_equip} as your weapon")

            # Modify Player Stats based on equipped weapon. Legendary Items have higher multiplier, wands affect MP

            if item_to_equip.lower().endswith("sword"):
                if item_to_equip.lower().startswith("Legendary"):
                    myPlayer.ap = myPlayer.ap * sword_leg_mult
                    myPlayer.weapon_mult = sword_leg_mult
                    print(f"{item_to_equip} equipped, Attack Points now {myPlayer.ap}")
                else:
                    myPlayer.ap = myPlayer.ap * sword_mult
                    myPlayer.weapon_mult = sword_mult
                    print(f"{item_to_equip} equipped, Attack Points now {myPlayer.ap}")
            elif item_to_equip.lower().endswith("knife"):
                if item_to_equip.lower().startswith("Legendary"):
                    myPlayer.ap = myPlayer.ap * knife_leg_mult
                    myPlayer.weapon_mult = knife_leg_mult
                    print(f"{item_to_equip} equipped, Attack Points now {myPlayer.ap}")
                else:
                    myPlayer.ap = myPlayer.ap * knife_mult
                    myPlayer.weapon_mult = knife_mult
                    print(f"{item_to_equip} equipped, Attack Points now {myPlayer.ap}")
            elif item_to_equip.lower().endswith("wand"):
                if item_to_equip.lower().startswith("Legendary"):
                    myPlayer.mp = myPlayer.mp * wand_leg_mult
                    myPlayer.weapon_mult = wand_leg_mult
                    print(f"{item_to_equip} equipped, Magic Points now {myPlayer.mp}")
                else:
                    myPlayer.mp = myPlayer.mp * wand_mult
                    myPlayer.weapon_mult = wand_mult
                    print(f"{item_to_equip} equipped, Magic Points now {myPlayer.mp}")

            elif item_to_equip.lower() == "none":
                myPlayer.mp = myPlayer.mp * 1
                print(f"Nothing equipped, Magic Points now {myPlayer.mp} and Attack Points now {myPlayer.ap}")
        else:
            print(f"Sorry, you don't have a {item_to_equip}")
            player_equip()


def player_move():
    print("Where would you like to move to?\n")
    dest = input("> ")
    if dest in ["up", "north"]:
        destination = zonemap[myPlayer.location][UP]  # take next location from zonemap dictionary
        movement_handler(destination)
    if dest in ["left", "west"]:
        destination = zonemap[myPlayer.location][LEFT]
        movement_handler(destination)
    if dest in ["right", "east"]:
        destination = zonemap[myPlayer.location][RIGHT]
        movement_handler(destination)
    if dest in ["down", "south"]:
        destination = zonemap[myPlayer.location][DOWN]
        movement_handler(destination)


def movement_handler(destination):
    destination_name = zonemap[destination][ZONENAME]  # moves player based on player_move function
    print("\n" + "You have moved to the " + destination_name + ".")
    myPlayer.location = destination
    print_location()


def player_examine():
    # variables used for weapon multiplier under player_examine function
    sword_leg_mult_exam = 2
    sword_mult_exam = 1.5
    knife_leg_mult_exam = 1.5
    knife_mult_exam = 1.2
    wand_leg_mult_exam = 5
    wand_mult_exam = 3

    current_location = zonemap[myPlayer.location]  # set player current location based on zonemap dictionary

    if current_location[ITEM] == "none" and current_location[ENEMY] == "none":  # if no item and no boss...
        zonemap[myPlayer.location][SOLVED] = True  # ...set solved as true for area
        print("You have already completed this part of the Island.")
    else:
        print(current_location[EXAMINATION])  # print examine from zonemap dictionary

        # Check if there is an item in this location
        if current_location[ITEM].lower() != "none":
            if current_location[ITEM] == "potion":  # ask if the item is a potion, then add 1 potion to inv
                print("You found a health potion!")
                myPlayer.num_health_pots += 1
                current_location[ITEM] = "none"
            elif current_location[ITEM].lower().endswith("key"):  # ask if item is key, tell player to defeat boss
                print("You get the sense that by defeating this enemy, you will be rewarded...")
            elif current_location[ITEM].lower().endswith("liquid"):
                myPlayer.special_item_inventory.append("restoring liquid")
            else:
                print("You find a " + current_location[ITEM] + "!")  # acquire item
                myPlayer.weapons_inventory.append(zonemap[myPlayer.location][ITEM])
                if current_location[ITEM].lower() in myPlayer.special_item_available and not current_location[
                    ITEM].lower().endswith("key"):
                    # above, if item is in available items but not a key, then...
                    print(
                        "The " + current_location[ITEM] + " has been added to your Special Items Pouch for later use.")
                else:
                    print(
                        f"Would you like to equip the {current_location[ITEM]} as your weapon?")  # assume item is weapon
                    temp_equip = input("> ")
                    if temp_equip.lower() in ["yes", "y"]:
                        myPlayer.equipped_weapon = current_location[ITEM]  # equip weapon form inventory
                        item_to_equip_exam = myPlayer.equipped_weapon
                        if item_to_equip_exam.lower().endswith("sword"):  # same as player_equip function
                            if item_to_equip_exam.lower().startswith("Legendary"):
                                myPlayer.ap = myPlayer.ap * sword_leg_mult_exam
                                myPlayer.weapon_mult = sword_leg_mult_exam
                                print(f"{item_to_equip_exam} equipped, Attack Points now {myPlayer.ap}")
                            else:
                                myPlayer.ap = myPlayer.ap * sword_mult_exam
                                myPlayer.weapon_mult = sword_mult_exam
                                print(f"{item_to_equip_exam} equipped, Attack Points now {myPlayer.ap}")
                        elif item_to_equip_exam.lower().endswith("knife"):
                            if item_to_equip_exam.lower().startswith("Legendary"):
                                myPlayer.ap = myPlayer.ap * knife_leg_mult_exam
                                myPlayer.weapon_mult = knife_leg_mult_exam
                                print(f"{item_to_equip_exam} equipped, Attack Points now {myPlayer.ap}")
                            else:
                                myPlayer.ap = myPlayer.ap * knife_mult_exam
                                myPlayer.weapon_mult = knife_mult_exam
                                print(f"{item_to_equip_exam} equipped, Attack Points now {myPlayer.ap}")
                        elif item_to_equip_exam.lower().endswith("wand"):
                            if item_to_equip_exam.lower().startswith("Legendary"):
                                myPlayer.mp = myPlayer.mp * wand_leg_mult_exam
                                myPlayer.weapon_mult = wand_leg_mult_exam
                                print(f"{item_to_equip_exam} equipped, Magic Points now {myPlayer.mp}")
                            else:
                                myPlayer.mp = myPlayer.mp * wand_mult_exam
                                myPlayer.weapon_mult = wand_mult_exam
                                print(f"{item_to_equip_exam} equipped, Magic Points now {myPlayer.mp}")

                        elif item_to_equip_exam.lower() == "none":
                            myPlayer.mp = myPlayer.mp * 1

                            print(
                                f"Nothing equipped, Magic Points now {myPlayer.mp} and Attack Points now {myPlayer.ap}")
                    elif temp_equip.lower() in ["no", "n"]:
                        print(f"No problem, your current weapon is {myPlayer.equipped_weapon}")
                    else:
                        print("Invalid Entry, the item has been placed into your backpack, you may equip it later")
                current_location[ITEM] = "None"


        elif current_location[ITEM].lower() == "none":  # if no items in map location...
            print("There are no items to collect here...")

        # Check if there's a boss in this location
        if current_location[ENEMY] is not None:  # if boss exists, fight boss
            print("You've encountered a " + current_location[ENEMY] + "!")
            boss_fight()


## GAME FUNCTIONALITY ##


def restart_game():
    current_location = zonemap[myPlayer.location][ZONENAME]
    boss_name = zonemap[myPlayer.location][BOSS]
    ascii_death_text = '''
             88                               88           
             88                         ,d    88           
             88                         88    88           
     ,adPPYb,88  ,adPPYba, ,adPPYYba, MM88MMM 88,dPPYba,   
    a8"    `Y88 a8P_____88 ""     `Y8   88    88P'    "8a  
    8b       88 8PP""""""" ,adPPPPP88   88    88       88  
    "8a,   ,d88 "8b,   ,aa 88,    ,88   88,   88       88  
     `"8bbdP"Y8  `"Ybbd8"' `"8bbdP"Y8   "Y888 88       88  
    '''

    print(ascii_death_text)
    print(f"You were slain during your adventure by a {boss_name}, whilst at the {current_location} and there is no ")
    print(f"potion nor spell can fix that")
    print(f"But you can take what you've learned forward with you, into a new body, a new soul...")
    print(f"And a new name - if you wish!")

    myPlayer.equipped_weapon = "None"  # Weapon Equipped
    myPlayer.weapons_inventory = []  # weapons on inventory
    myPlayer.special_item_inventory = []  # special items that are on players inventory
    myPlayer.special_item_available = ["lighthouse key", "gourda castle key", "restoring liquid"]
    myPlayer.name = ""  # player name
    myPlayer.hp = 0  # health points
    myPlayer.mp = 0  # magic points
    myPlayer.ap = 0  # attack points
    myPlayer.status_effect = []  # status effects
    myPlayer.job = ""  # player class type
    myPlayer.location = "c4"  # player starting location, updated based on player movement
    myPlayer.num_health_pots = 2  # number of health potions at game start, updates during game
    myPlayer.health_pot_heal_amount = 40  # amount health potions increase health points by
    myPlayer.gameover = False  # when true, game ends
    myPlayer.weapon_mult = 1  # weapon multiplier, updated when new weapon equipped

    title_screen()


def boss_fight():  # placeholder - need to rewrite this function to use class enemy
"""
    clear_screen()
    # set variables so function is easy to write
    boss_location = myPlayer.location
    boss_name = zonemap[myPlayer.location][BOSS]
    boss_hp = zonemap[myPlayer.location][BOSSHEALTH]
    boss_ap = zonemap[myPlayer.location][BOSSATTACK]

    while boss_hp > 0 and myPlayer.hp > 0:

        # Boss Info

        print(f"Enemy: {boss_name.upper()} | HP: {boss_hp} | AP: {boss_ap}")
        print("###################################################")
        print(f"{myPlayer.name.upper()} | Health Points: {myPlayer.hp}")
        print(f"Weapon: {myPlayer.equipped_weapon.upper()} | Magic Points: {myPlayer.mp}")
        print(f"Weapon Multiplier: {myPlayer.weapon_mult} | AP: {myPlayer.ap}")
        print(f"Health Potions: {myPlayer.num_health_pots}")
        print("###################################################")

        # Player's turn
        print("What would you like to do?")
        print("Attack, Use Magic, Use Potion")
        choice = input("> ")
        if choice.lower().endswith("potion"):
            use_potion()
        elif choice.lower() == "attack":
            player_attack = random.randint(1,
                                           myPlayer.ap)  # player attack points randomly select between 1 and player attack points
            boss_hp -= player_attack  # deduct player attack from enemy HP
            print(f"You attack the {boss_name.upper()} for {player_attack} damage.")

            if boss_hp <= 0:
                print(f"You defeated the {boss_name.upper()}!")
                break
        elif choice.lower() == "magic":
            player_magic = random.randint(1, myPlayer.mp)
            boss_hp -= player_magic
            print(f"You cast a spell on the {boss_name} for {player_magic} damage.")

            if boss_hp <= 0:
                print(f"You defeated the {boss_name}!")
                break

            # Boss's turn
        boss_attack = random.randint(1, boss_ap)
        myPlayer.hp -= boss_attack
        print(f"The {boss_name} attacks you for {boss_attack} damage.")

        if myPlayer.hp <= 0:
            print("You've been defeated!")
            sitrep()
            myPlayer.gameover = True
            break

    # After the battle
    if boss_hp <= 0:

        solved_places[boss_location] = True  # set location to solved
        myPlayer.num_health_pots += 1  # reward player with health potion
        print(f"You have received a Health Potion")
        if boss_name.lower() in ["old wizard"]:  # once old wizard is defeated, give gourda castle key
            myPlayer.special_item_inventory.append("gourda castle key")
            print("The Old Wizard disintegrated before your eyes, leaving only the Gourda Castle Key behind!")
            print("You added the Gourda Castle Key to your Special Item pouch!")
        elif boss_name.lower() in ["sandworm"]:  # once sandworm is defeated, give lighthouse key
            myPlayer.special_item_inventory.append("lighthouse key")
            print("The Sandworm explodes into a million pieces, it left the Lighthouse Key behind!")
            print("You added the Lighthouse Key to your Special Item pouch!")


    else:
        print(f"You died fighting the {boss_name}")
        print("Would you like to play again? (Yes/No)")
        restart = input("> ")
        if restart.lower() == "yes":
            restart_game()

        elif restart.lower() == "no":
            print(f"The final status of {myPlayer.name} the {myPlayer.job}")
            sitrep()
            print("")
            print("Press any key to exit: ")
            input()
        else:
            print("Invalid answer, would you like to restart the game (Yes/No)")
            restart = input("> ")
            if restart.lower() == "yes":
                restart_game()
            elif restart.lower() == "no":
                print(f"The final status of {myPlayer.name} the {myPlayer.job}")
                sitrep()
                print("")
                print("Press any key to exit: ")
                input()

    # Continue with the main game loop
    main_game_loop()
"""


def main_game_loop():
    while myPlayer.gameover is False:
        prompt()


def start_game():
    clear_screen()

    ## NAME COLLECTION ###
    question1 = "Tell me, what name do you go by?\n"
    for character in question1:
        sys.stdout.write(character)  # prints info slowly
        sys.stdout.flush()
        time.sleep(0.05)
    player_name = input("> ")
    myPlayer.name = player_name
    if player_name.lower() != "admin":  # if user name is admin, skip game intro, otherwise continue

        ## PLAYER CLASS COLLECTION ##

        question2 = "Tell me " + player_name + ", what manner of being are you?\n"
        valid_jobs = ["warrior", "mage", "priest"]
        question2added = ("You can play as any of the following: " + ", ".join(valid_jobs) + "\n")
        for character in question2:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        for character in question2added:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.02)
        player_job = input("> ")

        # set player stats based on class or character type
        if player_job.lower() in valid_jobs:
            myPlayer.job = player_job
            if myPlayer.job.lower() == "warrior":
                print_warrior()
                myPlayer.hp = 120
                myPlayer.mp = 20
                myPlayer.ap = 50
            elif myPlayer.job.lower() == "mage":
                print_mage()
                myPlayer.hp = 20
                myPlayer.mp = 60
                myPlayer.ap = 30
            elif myPlayer.job.lower() == "priest":
                print_priest()
                myPlayer.hp = 70
                myPlayer.mp = 40
                myPlayer.ap = 20

            print("You will be known on Lithuin Island as " + myPlayer.name + " the " + myPlayer.job + "!\n")
        else:
            while myPlayer.job.lower() not in valid_jobs:
                print("That's not a valid player class, try again")
                player_job = input("> ")
                if player_job.lower() in valid_jobs:
                    myPlayer.job = player_job
                    if myPlayer.job.lower() == "warrior":
                        print_warrior()
                        myPlayer.hp = 120
                        myPlayer.mp = 20
                        myPlayer.ap = 50
                    elif myPlayer.job.lower() == "mage":
                        print_mage()
                        myPlayer.hp = 20
                        myPlayer.mp = 120
                        myPlayer.ap = 30
                    elif myPlayer.job.lower() == "priest":
                        print_priest()
                        myPlayer.hp = 70
                        myPlayer.mp = 70
                        myPlayer.ap = 20
                    print("You will be known on Lithuin Island as " + myPlayer.name + " the " + myPlayer.job + "!\n")

        ## INTRODUCTION ##

        question3 = "Welcome, " + player_name + " the " + player_job + ".\n"
        for character in question3:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)

        # game intro
        speech1 = "Welcome to Lithuin Island! \n"
        speech2 = "The Central Forest is in the middle of Lithuin Island. Tall trees create a canopy that blocks\n"
        speech3 = "the sky, but causes the forest floor to glisten with a green, almost magical glow. A strange mound\n"
        speech4 = "of dirt a few steps away appears fairly fresh.\n"

        for character in speech1:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.1)
        for character in speech2:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.1)
        for character in speech3:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        for character in speech4:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.01)

        clear_screen()
        print("")
        print("##########################")
        print("#   Let's start now...   #")
        print("##########################")
        main_game_loop()
    else:
        myPlayer.job = "ADMIN"
        myPlayer.hp = 20
        myPlayer.mp = 20
        myPlayer.ap = 20
        main_game_loop()


title_screen()