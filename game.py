import pygame, os, time, random
# INITIALIZE A FONT FOR THE MESSAGES
pygame.font.init()

# SETTING THE WINDOW
Width, Height = 750, 750
Window = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("SPACE INVADERS")

# BACKGROUND
background = pygame.transform.scale(pygame.image.load(os.path.join("source", "background.png")),
                                    (Width, Height))

# SHIPS
# Load red ship
redSpaceShip = pygame.image.load(os.path.join("source", "redShip.png"))
redMissile = pygame.image.load(os.path.join("source", "redLaser.png"))

# Load green ship
greenSpaceShip = pygame.image.load(os.path.join("source", "greenShip.png"))
greenMissile = pygame.image.load(os.path.join("source", "greenLaser.png"))

# Load blue ship
blueSpaceShip = pygame.image.load(os.path.join("source", "blueShip.png"))
blueMissile = pygame.image.load(os.path.join("source", "blueLaser.png"))

# Load yellow ship --- PLAYER
playerShip = pygame.image.load(os.path.join("source", "yellowShip.png"))
playerMissile = pygame.image.load(os.path.join("source", "yellowLaser.png"))

class Missile:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def shift(self, velocity):
        self.y += velocity

    def pop(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, _object):
        return collide(self, _object)

class Ship:
    cd = 30

    def __init__(self, x, y, hp = 100):
        self.x = x
        self.y = y
        self.hp = hp
        self.shipImage = None
        self.missileImage = None
        self.missiles = []
        self.cdCounter = 0

    def draw(self, window):
        window.blit(self.shipImage, (self.x, self.y))
        for i in self.missiles:
            i.draw(window)

    def shiftMissile(self, velocity, _object):
        self._cd()
        for i in self.missiles:
            i.shift(velocity)
            if i.pop(Height):
                self.missiles.remove(i)
            elif i.collision(_object):
                _object.hp -= 10
                self.missiles.remove(i)

    def _cd(self):
        if self.cdCounter >= self.cd:
            self.cdCounter = 0
        elif self.cdCounter > 0:
            self.cdCounter += 1

    def fire(self):
        if self.cdCounter == 0:
            missile = Missile(self.x, self.y, self.missileImage)
            self.missiles.append(missile)
            self.cdCounter = 1

    def getWidth(self):
        return self.shipImage.get_width()

    def getHeight(self):
        return self.shipImage.get_height()

class Human(Ship):
    def __init__(self, x, y, hp = 100):
        super().__init__(x, y, hp)
        self.shipImage = playerShip
        self.missileImage = playerMissile
        self.mask = pygame.mask.from_surface(self.shipImage)
        self.maxHp = hp

    def shiftMissile(self, velocity, _object):
        self._cd()
        for i in self.missiles:
            i.shift(velocity)
            if i.pop(Height):
                self.missiles.remove(i)
            else:
                for j in _object:
                    if i.collision(j):
                        _object.remove(j)
                        if i in self.missiles:
                            self.missiles.remove(i)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.shipImage.get_height() + 10, self.shipImage.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.shipImage.get_height() + 10, self.shipImage.get_width() * (self.hp/self.maxHp), 10))

class Bot(Ship):
    clrs = {
        "red": (redSpaceShip, redMissile), 
        "green": (greenSpaceShip, greenMissile),
        "blue": (blueSpaceShip, blueMissile)
    }

    def __init__(self, x, y, clr, hp = 100):
        super().__init__(x, y, hp)
        self.shipImage, self.missileImage =  self.clrs[clr]
        self.mask = pygame.mask.from_surface(self.shipImage)

    def shift(self, velocity):
        self.y += velocity

    def fire(self):
        if self.cdCounter == 0:
            missile = Missile(self.x - 20, self.y, self.missileImage)
            self.missiles.append(missile)
            self.cdCounter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    frames = 60
    stage = 1
    tries = 5
    _font = pygame.font.SysFont("timesnewroman", 50)

    bots = []
    wave = 3
    
    player = Human(300, 600)

    repeater = pygame.time.Clock()

    dead = False
    deadCount = 0

    def redraw():
        Window.blit(background, (0, 0))

        triesLabel = _font.render(f"Missed: {tries}", 1, (130, 0, 233))
        Window.blit(triesLabel, (10, 10))

        stageLabel = _font.render(f"Stage: {stage}", 1, (130, 0, 233))
        Window.blit(stageLabel, (Width - stageLabel.get_width() - 10, 10))

        for i in bots:
            i.draw(Window)

        player.draw(Window)

        if dead:
            deadLabel = _font.render("You died!", 1, (255, 255, 255))
            Window.blit(deadLabel, (Width / 2 - deadLabel.get_width() / 2, 350))        

        pygame.display.update()

    while run:
        repeater.tick(frames)
        redraw()

        if tries <= 0 or player.hp <= 0:
            dead = True
            deadCount += 1

        if dead:
            if deadCount > frames * 3:
                run = False
            else: 
                continue
        
        if len(bots) == 0:
            stage += 1
            wave += 4
            for i in range(wave):
                bot = Bot(random.randrange(50, Width - 100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                bots.append(bot)

        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                quit()

        instruction = pygame.key.get_pressed()
        if instruction[pygame.K_LEFT] and player.x - 5 > 0:
            player.x -= 5
        if instruction[pygame.K_RIGHT] and player.x + 5 + player.getWidth() < Width:
            player.x += 5
        if instruction[pygame.K_UP] and player.y - 5 > 0:
            player.y -= 5
        if instruction[pygame.K_DOWN] and player.y + 5 + player.getHeight() < Height:
            player.y += 5 
        if instruction[pygame.K_SPACE]:
            player.fire()

        for i in bots[:]:
            i.shift(1)
            i.shiftMissile(5, player)

            if random.randrange(0, 2*60) == 1:
                i.fire()

            if collide(i, player):
                player.hp -= 10
                bots.remove(i)
            elif i.y + i.getHeight() > Height:
                tries -= 1
                bots.remove(i)

        player.shiftMissile(-5, bots)

def menu():
    _font = pygame.font.SysFont("timesnewroman", 80)
    run = True
    while run:
        Window.blit(background, (0, 0))
        _label = _font.render("START", 1, (255, 255, 255))
        Window.blit(_label, (Width / 2 - _label.get_width() / 2, 350))
        pygame.display.update()
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                run = False
            if i.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

menu()