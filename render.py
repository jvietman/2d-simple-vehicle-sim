from datetime import datetime
import pygame, engine, json, math, os

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

class map(obj):
    def __init__(self, win_resolution: tuple, maptexture: str, size: list):
        """Child-class of obj specifically for displaying a map.
        
        The center of the map is the origin, meaning x,y = 0.\n
        This means right side of the map = +x and left side = -x. For y thats top = +y and bottom = -y. 

        Args:
            win_resolution (tuple): resolution of the whole window ```(width, height)```
            maptexture (str): filepath of texture
            size (list): size of map, in units
        """
        # super class constructor
        obj.__init__(self, win_resolution, {"default": maptexture}, [0, 0], size, 0)
        
    def update(self, size: tuple, pos: tuple, scale: tuple):
        """Render map pos and size on screen.\n

        Args:
            size (tuple): width and height of units captured on camera
            pos (tuple): topleft position of camera on map
            scale (tuple): x and y scale from camera zoom (units -> pixels)
        """
        
        self.image = pygame.Surface(self.res, pygame.SRCALPHA)
        # value that gets subtracted from the positions to match the rules of the map (center origin)
        # left side = +x & right side = -x
        # top side = +y & bottom side = -y
        # center (origin) of map, where x,y = 0: x = width/2 & y = height/2
        origin = (self.size[0]/2, self.size[1]/2)
        
        # camera position on map from origin
        cam_on_map = ((-pos[0]-origin[0]+size[0]/2)*scale[0], (-pos[1]-origin[1]+size[1]/2)*scale[1])
        
        # the frame, which units are visible to cam
        display_size = (self.size[0]*scale[0], self.size[1]*scale[1]) # first calculate whats visible, units -> pixels
        
        self.image.blit(pygame.transform.scale(self._textures["default"], display_size), cam_on_map, (0, 0, display_size[0], display_size[1]))
        self.rect = self.image.get_rect()

def move_direction(pos, direction_deg, distance) -> list:
    """
    Move from an initial position (x, y) by a certain distance in a specified direction.
    
    :param x: Initial x-coordinate.
    :param y: Initial y-coordinate.
    :param direction_deg: Direction in degrees (0° is along the positive x-axis, increasing clockwise).
    :param distance: Distance to move.
    :return: Tuple (new_x, new_y) representing the new position.
    """
    # Convert direction from degrees to radians
    direction_rad = math.radians(direction_deg-90)
    
    x, y = pos
    # Calculate new coordinates
    new_x = x + distance * math.cos(direction_rad)
    new_y = y + distance * math.sin(direction_rad)
    
    return [new_x, new_y]

