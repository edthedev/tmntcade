"""Player handler."""

from dataclasses import dataclass, field
from typing import List

import pygame

# from text import TextPrint
from controls import ControlSet
from sandwich import Sandwich
from colors import Colors
from laser import Laser

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# Joystick X / Y Axis
JOY_X = 0
JOY_Y = 1

@dataclass
class PlayerImages():
    """Images of a NutNik"""
    default: str
    jumping: str
    falling: str = ''
    eating: str = ''

@dataclass
class Player():
    """A game player.

    >>> Player(start_x=9001).pos_x
    9001

    >>> Player(start_x=9001).pos_y
    100
    """
    controls: List[ControlSet] = field(default_factory=list)
    pos_x: int = 100
    pos_y: int = 100
    size_x: int = 50
    size_y: int = 50
    move_amt: int = 5
    color: tuple = Colors.RED
    jumping: int = 0
    falling: int = 0
    jump_max: int = 500 # this will change during play
    ground_y: int = 0 # override this!
    has_sandwich: int = 0
    fatten_x: int = 10
    fatten_y: int = 5
    fat_count: int = 50
    launched: int = 0
    images: PlayerImages = None
    max_x: int = 100
    start_x: int = 100
    secret_keys: int = 1
    lasering: int = 0
    laser: Laser = None

    def __post_init__(self):
        """Set pos_x to start_x"""
        self.pos_x = self.start_x

    def logic(self):
        """Do player game logic."""

        # Can't jump forever.
        if self.jumping and self.pos_y < self.ground_y - self.jump_max + self.size_x:
            self.jumping = 0
            self.falling = 1

        if self.falling and self.pos_y > self.ground_y - self.size_y:
            self.falling = 0

        if self.jumping:
            self.pos_y -= self.move_amt

        if self.falling:
            self.jumping = 0 # Supports voluntary fall.
            self.pos_y += self.move_amt

        if self.launched:
            self.pos_y -= 1.5*(self.move_amt)

        # Can't Launch forever
        if self.launched and self.pos_y < self.ground_y - 3*(self.jump_max):
            self.launched = 0
            self.falling = 1

        if self.lasering > 0:
            self.lasering -= 1
            if self.laser is None:
                self.laser = Laser(size_y=self.ground_y, pos_y=0)
            self.laser.pos_x = self.pos_x + self.size_x / 2
            self.laser.size_y = self.pos_y
        else:
            self.laser = None

    def control(self, keys=None, joystick=None):
        """Look for signals accepted by this player, and apply them.

        Return True if the player fired.
        """
        if keys:
            return self._key_control(keys)
        if joystick:
            return self._joy_control(joystick)

    def _joy_control(self, joystick):
        """Apply joystick controls.

        Only pass in the joystick you want to have accepted.
        Return True if the player fired.
        """
        fired = False
        if joystick.get_axis(JOY_Y) >= .8:
            # self.text_print.print(self.screen,
            # "Joystick DOWN: {}".format(joystick.get_axis(JOY_Y)))
            self._down()
        if joystick.get_axis(JOY_Y) <= -.8:
            # self.text_print.print(self.screen,
            # "Joystick UP: {}".format(joystick.get_axis(JOY_Y)))
            self._up()
        if joystick.get_axis(JOY_X) >= .8:
            # self.text_print.print(self.screen,
            # "Joystick RIGHT: {}".format(joystick.get_axis(JOY_X)))
            self._right()
        if joystick.get_axis(JOY_X) <= -.8:
            # self.text_print.print(self.screen,
            # "Joystick LEFT: {}".format(joystick.get_axis(JOY_X)))
            self._left()
        if joystick.get_button(0):
            # self.text_print.print(self.screen, "Player fired!")
            fired = True
        return fired

    def collide(self, other):
        """Detect a collision.

        >>> Player(start_x=500,pos_y=500).collide(Player(start_x=500,pos_y=500))
        True

        >>> Player(start_x=500,pos_y=500).collide(Player(start_x=500,pos_y=0))
        False

        >>> Player(start_x=500,pos_y=500).collide(Player(start_x=0,pos_y=500))
        False

        >>> Player(start_x=510,pos_y=500).collide(Player(start_x=500,pos_y=500))
        True

        >>> Player(start_x=510,pos_y=500,lasering=0).collide(Player(start_x=500,pos_y=30))
        False

        >>> Player(start_x=510,pos_y=500,lasering=30).collide(Player(start_x=500,pos_y=30))
        True
 
        """
        if self.lasering:
            return self.inline_with(other)
        return (
            self.pos_x-self.size_x <= other.pos_x + other.size_x and
            self.pos_y - self.size_y <= other.pos_y and
            self.pos_x+self.size_x >= other.pos_x+other.size_x and
            self.pos_y + self.size_y >= other.pos_y
        )

    def fatten(self):
        """Get fatter."""
        self.fat_count += 10

    def _up(self):
        """Start a jump."""
        if not self.falling and not self.jumping \
            and not (self.lasering > 0):
            self.jumping = 1
            self.fat_count -= 1  # Starting a jump costs your fat.

    def _down(self):
        """Interrupt a jump. - New experimental feature...might remove this."""
        self.falling = 1
        if self.secret_keys > 0:
            self.lasering = 200
            self.secret_keys -= 1

        ## Eat to get fatter.
        if self.has_sandwich > 0:
            self.has_sandwich = 0
            self.fatten()

    def _left(self):
        """Move self left."""
        if self.jumping or self.falling:
            self.pos_x -= (self.move_amt / 2)
        elif self.launched:
            self.pos_x -= (self.move_amt / 3)
        else:
            self.pos_x -= self.move_amt
        if self.pos_x < -50:
            self.pos_x = -50

    def _right(self):
        """Move self right."""
        if self.jumping or self.falling:
            self.pos_x += (self.move_amt / 2)
        elif self.launched:
            self.pos_x += (self.move_amt / 3)
        else:
            self.pos_x += self.move_amt
        if self.pos_x > self.max_x + 50:
            self.pos_x = self.max_x + 50

    def _key_control(self, keys):
        """Apply keyboard controls - as accepted by this player.
        Return True if the player fired.
        """
        fired = False
        for control_set in self.controls:
            if keys[control_set.up_key]:
                self._up()
            if keys[control_set.down_key]:
                self._down()
            if keys[control_set.left_key]:
                self._left()
            if keys[control_set.right_key]:
                self._right()
        if keys[pygame.K_SPACE]:
            fired = True
        return fired

    def draw(self, screen):
        """Draw the player."""

        if self.fat_count < 30:
            self.fat_count = 30

        self.size_x = self.fat_count
        self.size_y = self.fat_count * 2 / 3

        img = None

        if self.jumping:
            img = pygame.image.load(self.images.jumping)
        else:
            img = pygame.image.load(self.images.default)
        img = pygame.transform.scale(img, (int(self.size_x), int(self.size_y)))

        #pygame.draw.rect(screen, WHITE,
        #                 [self.pos_x, self.pos_y, self.size_x, self.size_y])
        # pygame.draw.rect(screen, self.color,
        #                [self.pos_x + 10, self.pos_y + 10, self.size_x - 10, self.size_y - 10])

        screen.blit(img, (self.pos_x, self.pos_y))
        # self.text_print.indent()
        # self.text_print.print(screen, "Player message: {}".format(self.debug))

        if self.has_sandwich:
            Sandwich.draw(screen, self.pos_x,
                          pos_y=self.pos_y - Sandwich.sandwich_tall)


    def land_on(self, pad):
        """Detect if we landed on a launcher.

        >>> Player().land_on(Player())
        False

        >>> Player(pos_y=90, size_y=10).land_on(Player(pos_y=100, size_y=10))
        True
        """
        bottom_of_self = self.pos_y + self.size_y
        margin = 3
        return (
            self.inline_with(pad)
            and pad.pos_y - margin < bottom_of_self
            and bottom_of_self < pad.pos_y + margin
        )

    def inline_with(self, other):
        """Return true if lined up in a vertical column with player.

        >>> Player().inline_with(Player())
        True

        >>> Player(start_x=20, size_x=10).inline_with(Player(start_x=15, size_x=10))
        True

        >>> Player(start_x=200, size_x=10).inline_with(Player(start_x=15, size_x=10))
        False

        >>> Player(pos_y=100,size_y=10).inline_with(Player(pos_y=90))
        True
        """
        # return (
        #     pad.pos_x + pad.size_x > self.pos_x
        #    and pad.pos_x < self.pos_x + self.size_x
        #)
        return (
            # Left Edge of Other within self
            other.pos_x >= self.pos_x
            and other.pos_x <= self.pos_x + self.size_x
            or
            # Right Edge of Other within self
            other.pos_x + other.size_x >= self.pos_x
            and other.pos_x + other.size_x <= self.pos_x + self.size_x
        )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
