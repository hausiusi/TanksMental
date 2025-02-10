from ursina import *
import pytmx
from src.enums import *
import os
from src.widgetry.drops import randomize_drop

class TileLoader:
    def __init__(self, game, tile_size):
        self.game = game
        self.tile_size = tile_size

    @staticmethod
    def get_tile_prop(tile_props:dict, prop_name, type:Enum):
        try:
            return type(tile_props.get(prop_name))
        except Exception as ex:
            return None
        
    def load(self, tmx_file,):
        game = self.game
        tile_size = self.tile_size
        self.tmx_data = pytmx.TiledMap(tmx_file)
        map_width = self.tmx_data.width
        map_height = self.tmx_data.height

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                    tile_texture = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile_texture:
                        tile_texture, *_ = tile_texture
                        world_x = 0.5 + (x - map_width / 2) * tile_size
                        world_y = -0.5 - (y - map_height / 2) * tile_size
                        name = os.path.splitext(os.path.basename(tile_texture))[0]
                        name = f"{name}_{x}_{y}"
                        durability = tile_props.get("durability")
                        takes_hit = tile_props.get("takes_hit")
                        damaging = tile_props.get("damaging")
                        collision_effect = self.get_tile_prop(tile_props, "collision_effect", CollisionEffect)
                        entity_type=self.get_tile_prop(tile_props, "entity_type", EntityType)
                        
                        effect_strength = tile_props.get("effect_strength")
                        tile = Entity(
                            name=name,
                            model='quad',
                            entity_type=entity_type,
                            z = 0.001,
                            texture=Texture(tile_texture, 'mipmap'),      
                            scale=(game.tile_size - 0.001, game.tile_size - 0.001),
                            position=(world_x, world_y),
                            collider='box',
                            durability=durability,
                            takes_hit=takes_hit,
                            damaging=damaging,
                            collision_effect=collision_effect,
                            effect_strength=effect_strength,
                            render_queue=1,
                            color = color.Color(1,1,1,1)
                        )

                        tile.on_destroy = lambda t=tile: game.remove_terrain_entity(t)
                        game.terrain_entities.append(tile)

