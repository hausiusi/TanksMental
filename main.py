from ursina import *
import math
from src.levels import load_map
from src.player import Player
from src.npc import EnemyTank
from src.game import Game
from src.controller import KeyboardController, PS4Controller
from src.types import CollisionEffect, EntityType
from src.npc import NpcSpawner


app = Ursina()
camera.orthographic = False
camera.fov = 50
window.fullscreen = True
window.exit_button.visible = False

game = Game()
spawner = NpcSpawner(game)
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

tile_size = 1

def create_tile_map():
    level_map = load_map(0)
    for y, row in enumerate(level_map):
        for x, val in enumerate(row):
            # Position the tile such that the center is (0, 0)
            # Tile positions will be adjusted based on the grid center
            if val != 0:
                pos_x = (x - len(row) // 2) * tile_size
                pos_y = -(y - len(level_map) // 2) * tile_size

                durability = 100
                takes_hit = False
                resistance = 0
                damaging = 0
                collision_effect = CollisionEffect.NO_EFFECT
                effect_strength = 0
                name = ""
                entity_type=EntityType.TERRAIN

                # Create a tile (Entity with Quad mesh)
                if val == 1:
                    tile_texture = 'assets/images/grass.png'
                    collision_effect = CollisionEffect.SLOW_DOWN
                    effect_strength = 50
                    name = f'grass_{x}_{y}'
                elif val == 2:
                    tile_texture = 'assets/images/wall0.png'
                    collision_effect = CollisionEffect.BARRIER
                    durability = 5
                    takes_hit = True
                    name = f'wall_{x}_{y}'
                elif val == 3:
                    tile_texture = 'assets/images/water0.png'
                    collision_effect = CollisionEffect.DAMAGE_WET
                    effect_strength = 90
                    name = f'water_{x}_{y}'
                elif val == 4:
                    tile_texture = 'assets/images/fire0.png'
                    collision_effect = CollisionEffect.DAMAGE_BURN
                    effect_strength = 1
                    name = f'fire_{x}_{y}'
                    damaging = 1
                elif val == 5:
                    tile_texture = 'assets/images/stones0.png'
                    collision_effect = CollisionEffect.SLOW_DOWN
                    effect_strength = 50
                    name = f'stones_{x}_{y}'
                elif val == 6:
                    tile_texture = 'assets/images/white_wall.png'
                    collision_effect = CollisionEffect.BARRIER
                    takes_hit = True
                    durability = 10
                    name = f'white_wall_{x}_{y}'
                elif val == 7:
                    tile_texture = 'assets/images/sand.png'
                    collision_effect = CollisionEffect.SLOW_DOWN
                    effect_strength = 30
                    takes_hit = True
                    durability = 1
                    name = f'sand_{x}_{y}'
                elif val == 8:
                    tile_texture = 'assets/images/gas_station0.png'
                    collision_effect = CollisionEffect.NO_EFFECT
                    entity_type = EntityType.BASE
                    takes_hit = True
                    durability = 1
                    name = f'gas_station_{x}_{y}'

                tile = Entity(
                    name=name,
                    model='quad',
                    entity_type=entity_type,
                    z = 0,                    
                    texture=tile_texture,  # Apply the texture to each tile
                    scale=(tile_size - 0.001, tile_size - 0.001),  # Set the tile size
                    position=(pos_x, pos_y),  # Position the tile in the grid
                    collider='box',  # Add a collider if needed (for interaction)
                    durability=durability,
                    takes_hit=takes_hit,
                    damaging=damaging,
                    collision_effect=collision_effect,
                    effect_strength=effect_strength,
                    render_queue=1,
                    color = color.Color(1,1,1,1)
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
    game.refresh_level_stats(spawner.npc_pool_index, len(spawner.npc_pools), spawner.total_npcs - spawner.spawned_count)

timer_counter = 0
update_interval = 0.1
is_game_over = False

spawner.spawn_initial_npcs()

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


create_tile_map()
game.update_no_barrier_entities()
game.update_barrier_entities()
app.run()
