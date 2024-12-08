Copyright 2024 Sipho Zuma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

import pygame

class Controls:
    def __init__(self):
        pygame.joystick.init()
        self.joystick = self._initialize_joystick()

        self.SPACE = "SPACE"
        self.UP = 'UP',
        self.DOWN = 'DOWN',
        self.LEFT = 'LEFT',
        self.RIGHT = 'RIGHT'
        self.SELECT = 'SELECT'
        self.ESCAPE = 'ESCAPE'

        
        self.key_map = {
            pygame.K_UP: 'UP',
            pygame.K_DOWN: 'DOWN',
            pygame.K_LEFT: 'LEFT',
            pygame.K_SPACE: 'SPACE',
            pygame.K_RIGHT: 'RIGHT',
            pygame.K_RETURN: 'SELECT',
            pygame.K_ESCAPE: 'ESCAPE'
        }
        
        self.dpad_button_map = {
            11: 'UP',
            12: 'DOWN',
            13: 'LEFT',
            14: 'RIGHT',
            0: 'SELECT',
            1: 'ESCAPE'
        }
        
        self.pressed = set()
        self.just_pressed = set()
        self.just_released = set()

    def _initialize_joystick(self):
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Joystick connected: {joystick.get_name()}")
            return joystick
        else:
            print("No joystick connected.")
            return None

    def update(self, events):
        self.just_pressed.clear()
        self.just_released.clear()

        for event in events:
            if event.type == pygame.KEYDOWN:
                action = self.key_map.get(event.key)
                if action:
                    self.pressed.add(action)
                    self.just_pressed.add(action)
            elif event.type == pygame.KEYUP:
                action = self.key_map.get(event.key)
                if action:
                    self.pressed.discard(action)
                    self.just_released.add(action)
            elif event.type == pygame.JOYBUTTONDOWN and self.joystick:
                action = self.dpad_button_map.get(event.button)
                if action:
                    self.pressed.add(action)
                    self.just_pressed.add(action)
            elif event.type == pygame.JOYBUTTONUP and self.joystick:
                action = self.dpad_button_map.get(event.button)
                if action:
                    self.pressed.discard(action)
                    self.just_released.add(action)

    def is_pressed(self, action):
        return action in self.pressed

    def is_just_pressed(self, action):
        return action in self.just_pressed

    def is_just_released(self, action):
        return action in self.just_released
