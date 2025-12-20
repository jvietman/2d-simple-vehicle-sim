import pygame, json, os

class obj(pygame.sprite.Sprite):
    """**Represents an object in pygame.**\n
    
    This class holds data like textures and position data and provides an update method which ultimately renders the sprite onto the screen.\n
    An object is not just simply rendered somewhere on the screen. The screen doesnt represent the whole world,
    but rather there is a camera that displayes a certain part of an infinite world (of course not infinite but until you reach the integer limit).\n
    Scaling and position of an object on screen is determined by the renderer, but the update method provided here ultimately clears the last sprite
    and render the new sprite with its current texture and rotation on the screen.
    """
    def __init__(self, win_resolution: tuple, textures: dict, pos = [0, 0], size = [1, 1], rotation = 0):
        """
        Args:
            win_resolution (tuple): resolution of the whole window ```(width, height)```
            textures (dict): dictionary of texture names as keys and values as location of the texture file, (default has to be always included) ```{"default": "default.png"}```
            pos (list, optional): x and y position in world, in units. Defaults to [0, 0].
            size (list, optional): width and height of object in world, in units. Defaults to [1, 1].
            rotation (int, optional): rotation of object in dregrees. Defaults to 0.
        """
        # super class constructor
        pygame.sprite.Sprite.__init__(self)
        self.res = win_resolution
        
        # sizes and positions are not in specific unit, but in a rather universal unit (you can interpret units as meters, cm, km etc., up to you)
        # how big a unit is on screen is decided by the renderer
        self.pos = pos
        self.size = size
        self.rotation = rotation
        self.state = "default" # states = current texture
        # this is a universal default state which has to be included in any list of textures
        
        self._textures = {}
        for i in textures.keys():
            self._textures[i] = pygame.image.load(textures[i])
        
        # pygame sprite variables
        self.image = pygame.Surface(self.res, pygame.SRCALPHA)
        self.image.blit(self._textures[self.state], pos)
        
        self.rect = self.image.get_rect()
        
    def _scaled(self, tuple: tuple, scale: tuple):
        return (tuple[0]*scale[0], tuple[1]*scale[1])
    
    def update(self, pos: tuple, size: tuple, empty = False):
        """Render sprite on screen.\n
        
        Parameter values usually provided be the renderer, which converts objects size and position from units to pixels to be printed on screen.

        Args:
            pos (tuple): x and y position on screen (center origin), in pixels
            size (tuple): width and height on screen, in pixels
            empty (bool, optional): if object is visible on screen, decides if worth rendering. Defaults to False.
        """
        self.image = pygame.Surface(self.res, pygame.SRCALPHA)
        if not empty:
            rotated = pygame.transform.rotate(pygame.transform.scale(self._textures[self.state], size), 360-self.rotation)
            frame = max(size[0], size[1])
            tpos = (pos[0]+(frame-rotated.get_width())/2, pos[1]+(frame-rotated.get_height())/2)
            self.image.blit(rotated, tpos)
            self.rect = self.image.get_rect()

class vehicle(obj):
    def __init__(self, win_resolution: tuple, working_directory: str, pos = [0, 0], rotation = 0):
        """Child-class of obj specifically for displaying vehicles.

        Args:
            win_resolution (tuple): resolution of the whole window ```(width, height)```
            working_directory (str): path to vehicle folder that holds textures and vehicle.json
            pos (list, optional): x and y position in world, in units. Defaults to [0, 0].
            rotation (int, optional): rotation of object in dregrees. Defaults to 0.
        """
        # super class constructor
        with open(working_directory+"/vehicle.json") as f:
            self.data = json.load(f)
            f.close()
        
        os.chdir(working_directory)
        obj.__init__(self, win_resolution, self.data["textures"], pos, (self.data["width"], self.data["length"]), rotation)