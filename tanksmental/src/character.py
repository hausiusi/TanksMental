# File contains the player characters properties

class PlayerCharacter:
    max_speed = 0
    max_durability = 0
    bullets = [] # Add enums
    move_audio = None # Add enums
    initial_texture = None

class IronGuard(PlayerCharacter):
    '''Standard tank. Medium speed, medium damage, medium durability'''
    max_speed = 2
    max_durability = 100
    initial_texture = 'assets/images/player_tank.png'

class TrailBlazer(PlayerCharacter):
    '''Light tank. Fast, low damage, low durability'''
    max_speed = 4
    max_durability = 50
    initial_texture = 'assets/images/mortar_carrier.png'
