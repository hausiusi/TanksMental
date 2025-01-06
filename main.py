from ursina import *
from src.player import Player
from src.game import Game
from src.controller import KeyboardController, PS4Controller
from src.enums import EntityType


app = Ursina()

game = Game()
controller = PS4Controller()
keyboard = KeyboardController()

# Mode toggle
is_edit_mode = False

def is_on_screen(entity):
    """Check if an entity is within fixed screen bounds."""
    position = entity.position
    return is_position_on_screen(position)

def is_position_on_screen(position):
        return (
        game.settings.screen_left <= position.x <= game.settings.screen_right and
        game.settings.screen_bottom <= position.y <= game.settings.screen_top
    )

def refresh_stats():
    for player in game.players:
        player.refresh_stats()
    game.refresh_level_stats(game.npc_spawner.npc_pool_index + 1, 
                             len(game.npc_spawner.npc_pools), 
                             game.npc_spawner.total_npcs - game.npc_spawner.spawned_count)

timer_counter = 0
update_interval = 0.2
is_game_over = False


def update():

    global is_edit_mode
    global timer_counter
    global update_interval
    global is_game_over

    if is_game_over or game.paused:
        return
    
    if is_edit_mode:
        return  # Skip movement logic when in edit mode
    
    dt = time.dt
    timer_counter += dt
    if timer_counter > update_interval:
        refresh_stats()
        timer_counter = 0

    if dt > 0.02:
        print(f"The frame rate is low {1 / dt}")

def input(key):
    global is_edit_mode
    if key == 'tab':  # Toggle edit/play mode
        is_edit_mode = not is_edit_mode
        EditorCamera(enabled=is_edit_mode)  # Enable/disable the editor camera
        print("Edit mode:", is_edit_mode)


app.run()
