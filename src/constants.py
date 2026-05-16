# User-facing text strings for the Critters game.
# This module centralizes all UI text to avoid duplication and simplify localization.

# --- HUD ---
HUD_BUILD_BUTTON = "Build"
HUD_CRAFT_BUTTON = "Craft"
HUD_BUFFS_TITLE = "Buffs"
HUD_BUFFS_NONE = "(none)"

# --- Deconstruction Mode ---
DECONSTRUCTION_MODE_LABEL = "Deconstruction Mode (X to exit)"

# --- World Messages (feedback) ---
MESSAGE_DECONSTRUCTED = "Deconstructed"
MESSAGE_OUT_OF_RANGE = "Out of range"
MESSAGE_FOLLOW_START = "Critter is following you."
MESSAGE_FOLLOW_STOP = "Stopped following."

# --- Critter Inspector UI ---
INSPECTOR_TITLE = "Critter Stats"
LABEL_STATE = "State:"
LABEL_STRENGTH = "Strength:"
LABEL_SPEED = "Speed:"
LABEL_ENDURANCE = "Endurance:"
LABEL_CAPACITY = "Carry Capacity:"
LABEL_HELD = "Held:"
LABEL_GATHER_SPEED = "Gather Speed:"
LABEL_MOVE_SPEED = "Move Speed:"
LABEL_BUFFS = "Buffs:"
LABEL_ASSIGNED = "Assigned:"
VALUE_ASSIGNED_NONE = "None"
BUTTON_FOLLOW = "Follow"
BUTTON_STOP_FOLLOW = "Stop Following"

# --- Breeding Parameters ---
BREED_INHERIT_A = 0.40
BREED_INHERIT_B = 0.40
BREED_WILDCARD = 0.20
BREED_WILDCARD_LOG_WEIGHT = 0.80
BREED_WILDCARD_UNIFORM_WEIGHT = 0.20
BREED_WILDCARD_LOG_MU = 2.8   # Results in mode ~15
BREED_WILDCARD_LOG_SIGMA = 0.55
BREED_MUTATION_MIN = 0.9
BREED_MUTATION_MAX = 1.1

# --- Recycling & Candies ---
ITEM_CANDY_STR = "Strength Candy"
ITEM_CANDY_SPD = "Speed Candy"
ITEM_CANDY_END = "Endurance Candy"
MESSAGE_RELEASE_SUCCESS = "Critter released. Received {candy}."

# --- Building Interaction Prompts ---
PROMPT_GATHER = "Press E to collect resources"
PROMPT_WITHDRAW = "Withdraw (E)"
PROMPT_BREED = "Press E to breed critters"
PROMPT_REST = "Rest on Chair (E)"
PROMPT_ASSIGN = "Assign: E"
PROMPT_DIRECT_ASSIGN = "Right-click: Assign"

# --- Building Costs ---
BUILDING_GATHERING_HUT_COST = {"wood": 10, "stone": 5}
BUILDING_MATING_HUT_COST = {"wood": 15, "stone": 10}
BUILDING_RELEASE_ALTAR_COST = {"stone": 15}
BUILDING_LUMBER_MILL_COST = {"wood": 20}
BUILDING_FORESTER_HUT_COST = {"wood": 15, "stone": 5}
BUILDING_CHAIR_COST = {"wood": 4}
BUILDING_CAMPFIRE_COST = {"wood": 2, "stone": 2}

# --- Item Types ---
ITEM_FOOD = "food"
ITEM_WOOD = "wood"
ITEM_STONE = "stone"
ITEM_SAPLING = "sapling"
ITEM_STICK = "stick"

# --- Building Labels ---
BUILDING_GATHERING_HUT = "Gathering Hut"
BUILDING_MATING_HUT = "Mating Hut"
BUILDING_LUMBER_MILL = "Lumber Mill"
BUILDING_FORESTER_HUT = "Forester's Hut"
BUILDING_RELEASE_ALTAR = "Release Altar"
BUILDING_CHAIR = "Chair"
BUILDING_CAMPFIRE = "Campfire"

# --- Building Interaction Feedback Messages ---
MSG_ASSIGN_GATHERING = "Critter assigned to Gathering Hut."
MSG_ASSIGN_MATING = "Critter assigned to Mating Hut."
MSG_BREED_NEED_TWO = "Need at least 2 critters to breed!"
MSG_BREED_NEED_FOOD = "Need {} food to breed!"  # Format with required amount
MSG_BREED_SUCCESS = "Breeding produced a new critter!"

# --- Buff Names ---
BUFF_NAME_WARM = "Warm"
BUFF_NAME_RESTED = "Rested"

# --- Title Screen ---
TITLE_TEXT = "CRITTERS"
BUTTON_NEW_GAME = "New Game"
BUTTON_CONTINUE = "Continue"
INSTRUCTIONS = "N: New, C: Continue, Esc: Quit"
CONFIRM_OVERWRITE = "New Game will overwrite the saved game."
CONFIRM_PROCEED = "Proceed?"
BUTTON_YES = "Yes"
BUTTON_NO = "No"

# --- Build Menu ---
BUILD_MENU_TITLE = "Build Menu (B to close)"
BUILD_BUTTON_TEXT = "Build"
BUILD_PLACEMENT_INSTR = "Click grid to place"

# --- Crafting Menu ---
CRAFTING_MENU_TITLE = "Crafting (R to close)"
CRAFT_MSG_NOT_ENOUGH = "Not enough {resource}!"
CRAFT_MSG_UNLOCKED = "Unlocked: {item}!"
CRAFT_MSG_CRAFTED = "Crafted: {item}!"

# --- Display Settings ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# --- Building Labels (for Build Menu) ---
BUILDING_GATHERING_HUT = "Gathering Hut"
BUILDING_MATING_HUT = "Mating Hut"
BUILDING_CHAIR = "Chair"
BUILDING_CAMPFIRE = "Campfire"
