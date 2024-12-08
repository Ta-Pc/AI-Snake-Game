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

