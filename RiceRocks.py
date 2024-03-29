# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
rocks = set([])
missiles = set([])
explosions = set([])
locations = []
rock_count = 0
started = False

expl_time = 0
expl_loop = 0

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
# ship image

# sound assets purchased from sounddogs.com, please do not redistribute
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [85, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([192, 64], [128, 128], 17, 24, animated = True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
#explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
explosion_sound = simplegui.load_sound("https://ia601502.us.archive.org/0/items/explode1_201508/explode1.mp3")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, ang_vel, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.collide = False
        self.angle = angle
        self.ang_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def collide(self, other):
        if dist(self.pos, other.get_position()) < self.radius + other.get_radius():
            return True
   
    def turn_left(self):
        self.ang_vel -= 0.06

    def turn_right(self):
        self.ang_vel += 0.06

    def thrust_on(self):
        self.thrust = True
        ship_thrust_sound.play()
        self.image_center = ((ship_info.get_center()[0] * 3)+2, ship_info.get_center()[1])
        
    def thrust_off(self):
        self.thrust = False
        self.image_center = ship_info.get_center()
        ship_thrust_sound.rewind()
        
    def stop_turning(self):
        self.ang_vel = 0
        
    def shoot(self):
        global canvas, missiles
        missiles.add(Sprite([self.pos[0] + (math.cos(self.angle) * 36), self.pos[1] + (math.sin(self.angle) * 36)], 
                            [self.vel[0] + (self.forward[0] * 8), self.vel[1] + (self.forward[1] * 8)], 
                             0, 
                             0, 
                             missile_image, missile_info, missile_sound))
       
    def update(self):
        c = 0.02 # Friction constant 'c'
        self.forward = [math.cos(self.angle), math.sin(self.angle)] # Accel vector
        a = 0.1 # Accel factor
        self.angle += self.ang_vel
        
        # Pos update with wrapping
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
                
        # Friction update
        self.vel[0] *= (1 - c)
        self.vel[1] *= (1 - c)
        # Thrust update
        if self.thrust:
            self.vel[0] += self.forward[0] * a
            self.vel[1] += self.forward[1] * a
   
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius


# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def collide(self, other):
        if dist(self.pos, other.get_position()) < self.radius + other.get_radius():
            return True

    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        soundtrack.play()
        score = 0
        
def draw(canvas):
    global time, expl_time, started, rock_count, score, lives, missiles, rocks, expl_loop, current_explosion_center
   
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, 
                      nebula_info.get_center(), 
                      nebula_info.get_size(), 
                      [WIDTH / 2, HEIGHT / 2], 
                      [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, 
                      center, size, 
                      (wtime - WIDTH / 2, HEIGHT / 2), 
                      (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, 
                      center, size, 
                      (wtime + WIDTH / 2, 
                       HEIGHT / 2), 
                      (WIDTH, HEIGHT))

    # draw ship and sprites when the game begins
    if started == True:
        my_ship.draw(canvas)
        
        for i in rocks:
            i.draw(canvas)
            
        # Drawing and updating explosions
        for i in list(explosions):
            if i.lifespan > 0:
                
                # Explosion spritemap update logic
                current_explosion_index = (expl_time % explosion_info.get_lifespan()) // 1
                
                current_explosion_center = [
                    explosion_info.get_center()[0] + current_explosion_index * explosion_info.get_size()[0], 
                    explosion_info.get_center()[1]]
                
                i.image_center = current_explosion_center
       
                expl_time += 0.4
                
                i.draw(canvas)
                i.lifespan -= 1

            else:
                explosions.remove(i)
            
    
    # Drawing missiles with a lifespan when the game starts
    if started == True:
        for i in list(missiles): # Using a list to avoid iteration problems
            if i.lifespan > 0:
                i.draw(canvas)
                i.lifespan -= 1
            else:
                missiles.remove(i)
    
    # draw score and lives
    canvas.draw_text("SCORE ", (730, 23), 20, "White", "monospace")
    canvas.draw_text(str(score), (755, 43), 23, "White")
    canvas.draw_text("LIVES ", (10, 23), 20, "White", "monospace")
    canvas.draw_text(str(lives), (30, 43), 23, "White")

    
    # update ship and sprites
    my_ship.update()
    
    for i in rocks:
        i.update()
    
    for i in missiles:
        i.update()
        
    for i in explosions:
        i.update()
        
        
# draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

# draw splash screen if lives = 0
    if lives == 0:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        started = False
        lives = 3
        score = 0
        rocks = set([])
        rock_count = 0
        soundtrack.rewind()

# The draw handler is calling the group_collide function, defined in line 364,
# and decreases the lives upon collision and plays a red alert sound!
    if group_collide(canvas, rocks, my_ship) == True:
        lives -= 1
        explosion_sound.play() # Replace w/ Red Alert sound
            
# group_group_collide
    if group_group_collide(canvas, rocks, missiles):
        score += 10
        rock_count -= 1
    
# timer handler that spawns rocks
def rock_spawner():
    global rocks, rock_count
    if started == True:
        if rock_count < 10:
            rocks.add(Sprite([random.randrange(0, WIDTH), random.randrange(0, 30)], 
                             [random.randrange(-2, 2),random.randrange(-2, 2)], 
                             0, 
                             random.randrange(-9.0, 9.0) * 0.01, 
                             asteroid_image, asteroid_info))
            rock_count += 1
            rocks.add(Sprite([random.randrange(0, WIDTH), random.randrange(HEIGHT-30, HEIGHT)], 
                             [random.randrange(-2, 2),random.randrange(-2, 2)], 
                             0, 
                             random.randrange(-9.0, 9.0) * 0.01, 
                             asteroid_image, asteroid_info))
            rock_count += 1

        else:
            return
    
# The Explosion function
def explosion(canvas, pos):
    explosions.add(Sprite(pos, 
                          [0, 0], 
                          0, 
                          0,
                          explosion_image, explosion_info, explosion_sound,))

    
def keydown(key):
    global started, lives, score
    if (not started):
        if key==simplegui.KEY_MAP["space"]:
            started = True
            lives = 3
            soundtrack.play()
            score = 0

    
    if (started):
        # If 'q' is pressed, go to intro screen and stop the soundtrack
        if key==simplegui.KEY_MAP["q"]:
            started = False
            soundtrack.rewind()
            flush_ingame_assets()
            
        if key==simplegui.KEY_MAP["left"]:
            my_ship.turn_left()
        elif key==simplegui.KEY_MAP["right"]:
            my_ship.turn_right()
        elif key==simplegui.KEY_MAP["up"]:
            my_ship.thrust_on()
        elif key==simplegui.KEY_MAP["space"]:
            my_ship.shoot()

def keyup(key):
    if key==simplegui.KEY_MAP["left"]:
        my_ship.stop_turning()
    elif key==simplegui.KEY_MAP["right"]:
        my_ship.stop_turning()
    elif key==simplegui.KEY_MAP["up"]:
        my_ship.thrust_off()
        

# Check for collisions between a group with a sprite
def group_collide(canvas, group, sprite):
    global locations 
    for i in list(group):
        if i.collide(sprite) == True:
            locations.append(i.get_position())
            explosion(canvas, pos=i.get_position())
            group.remove(i)
            return True

        
# Check for collisions between two groups
def group_group_collide(canvas, group1, group2):
    global explosions
    for i in list(group1): 
        if group_collide(canvas, group2, i):

            group1.remove(i)
            return True

        
def flush_ingame_assets():
    global rocks, missiles, explosions, rock_count
    rocks = set([])
    missiles = set([])
    explosions = set([])
    rock_count = 0


# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], 
               [0, 0], 
               0, 
               0, 
               ship_image, ship_info)

    
# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)


timer = simplegui.create_timer(1600.0, rock_spawner)

    
# get things rolling
timer.start()
frame.start()
