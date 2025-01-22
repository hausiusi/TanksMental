from abc import ABC, abstractmethod
from ursina import *
import pygame
import pprint
import os

class BaseController(ABC):
    @abstractmethod
    def initialize_controller(self):
        pass

    @abstractmethod
    def get_buttons_state(self, player_index: int = 0):
        pass

    @abstractmethod
    def controllers_count(self):
        pass


class PS4Controller(BaseController):
    def initialize_controller(self):
        pygame.init()
        pygame.joystick.init()
        self.controllers = []
        self.states = []

        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.controllers.append(joystick)
            
            # Initialize states for each joystick
            buttons_state = {j: False for j in range(joystick.get_numbuttons())}
            hat_state = {j: (0, 0) for j in range(joystick.get_numhats())}
            axis_state = {j: 0.0 for j in range(joystick.get_numaxes())}

            self.states.append({
                "buttons": buttons_state,
                "axis": axis_state,
                "hat": hat_state
            })

    @property
    def controllers_count(self):
        return len(self.controllers)

    def refresh_buttons_state(self):
        for event in pygame.event.get():
            if event.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
                joystick_index = event.joy  # Identify which joystick sent the event
                if joystick_index >= len(self.states):
                    continue  # Ignore events from unknown joysticks
                
                joystick_state = self.states[joystick_index]
                
                if event.type == pygame.JOYAXISMOTION:
                    joystick_state["axis"][event.axis] = round(event.value, 2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    joystick_state["buttons"][event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    joystick_state["buttons"][event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    joystick_state["hat"][event.hat] = event.value

    def get_buttons_state(self, player_index: int = 0):
        if player_index >= len(self.states):
            raise ValueError(f"No joystick found for player index {player_index}")
        self.refresh_buttons_state()
        joystick_state = self.states[player_index]
        if os.name == "nt":
            return {
                "shoot": joystick_state["buttons"].get(0, False),
                "drop": joystick_state["buttons"].get(1, False),
                "up": joystick_state["buttons"].get(11, False),
                "down": joystick_state["buttons"].get(12, False),
                "left": joystick_state["buttons"].get(13, False),
                "right": joystick_state["buttons"].get(14, False),
                "previous_bullet": joystick_state["buttons"].get(9, False),
                "next_bullet": joystick_state["buttons"].get(10, False),
                "pause": joystick_state["buttons"].get(6, False)
            }
        elif os.name == "posix":
            return {
                "shoot": joystick_state["buttons"].get(0, False),
                "drop": joystick_state["buttons"].get(1, False),
                "up": joystick_state["hat"][0][1] == 1,
                "down": joystick_state["hat"][0][1] == -1,
                "left": joystick_state["hat"][0][0] == -1,
                "right": joystick_state["hat"][0][0] == 1,
                "previous_bullet": joystick_state["buttons"].get(4, False),
                "next_bullet": joystick_state["buttons"].get(5, False),
                "pause": joystick_state["buttons"].get(9, False)
            }
    

class KeyboardController(BaseController):
    def initialize_controller(self):
        pass

    @property
    def controllers_count(self):
        return 1 # Keyboard controller is always 1

    def get_buttons_state(self, player_index: int = 0):
        ret = {}
        ret['shoot'] = held_keys['space'] == 1
        ret['drop'] = held_keys['p'] == 1
        ret['up'] = held_keys['w'] == 1
        ret['down'] = held_keys['s'] == 1
        ret['left'] = held_keys['a'] == 1
        ret['right'] = held_keys['d'] == 1
        ret['previous_bullet'] = held_keys['u'] == 1
        ret['next_bullet'] = held_keys['i'] == 1
        ret['pause'] = held_keys['escape'] == 1
        return ret

if __name__ == '__main__':
    ps4ctrl = PS4Controller()
    ps4ctrl.initialize_controller()
    while True:
        state = ps4ctrl.get_buttons_state()
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(ps4ctrl.states)
        #pp.pprint(state)
        os.system('clear')