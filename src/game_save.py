import os
from src.player import Player
from src.ammunition import AmmoCatalog, BulletPool
from typing import List, Optional, Tuple
from src.misc.utils import json_load, json_save
from src.controller import PS4Controller

class SaveManager:
    def __init__(self):
        self.saves = []

    def get_saves(self):
        # TODO: Use it (load saved games on init) in startmenu or remove
        return self.saves
    
    def save_game_to_dict(self, players: List[Player], level: int) -> dict:
        data_to_save = {
            "players": [],
            "level" : 0
        }

        for player in players:
            ammunition_to_save = {
                "bullet_pools": [],
                "deploy_pool" : [],
            }
            for bullet_pool in player.ammunition.bullet_pools:
                pool_to_save = {
                    "hit_damage" : bullet_pool.hit_damage,
                    "bullet_speed" : bullet_pool.bullet_speed,
                    "max_bullets" : bullet_pool.max_bullets,
                }
                ammunition_to_save["bullet_pools"].append(pool_to_save)

            for key, deployable in player.ammunition.deploy_pool.deployables.items():
                deployable_to_save = {
                    "name" : key,
                    "items_count" : deployable.items_count 
                }
                ammunition_to_save["deploy_pool"].append(deployable_to_save)
            player_to_save = {
                "player_id": player.player_id,
                "max_speed": player.max_speed,
                "durability": player.durability,
                "max_durability" : player.max_durability,
                "initial_texture": player.initial_texture,
                "kills" : player.kills,
                "tanks_damage" : player.tanks_damage_dealt,
                "other_damage" : player.other_damage_dealt,
                "deaths" : player.deaths,
                "color" : player.color,
                "ammunition" : ammunition_to_save,
            }
            data_to_save["players"].append(player_to_save)
            data_to_save["level"] = level

        return data_to_save
    
    def save_game_to_file(self, players: List[Player], level: int, file: Optional[str]=None):
        file = os.path.join('saves', 'game', file)    
        data_to_save = self.save_game_to_dict(players=players, level=level)

        json_save(data_to_save, file)

    def load_game_from_dict(self, game, data, controllers) -> Tuple[List[Player], int]:
        def get_player_controller_and_index(requested_index):
            cumulative_index = 0
            for controller in controllers:
                tmp = cumulative_index
                cumulative_index += controller.controllers_count
                if cumulative_index > requested_index:
                    # Calculate the local index within this controller
                    local_index = requested_index - tmp
                    return controller, local_index
            return None

        players = []
        for i, player_props in enumerate(data['players']):
            controller, controller_id = get_player_controller_and_index(i)
            id = player_props['player_id']
            player = Player(
                    game=game,
                    max_durability=player_props['max_durability'],
                    controller=controller,
                    controller_id=controller_id,
                    player_id=id,
                    model='quad',
                    texture=player_props['initial_texture'],
                    z=0,
                    scale=(0.8, 1),
                    color=player_props['color'],
                    collider='box',
                    rigidbody=True,
                    is_tank=True,
                    can_shoot=True,
                    max_speed=player_props['max_speed'],
                    takes_hit=True,
                    is_exploded=False,
                    remove_counter=0,
                    remove_limit=3,
                    name = f"Player{id}"
                )
            
            player.durability = player_props['durability']
            player.kills = player_props['kills']
            player.tanks_damage_dealt = player_props['tanks_damage']
            player.other_damage_dealt = player_props['other_damage']

            ammunition = player.ammunition
            ammunition.bullet_pools
            for i, pool_props in enumerate(player_props['ammunition']["bullet_pools"]):
                if len(ammunition.bullet_pools) < i:
                    print(f"Error: ammocatalog pool size is {i}, can't add modify on index {i}")
                pool : BulletPool = ammunition.bullet_pools[i]
                pool.max_bullets = pool_props['max_bullets']
                pool.hit_damage = pool_props['hit_damage']
                pool.bullet_speed = pool_props['bullet_speed']
            ammunition.deploy_pool.recover_from_save(player_props['ammunition']['deploy_pool'])

            players.append(player)
        return players, data['level']

    def load_game_from_file(self, game, save, controllers):
        """Returns players with their state and the level that they reached"""
        data = json_load(file_path=save)
        return self.load_game_from_dict(game, data, controllers)

        
