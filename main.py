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

def get_collision_element(element, direction, distance):
    """Gets the entity that was collided with passed entity"""
    try:
        ray = raycast(element.position, direction, ignore=[element], distance=distance)
        if ray.hit:
            return ray.entity
    except Exception as ex:
        pass
    return None


def update():

    global is_edit_mode
    global timer_counter
    global update_interval
    global is_game_over

    if is_game_over or game.paused:
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
                    # This if and break affect the performance - consider fixing it
                    if (collided_entity.entity_type == bullet.owner.entity_type 
                        or collided_entity.entity_type == EntityType.BOSS and bullet.owner.entity_type == EntityType.ENEMY_TANK
                        or collided_entity.entity_type == EntityType.ENEMY_TANK and bullet.owner.entity_type == EntityType.BOSS):
                        break
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
        print("Edit mode:", is_edit_mode)


app.run()
