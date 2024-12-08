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

from abc import ABC, abstractmethod
import pygame
from Game import Game

class GameState(ABC):
    @abstractmethod
    def enter(self, game: Game):
        pass

    @abstractmethod
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        pass

    @abstractmethod
    def _handle_actions(self, game: Game):
        pass
    
    @abstractmethod
    def update(self, game: Game):
        pass
    
    @abstractmethod
    def draw(self, game: Game):
        pass
    
    @abstractmethod
    def exit(self, game: Game):
        pass

