from ursina import *
import math
from src.player import Player
from src.npc import EnemyTank
from src.game import Game
from src.controller import KeyboardController, PS4Controller
from src.types import CollisionEffect, EntityType


app = Ursina()
camera.orthographic = False
camera.fov = 50
window.fullscreen = True
window.exit_button.visible = False

game = Game()
controller = PS4Controller()
keyboard = KeyboardController()

player1 = Player(
    game,
    controller=controller,
    player_id=0,
    model='quad',
    texture='assets/images/player_tank.png',
    position=(-2, -5),
    z=0,
    scale=(0.8, 1),
    color=color.pink,
    collider='box',
    rigidbody=True,
    bullets_on_screen=0,
    is_tank=True,
    can_shoot=True,
    max_speed=2,
    takes_hit=True,
    durability=100,
    is_exploded=False,
    remove_counter=0,
    remove_limit=3,
)

player2 = Player(
    game,
    controller=controller,
    player_id=1,                  
    model='quad',
    texture='assets/images/player_tank.png',
    position=(2, -5),
    z=0,
    scale=(0.8, 1),
    color=color.yellow,
    collider='box',
    rigidbody=True,
    bullets_on_screen=0,
    is_tank=True,
    can_shoot=True,
    max_speed=2,
    takes_hit=True,
    durability=100,
    is_exploded=False,
    remove_counter=0,
    remove_limit=3,
)

player3 = Player(
    game,
    controller=keyboard,
    player_id=2,                  
    model='quad',
    texture='assets/images/player_tank.png',
    position=(4, -5),
    z=0,
    scale=(0.8, 1),
    color=color.turquoise,
    collider='box',
    rigidbody=True,
    bullets_on_screen=0,
    is_tank=True,
    can_shoot=True,
    max_speed=2,
    takes_hit=True,
    durability=100,
    is_exploded=False,
    remove_counter=0,
    remove_limit=3,

)

# Mode toggle
is_edit_mode = False  
#EditorCamera(enabled=True) 

def check_collision(direction, distance):
    try:       
        ray = raycast(player1.position, direction, ignore=[player1], distance=distance)
        return ray.hit
    except Exception as ex:
        return False

def get_collision_element(element, direction, distance):
    """Gets the entity that was collided with passed entity"""
    try:
        ray = raycast(element.position, direction, ignore=[element], distance=distance)
        if ray.hit:
            return ray.entity
    except Exception as ex:
        pass
    return None

directions = {
    0: Vec3(0, 1, 0),  # Up
    1: Vec3(1, 0, 0),  # Right
    2: Vec3(0, -1, 0), # Down
    3: Vec3(-1, 0, 0)  # Left
}

SCREEN_LEFT = -7
SCREEN_RIGHT = 7
SCREEN_TOP = 5
SCREEN_BOTTOM = -5

def is_on_screen(entity):
    """Check if an entity is within fixed screen bounds."""
    position = entity.position
    return is_position_on_screen(position)

def is_position_on_screen(position):
        return (
        SCREEN_LEFT <= position.x <= SCREEN_RIGHT and
        SCREEN_BOTTOM <= position.y <= SCREEN_TOP
    )

def refresh_stats():
    player1.refresh_stats()
    player2.refresh_stats()
    player3.refresh_stats()
    game.refresh_level_stats(game.npc_spawner.npc_pool_index + 1, 
                             len(game.npc_spawner.npc_pools), 
                             game.npc_spawner.total_npcs - game.npc_spawner.spawned_count)

timer_counter = 0
update_interval = 0.1
is_game_over = False


def update():

    global is_edit_mode
    global timer_counter
    global update_interval
    global is_game_over

    if is_game_over:
        return
    
    if is_edit_mode:
        return  # Skip movement logic when in edit mode

    timer_counter += time.dt
    if timer_counter > update_interval:
        refresh_stats()
        timer_counter = 0

    for bullet in scene.entities:
        if bullet.visible and hasattr(bullet, 'velocity'):
            bullet.position += bullet.velocity * time.dt
            # Destroy bullet if it goes off-screen
            if not game.is_on_screen(bullet):                
                destroy(bullet)
                bullet.owner.bullets_on_screen -= 1
                return
            collided_entity = get_collision_element(bullet, bullet.velocity, 0.5)
            if bullet.visible and collided_entity != None:
                if hasattr(collided_entity, 'takes_hit'):
                    if collided_entity.takes_hit:
                        collided_entity.durability -= bullet.hit_damage
                        if collided_entity.durability <= 0:
                            if hasattr(collided_entity, 'is_tank'):
                                    if not collided_entity.is_exploded:
                                        bullet.owner.kills += 1
                                        collided_entity.check_destroy()
                            else:
                                destroy(collided_entity)
                                if collided_entity.entity_type == EntityType.BASE:
                                    game.show_game_over()
                        if hasattr(collided_entity, 'is_tank') and not collided_entity.is_exploded:
                            bullet.owner.tanks_damage_dealt += bullet.hit_damage
                        else:
                            bullet.owner.other_damage_dealt += bullet.hit_damage
                            
                        destroy(bullet)
                        bullet.owner.bullets_on_screen -= 1

    

def input(key):
    global is_edit_mode
    if key == 'tab':  # Toggle edit/play mode
        is_edit_mode = not is_edit_mode
        EditorCamera(enabled=is_edit_mode)  # Enable/disable the editor camera
        player1.enabled = not is_edit_mode  # Disable player in edit mode
        print("Edit mode:", is_edit_mode)

game.create_tile_map()
game.npc_spawner.load_level_npcs(game.level_index)
game.npc_spawner.spawn_initial_npcs()
game.update_no_barrier_entities()
game.update_barrier_entities()
game.controllers.append(player1.controller)
game.controllers.append(player2.controller)
game.controllers.append(player3.controller)
game.players.append(player1)
game.players.append(player2)
game.players.append(player3)
app.run()