class render:
    def __init__(self, size: tuple, cam_pos = [0, 0], cam_zoom = 10):
        # setup
        self.size = size
        self.ratio = size[0]/size[1]
        self.screen = pygame.display.set_mode(size)
        
        # power curve rendering
        self.graph_scale = (1, 1)
        
        # renderer values
        self.cam_pos = cam_pos # middle of camera
        self.cam_zoom = cam_zoom # units in height displayed on screen. width is calculated automatically
        # sprite (object) rendering
        self.all_sprites = pygame.sprite.Group()
        self.objects = {}
        
        # performance debugging
        self._frames = 0 # counted frames in timeframe
        self._fps_short = 0 # fps counted in 0.2 seconds
        self._fps_short_counted = 1
        self._fps_begin = datetime.now() # start time of counting for 0.2 seconds
        self._fps_prev = 0
        self.fps = 0
        
        # graph display, temporary values
        self._graph_y_size = 10
        self._graph_trail_length = 100
        self._tmp_graph_prev = [(-1, -1)]

    # object operations
    def add_object(self, name: str, obj: obj):
        if name in self.objects:
            raise Exception("Object with this name already exists.")
        else:
            self.objects[name] = obj
            self.all_sprites.add(obj)
    
    def get_object(self, name: str) -> obj:
        return self.objects[name]
    
    def move_object(self, name: str, pos: tuple) -> tuple:
        o = self.objects[name]
        o.pos = [o.pos[0]+pos[0], o.pos[1]+pos[1]]
        return o.pos
    
    def move_object_straight(self, name: str, step: int)  -> tuple:
        o = self.objects[name]
        o.pos = move_direction(o.pos, o.rotation, step)
        return o.pos
    
    def rotate_object(self, name: str, degrees: int) -> int:
        o = self.objects[name]
        o.rotation += degrees
        if o.rotation < 0:
            o.rotation += 360
        if o.rotation > 359:
            o.rotation -= 360
        return o.rotation

    # debugging: power curves
    def power_curve(self, e: engine, step = 1):
        """Calculate and render powercurve.
        
        This method clears the whole screen and calculates and render the powercurve from scratch.
        Because we are doing everything from scratch, calling this method too often may cause performance issues, depending on the scaling.

        Args:
            e (engine): Reference to engine
        """
        self.screen.fill((0, 0, 0))

        scale = self.graph_scale
        
        # scaling
        # steps
        prev, now = (0, self.size[1]), (0, 0)
        for i in range(int(( e._graphs_limits[-1] * scale[0] ) / step)):
            now = (int(i*step), int(self.size[1] - (e._point_at_graph((i/scale[0])*step) * scale[1])))
            pygame.draw.line(self.screen, (0, 0, 255), prev, now, 4)
            prev = now
            
    def set_graph_scale(self, e: engine, size: tuple, step = 1):
        """Set the scale of the graph rendered by giving it width and height in pixels.
        
        Method does not return value, but saves the scale in the ```self._graph_scale``` tuple.

        Args:
            e (engine): Reference to engine
            size (tuple): Width and height in pixels
        """
        
        # calculate x scale
        w = size[0] / e._graphs_limits[-1]
        
        # get maximum
        max = 0
        for i in range(0, int((e._graphs_limits[-1]*w)/step)):
            y = e._point_at_graph((i/w)*step)
            max = y if y > max else max
        
        # calculate y scale and save
        self.graph_scale = (w, size[1] / max)
    
    # debug values: fps
    def _update_frames(self):
        """Updates the framerate value.
        
        Framerate is safed in the ```fps``` variable of this class. The fps value is rounded to the first decimal place.
        
        There are two types of fps values here:
        - fps short: quick, but low accuracy value: the frames rendered in 0.2 seconds
        - fps long: slow, but high accuracy value: the frames rendered in 1 second
        
        The fps is a combination of the short and long fps values. Depending on how many short fps youve counted, thats the percentage of whats added from short fps and what from long fps:
            fps = long_fps*(1-(0.2*short_counted)) + short_fps
        
        For example, if the short fps was counted 3 times, that means we have the fps value for 0.6 seconds, we add only 40% of the long fps.
        This results in a smooth, semi-accurate but quicker fps value.
        
        """
        self._frames += 1
        
        elapsed = (datetime.now()-self._fps_begin).total_seconds()
        if elapsed > 0.2*self._fps_short_counted:
            self._fps_short = self._frames
            self._fps_short_counted += 1
        if self._fps_short_counted > 5:
            self._fps_prev = self._frames
            self._fps_short_counted = 1
            self._fps_short = self._frames = 0
            self._fps_begin = datetime.now()
        
        self.fps = round(self._fps_prev*(1-(0.2*self._fps_short_counted)) + self._fps_short, 1)    
    
    # actual renderer shit
    def get_events(self) -> list[pygame.event.EventType]:
        return pygame.event.get()
        
    def update_graph(self, x=-1, y=-1):
        self._update_frames()
        
        prev = self._tmp_graph_prev[0]
        if not x == -1:
            pygame.draw.line(self.screen, (0, 0, 0), (0, 0), (self.size[0], 0), 20)
            pygame.draw.line(self.screen, (255, 0, 0), (int(x), 0), (int(x), 10), 5)
        if not y == -1:
            px, py = x-self._graph_y_size/2, self.size[1]-(y-self._graph_y_size/2)*self.graph_scale[1]
            pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(px, py, self._graph_y_size, self._graph_y_size), self._graph_y_size)
            
        
        self._tmp_graph_prev.append((x, y))
        if len(self._tmp_graph_prev) > self._graph_trail_length:
            if not prev[1] == -1:
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(prev[0]-self._graph_y_size/2, self.size[1]-((prev[1]-self._graph_y_size/2)*self.graph_scale[1]), self._graph_y_size, self._graph_y_size), self._graph_y_size)
            del prev
        
        pygame.display.update()
    
    def render(self):
        self._update_frames()

        scale = (self.size[0] / (self.cam_zoom*self.ratio), self.size[1] / self.cam_zoom)
        # for i in self.objects.values():
        #     i._img = pygame.Surface((i.size[0]*scale[0], i.size[1]*scale[1]))
        #     i._img.blit(i._textures[i.state], (0, 0))
        
        #     i._rect = i._img.get_rect()
        #     i._rect.x, i._rect.y = (200, 200)
            
            # i._rect.x, i._rect.y = ((i.pos[0]-self.cam_pos[0])*scale[0], (i.pos[1]-self.cam_pos[1])*scale[1])
        
        for j in self.objects.keys():
            i = self.objects[j]
            if j == "map":
                i.update(((self.cam_zoom*self.ratio), self.cam_zoom), self.cam_pos, scale)
            else:
                size = ((i.size[0]*scale[0]), i.size[1]*scale[1])
                pos = ((i.pos[0]-self.cam_pos[0]+(self.size[0]/scale[0])/2)*scale[0], (i.pos[1]-self.cam_pos[1]+(self.size[1]/scale[1])/2)*scale[1])
                outside_cam = pos[0] < -size[0] or pos[0]-size[0]/2 > self.size[0] or -size[1] > pos[1] or pos[1]-size[1]/2 > self.size[1]
                i.update(pos, size, outside_cam)
        self.all_sprites.draw(self.screen)
        pygame.display.update()