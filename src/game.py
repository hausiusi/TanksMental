from ursina import *
from typing import List
from src.settings import Settings
from src.levels import load_map, get_levels_count
from src.enums import CollisionEffect, EntityType
from src.npc import NpcSpawner
from src.startmenu import StartMenu
from src.player import Player
from src.game_save import SaveManager
from src.controller import PS4Controller
from datetime import datetime

class Game:
    def __init__(self):
        self.settings = Settings()
        camera.orthographic = True
        camera.fov = self.settings.camera_fov
        window.fullscreen = self.settings.fullscreen
        window.exit_button.visible = False

        self.players = []
        self.start_menu = StartMenu(self, start_game_callback=self._start_new_game, continue_game_callback=self._continue_game)
        self.player_positions = [
            Vec2(-2, self.settings.screen_bottom),
            Vec2(2, self.settings.screen_bottom),
            Vec2(-4, self.settings.screen_bottom),
            Vec2(4, self.settings.screen_bottom),
        ]

        self.paused = False

        self.aspect_ratio = window.aspect_ratio  # Aspect ratio of the window
        self.left_edge = -0.5 * self.aspect_ratio
        self.right_edge = 0.5 * self.aspect_ratio
        self.top_edge = 0.5
        self.bottom_edge = -0.5 # The bottom edge of the screen
        self.no_barrier_entities = []
        self.over = False
        self.level_complete = False
        self.tile_size = 1
        self.terrain_entities = []
        self.active_bullets = []
        self.save_file_path = ""

        self.directions = {
            # Multiple variants for the same directions
            # With numbers
            0  : Vec3(0, 1, 0),  # Up
            1  : Vec3(1, 0, 0),  # Right
            2  : Vec3(0, -1, 0), # Down
            3  : Vec3(-1, 0, 0),  # Left
            # With keyboard letters
            'w': Vec3(0, 1, 0),  # Up
            'd': Vec3(1, 0, 0),  # Right
            's': Vec3(0, -1, 0), # Down
            'a': Vec3(-1, 0, 0),  # Left
        }

        self.level_index = 0
        self.npc_spawner = NpcSpawner(self)
        self.levels_count = get_levels_count()

        stat_items = {
            "level"         : "Level",
            "wave"          : "Wave",
            "total_waves"   : "Total waves",
            "tanks_coming"  : "Tanks coming"
        }
        
        self.stat_text_pairs = {}
        pos_y = 0.45
        pos_x = self.left_edge

        origin_x = -0.5
        for key, value in stat_items.items():
            name_text = Text(
            name=key,
            text=value,
            scale=0.6,
            position=(pos_x, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y)
            )

            value_text = Text(
            text="0",
            scale=0.6,
            position=(pos_x + 0.1, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y)
            )
            self.stat_text_pairs[key] = (name_text, value_text)
            pos_y -= 0.02
    
    def _start_new_game(self, controller_avatars: list):
        position_index = 0
        controller_id = 0
        for controller_avatar in controller_avatars:
            controller = controller_avatar.controller
            character = controller_avatar.parent.character
            player = Player(
                game=self,
                max_durability=character.max_durability,
                controller=controller,
                controller_id = controller_id,
                player_id=position_index,
                model='quad',
                texture=character.initial_texture,
                position=self.player_positions[position_index],
                z=0,
                scale=(0.8, 1),
                color=controller_avatar.parent.color,
                collider='box',
                rigidbody=True,
                is_tank=True,
                can_shoot=True,
                max_speed=character.max_speed,
                takes_hit=True,
                is_exploded=False,
                remove_counter=0,
                remove_limit=3,
            )
            if isinstance(controller, PS4Controller):
                # Increasing controller ID only for the joysticks. The keyboard doesn't require the index
                controller_id += 1
            position_index += 1
            self.players.append(player)

        self.start_menu.destroy_startmenu_elements()
        self.create_tile_map()
        self.npc_spawner.load_level_npcs(self.level_index)
        self.npc_spawner.spawn_initial_npcs()

    def _continue_game(self, save_file_path, players: List[Player], level):
        self.save_file_path = save_file_path
        for player in players:
            player.initial_position = self.player_positions[player.player_id]
            player.position = self.player_positions[player.player_id]
            self.players.append(player)
        
        self.level_index = level
        self.start_menu.destroy_startmenu_elements()
        self.create_tile_map()
        self.npc_spawner.load_level_npcs(self.level_index)
        self.npc_spawner.spawn_initial_npcs()

    def pos_text_to_pos_entity(self, pos_text):
        return Vec2((pos_text.x / self.right_edge) * self.settings.horizontal_span / 2,
                    (pos_text.y / self.top_edge) * self.settings.vertical_span / 2)

    def update_no_barrier_entities(self):
        self.no_barrier_entities = [e for e in scene.entities if hasattr(e, "collision_effect") and e.collision_effect != CollisionEffect.BARRIER]

    def update_barrier_entities(self):
        self.barrier_entities = [e for e in scene.entities if hasattr(e, "collision_effect") and e.collision_effect == CollisionEffect.BARRIER]

    def show_game_over(self):
        background = Entity(
        model='quad',
        texture='assets/images/black.png',
        scale=(5, 1),          
        #color=color.Color(1, 1, 1, 0.5),
        z=-0.04,       
        position=(0, 0)             
        )
        game_over_text = Text(
        text='Game Over',            
        scale=2,
        z=-0.03,                    
        position=(0, 0),            
        color=color.red,            
        origin=(0, 0)
        )
        self.over = True        
    
    def show_level_complete(self):
        save_manager = SaveManager()
        if self.save_file_path == "":
            date_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            self.save_file_path = f"{date_str}.json"
            save_manager.save_game(self.players, self.level_index + 1, self.save_file_path)
        self.background = Entity(
        model='quad',
        texture='assets/images/black.png',
        scale=(5.5, 1.5),
        z=-0.04,       
        position=(0, 0)             
        )
        self.level_completed_text = Text(
        text=f'Level {self.level} completed!',            
        scale=2,
        z=-0.03,                    
        position=(0, 0),            
        color=color.green,            
        origin=(0, 0)
        )

        self.press_key_text = Text(
        text='Press shoot to continue',            
        scale=0.5,
        z=-0.03,                    
        position=(0, -0.05),            
        color=color.white,            
        origin=(0, 0)
        )
        
        self.level_complete = True

    def show_you_win(self):
        background = Entity(
        model='quad',
        texture='assets/images/black.png',
        scale=(5.5, 1.5),          
        #color=color.Color(1, 1, 1, 0.5),
        z=-0.04,       
        position=(0, 0)             
        )
        game_over_text = Text(
        text='You Win!',            
        scale=2,
        z=-0.03,                    
        position=(0, 0),            
        color=color.green,            
        origin=(0, 0)
        )
        self.over = True
    
    def show_start_screen(self):
        background = Entity(
        model='quad',
        texture='assets/images/black.png',
        scale=(5.5, 1.5),          
        #color=color.Color(1, 1, 1, 0.5),
        z=-0.04,       
        position=(0, 0)             
        )

        Start = Text(
        text='Press shoot to start the game',
        scale=1,
        z=-0.03,
        position=(0, 0),
        color=color.white,
        origin=(0, 0)
        )

    def destroy_terrain_elements(self):
        for entity in self.terrain_entities:
            destroy(entity)
        self.terrain_entities = []

    def create_tile_map(self):
        level_map = load_map(self.level_index)
        for y, row in enumerate(level_map):
            for x, val in enumerate(row):
                # Position the tile such that the center is (0, 0)
                # Tile positions will be adjusted based on the grid center
                if val != 0:
                    pos_x = (x - len(row) // 2) * self.tile_size
                    pos_y = -(y - len(level_map) // 2) * self.tile_size

                    durability = 100
                    takes_hit = False
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
                        effect_strength = 40
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
                        scale=(self.tile_size - 0.001, self.tile_size - 0.001),  # Set the tile size
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
                    self.terrain_entities.append(tile)

    @property
    def level(self):
        return self.level_index + 1

    def refresh_level_stats(self, wave, total_waves, tanks_coming):
        self.stat_text_pairs['level'][1].text = f'{self.level}'
        self.stat_text_pairs['wave'][1].text = f'{wave}'
        self.stat_text_pairs['total_waves'][1].text = f'{total_waves}'
        self.stat_text_pairs['tanks_coming'][1].text = f'{tanks_coming}'

    def is_on_screen(self, entity: Entity):
        """Check if an entity is within fixed screen bounds."""
        position = entity.position
        return self.is_position_on_screen(position)

    def is_position_on_screen(self, position):
        return (
        self.settings.screen_left <= position.x <= self.settings.screen_right and
        self.settings.screen_bottom <= position.y <= self.settings.screen_top
        )

    def get_collided_entity(self, entity:Entity, direction:Vec3, distance:float):
        """Gets the entity that was collided with passed entity"""
        try:
            ray = raycast(entity.position, direction, ignore=[entity], distance=distance, debug=False)
            if ray.hit:
                return ray.entity
        except Exception as ex:
            pass
        return None
    
    def get_collided_entity_at_pos(self, entity, position, direction : Vec3, distance: float):
        try:
            ray = raycast(position, direction, ignore=[entity], distance=distance, debug=False)
            if ray.hit:
                return ray.entity
        except Exception as ex:
            pass
        return None
    
    def get_collided_entities_at_position(self, entity: Entity, position):
        """
        This method is a working alternative and workaround for raycasting that doesn't work with
        entities that are already on NOT barrier surface
        """
        collided_entities = []

        # Save the original position of the entity
        original_position = entity.position

        # Temporarily move the entity to the desired position
        entity.position = position

        # Check for collisions at the new position
        for e in scene.entities:
            if entity != e and e.collider:
                if entity.intersects(e).hit:
                    collided_entities.append(e)

        # Restore the entity's original position
        entity.position = original_position

        return collided_entities
    
    def spawn(self, entity):
        if self.over:
            return
        
        if entity.entity_type == EntityType.PLAYER_TANK:
            entity.position = entity.initial_position
            print("Player has been recovered")
            return

        positions = list(range(self.settings.screen_left, self.settings.screen_right))
        random.shuffle(positions)
        
        for i in positions:
            position = (i, self.settings.screen_top)
            entity.position = position
            collided_entities = self.get_collided_entities_at_position(entity, position)
            if len(collided_entities) == 0:
                print("Tank has been spawned!")
                entity.visible = True
                break
    
    def get_collided_barriers(self, entity : Entity):
        colliding_entities = []
        for e in self.barrier_entities:
            if e == None:
                self.barrier_entities.remove(e)
                continue
            if entity.intersects(e):
                colliding_entities.append(e)

        return colliding_entities
