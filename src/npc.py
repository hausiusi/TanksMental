from ursina import *
from src.tank import Tank
from src.levels import load_npcs
from src.enums import EntityType
from src.iq import *

class EnemyTank(Tank):
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        self.game = game
        self.least_interval_between_bullets = 0.2
        self.bullet_interval_counter = 0
        self.npc_config = NPCIqConfig(NPCMissionType.FIND_AND_DESTROY_PLAYER, NPCBehaviour.SHOOT_DEFAULT_BULLET, visibility=180, distance=10)
        self.npc_iq = NPCIntelligence(self, self.npc_config)
        self.direction_vector = Vec3(0, -1, 0) # Pointing down

    def update(self):
        if self.game.paused:
            return


        self.direction_vector = self.npc_iq.get_direction()

        # Attempt to move the tank in its current direction
        self.move(self.direction_vector)

        self.bullet_interval_counter += time.dt

        if (self.bullet_interval_counter > self.least_interval_between_bullets 
            and not self.is_exploded):                
            self.ammunition.shoot_bullet(False)
            self.bullet_interval_counter = 0
            self.health_bar.update_health(self.health)

        super().update()

class NpcSpawner:
    def __init__(self, game):
        self.game = game
        self.load_level_npcs(self.game.level_index)

    def load_level_npcs(self, level):
        self.npc_pools = load_npcs(level)
        self.spawned_count = 0
        self.npc_pool_index = 0
        self.npcs_on_battlefield = 0
        self.total_npcs = 0
        for pool in self.npc_pools:
            self.total_npcs += pool['count']

    def __load_npc_pool(self, index):
        if len(self.npc_pools) <= index:
            return False
        
        self.npc_pool = self.npc_pools[index]
        self.max_npcs_at_once = self.npc_pool['at_once']
        self.npcs_available = self.npc_pool['count']
        return True

    def spawn_initial_npcs(self):
        if not self.__load_npc_pool(self.npc_pool_index):
            return

        while self.spawned_count < self.max_npcs_at_once and self.npcs_available > 0:
            spawn_count = min(self.npcs_available, self.max_npcs_at_once - self.spawned_count)
            for i in range(spawn_count):
                enemy_tank = self.create_npc()
                self.game.spawn(enemy_tank)
                self.spawned_count += 1
                self.npcs_on_battlefield += 1
                self.npcs_available -= 1

                if self.npcs_available == 0:  # NPC pool is empty
                    self.npc_pool_index += 1
                    if not self.__load_npc_pool(self.npc_pool_index):
                        break

    def spawn_more(self):
        self.npcs_on_battlefield -= 1
        if self.npcs_available == 0:
            index = self.npc_pool_index + 1
            if self.__load_npc_pool(index): # Ensure that no more NPCs are spawned than the maximum allowed
                self.npc_pool_index = index
            else:
                return
            
        if self.npc_pool['at_once'] <= self.npcs_on_battlefield:
            return
        enemy_tank = self.create_npc()
        self.game.spawn(enemy_tank)
        self.spawned_count += 1
        self.npcs_available -= 1
        self.npcs_on_battlefield += 1
        print(f"Spawned {enemy_tank.name}. In total {self.spawned_count} NPCs spawned. There are {self.npcs_available} left in the pool")

    def level_complete(self):
        self.game.show_level_complete()
    
    def create_npc(self) -> Entity:
        enemy_tank = EnemyTank(
                name=f'EnemyTank{self.spawned_count}',
                entity_type=self.npc_pool['entity_type'],
                game=self.game,
                max_durability=self.npc_pool['max_durability'],
                model='quad',
                texture=self.npc_pool['texture'],
                visible=False,
                z=0,
                scale=self.npc_pool['scale'],
                color=self.npc_pool['color'],
                collider='box',
                rigidbody=True,
                takes_hit=True,
                is_tank=True,
                can_shoot=True,
                max_speed=self.npc_pool['max_speed'],
                direction=0,
                is_exploded=False,
                remove_counter=0,
                remove_limit=1,
            )
        enemy_tank.ammunition.choose_bullet_pool(self.npc_pool['chosen_bullet'])
        enemy_tank.ammunition.bullet_pool.max_bullets = self.npc_pool['max_bullets']
        enemy_tank.on_destroy=self.level_complete if enemy_tank.entity_type==EntityType.BOSS else self.spawn_more

        return enemy_tank