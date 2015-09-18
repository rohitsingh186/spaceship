# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
num_rocks = 0
started = False

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
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.s2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def speed(vel):
    return math.sqrt((vel[0] ** 2) + (vel[1] ** 2))

# Processing sprite group
def process_sprite_group(sprite_group, canvas):
    global num_rocks
    for a_sprite in set(sprite_group):
        a_sprite.draw(canvas)
        if (a_sprite.pos[0] < - a_sprite.radius or a_sprite.pos[0] > WIDTH + a_sprite.radius) or (a_sprite.pos[1] < - a_sprite.radius or a_sprite.pos[1] > HEIGHT + a_sprite.radius) or (a_sprite.update()):
            sprite_group.remove(a_sprite)
            if a_sprite.radius == asteroid_info.radius:
                num_rocks -= 1
        
# Group Collide
def group_collide(rock_grp, other_object):
    global num_rocks, lives, started, rock_group, missile_group
    ret_val = False
    for a_rock in set(rock_grp):
        if a_rock.collide(other_object):
            rock_grp.remove(a_rock)
            num_rocks -= 1
            ret_val = True
            if other_object.radius == ship_info.radius:
                lives -= 1
                if lives == 0:
                    started = False
                    rock_group = set([])
                    missile_group = set([])
                    soundtrack.pause()
                    soundtrack.rewind()
    return ret_val

# Group-Group Collide
def group_group_collide(rock_grp, missile_grp):
    ret_val = 0
    for a_missile in set(missile_grp):
        if group_collide(rock_grp, a_missile):
            ret_val += 1
            missile_grp.remove(a_missile)
    return ret_val

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
        
    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        
    def shoot(self):
        unit_vector = angle_to_vector(self.angle)
        pos_x = self.pos[0] + self.radius * unit_vector[0]
        pos_y = self.pos[1] + self.radius * unit_vector[1]
        vel_x = self.vel[0] + 8 * unit_vector[0]
        vel_y = self.vel[1] + 8 * unit_vector[1]
        a_missile = Sprite([pos_x, pos_y], [vel_x, vel_y], 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        
        
    def update(self):
        global unit_vector
        if self.thrust:
            unit_vector = angle_to_vector(self.angle)
            self.vel[0] += 0.1 * unit_vector[0]
            self.vel[1] += 0.1 * unit_vector[1]
        
        if self.vel[0] is not(0) or self.vel[1] is not(0):
            unit_vector = angle_to_vector(self.angle)
            spd = speed(self.vel)
            if spd > 2 and self.thrust == False:
                spd = spd * 0.99
            else:
                spd -= 0.005 
            self.vel[0] = spd * unit_vector[0] 
            self.vel[1] = spd * unit_vector[1]
            self.pos[0] = (self.pos[0] + self.vel[0]) % (WIDTH + self.radius)
            self.pos[1] = (self.pos[1] + self.vel[1]) % (HEIGHT + self.radius)
        self.angle += self.angle_vel
    
    
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
            
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.age += 1
        if self.age >= self.lifespan:
            return True
        else:
            return False
        
    def collide(self, other_object):
        center_dist = dist(self.pos, other_object.get_position())
        if center_dist <= (self.radius + other_object.get_radius()):
            explosion_sound.rewind()
            explosion_sound.play()
            return True
        else:
            return False
        
           
def draw(canvas):
    global time, lives, score
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_text("Lives :- " + str(lives), [30, 50], 36, "Red")
    canvas.draw_text("Score :- " + str(score), [620, 50], 36, "Green")
    canvas.draw_circle(my_ship.pos, my_ship.radius, 2, "Red")
    canvas.draw_circle(my_ship.pos, my_ship.radius + 60, 2, "Green")
    
    # update ship and draw ship
    my_ship.update()
    group_collide(rock_group, my_ship)
    my_ship.draw(canvas) 
    
    # Collisions between missiles and rocks
    num = group_group_collide(rock_group, missile_group)
    score += num
    
    #draw and update missiles
    process_sprite_group(missile_group, canvas)
    
    #draw and update rocks
    process_sprite_group(rock_group, canvas)
    
    # Splash Screen
    if not started:
        canvas.draw_image(splash_image, splash_info.center, splash_info.size, [WIDTH / 2, HEIGHT / 2], splash_info.size)
        
        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, num_rocks
    if num_rocks < 12 and started:
        pos_x = random.randrange(asteroid_info.radius, WIDTH - asteroid_info.radius)
        pos_y = random.randrange(asteroid_info.radius, HEIGHT - asteroid_info.radius)
        vel_x = random.randrange(-1 , 1)
        vel_y = random.randrange(-1 , 1)
        if (dist([pos_x, pos_y], my_ship.pos) > asteroid_info.radius + my_ship.radius + 60):
            a_rock = Sprite([pos_x, pos_y], [vel_x, vel_y], 0, math.pi / 32, asteroid_image, asteroid_info)
            rock_group.add(a_rock)
            num_rocks += 1


# key handlers
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel = - math.pi / 32
    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel = math.pi / 32
    elif key == simplegui.KEY_MAP['up']:
        my_ship.image_center[0] = 135
        my_ship.thrust = True
        ship_thrust_sound.play()
    elif key == simplegui.KEY_MAP['down']:
        my_ship.vel = [0, 0]
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        missile_sound.play()
        
        
def keyup(key):
    if key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel = 0
    elif key == simplegui.KEY_MAP['up']:
        my_ship.image_center[0] = 45
        my_ship.thrust = False
        ship_thrust_sound.rewind()
    elif key == simplegui.KEY_MAP['space']:
        missile_sound.rewind()
        
def mouseclick_handler(position):
    global started, lives, score
    if ((WIDTH / 2) - (splash_info.size[0] / 2) < position[0] < (WIDTH / 2) + (splash_info.size[0] / 2)) and ((HEIGHT / 2) - (splash_info.size[1] / 2) < position[1] < (HEIGHT / 2) + (splash_info.size[1] / 2)):
        started = True
        lives = 3
        score = 0
        my_ship.pos = [WIDTH / 2, HEIGHT / 2]
        my_ship.vel = [0, 0]
        my_ship.angle = 0
        soundtrack.play()
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(mouseclick_handler)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
