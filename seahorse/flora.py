"""Ocean floor things to hide behind."""

import pygame
import random

from dataclasses import dataclass, field
from typing import List
from colors import Colors

from image import Images

@dataclass
class Flora():
    """Places to hide."""

    pos_x: int = 0
    pos_y: int = 0
    size_x: int = 0
    size_y: int = 0
    variety: int = 0
    size_multiple: int = 1
    block_size: int = 0

    img: pygame.Surface = None
    draw_area: pygame.Rect = None

    def __post_init__(self):
        """Randomize self."""
        self.img = pygame.image.load(Images.get_path(r'flora.purple.png'))

        # Size
        self.block_size = self.size_multiple * 32
        self.size_x = self.block_size * 2
        self.size_y = self.block_size * 2
        self.img = pygame.transform.scale(self.img, (int(self.size_x), int(self.size_y)))

        # Pick which variety we are.
        self.draw_area = pygame.Rect(self.variety * self.block_size,
                                     0,
                                     (self.variety + 1) * self.block_size,
                                     self.block_size)

    def draw(self, screen):
        """Draw self on the screen."""
        pygame.draw.rect(screen, Colors.WHITE,
                         [self.pos_x, self.pos_y, self.size_x, self.size_y])
        screen.blit(self.img, (self.pos_x, self.pos_y), area=self.draw_area)
    
    def logic(self):
        """Pass"""
        pass
