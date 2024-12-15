import pygame

class Controls:
    def __init__(self):
        pygame.joystick.init()
        self.joystick = self._initialize_joystick()

        self.SPACE = "SPACE"
        self.UP = 'UP'
        self.DOWN = 'DOWN'
        self.LEFT = 'LEFT'
        self.RIGHT = 'RIGHT'
        self.SELECT = 'SELECT'
        self.ESCAPE = 'ESCAPE'
        self.MOUSE_LEFT = "MOUSE_LEFT"
        self.MOUSE_RIGHT = "MOUSE_RIGHT"
        
        self.key_map = {
            pygame.K_UP: 'UP',
            pygame.K_DOWN: 'DOWN',
            pygame.K_LEFT: 'LEFT',
            pygame.K_SPACE: 'SPACE',
            pygame.K_RIGHT: 'RIGHT',
            pygame.K_RETURN: 'SELECT',
            pygame.K_ESCAPE: 'ESCAPE',
            pygame.K_s: 'S',
            pygame.K_l: 'L'
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
        self.mouse_pos = None
        self.mouse_just_pressed = False
        self.mouse_pressed = False

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
        self.mouse_just_pressed = False

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                   self.mouse_pressed = True
                   self.mouse_just_pressed = True
                   self.pressed.add(self.MOUSE_LEFT)
                   self.just_pressed.add(self.MOUSE_LEFT)
                   self.mouse_pos = event.pos
                if event.button == 3:
                    self.pressed.add(self.MOUSE_RIGHT)
                    self.just_pressed.add(self.MOUSE_RIGHT)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
                    self.pressed.discard(self.MOUSE_LEFT)
                    self.just_released.add(self.MOUSE_LEFT)
                if event.button == 3:
                   self.pressed.discard(self.MOUSE_RIGHT)
                   self.just_released.add(self.MOUSE_RIGHT)


    def is_pressed(self, action):
        return action in self.pressed

    def is_just_pressed(self, action):
        return action in self.just_pressed

    def is_just_released(self, action):
        return action in self.just_released