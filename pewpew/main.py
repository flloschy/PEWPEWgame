#sounds from https://sfxr.me/
import pygame
import random
import sys
import time
from json import load as json
from pygame import key
from termcolor import colored
pygame.font.init()
pygame.mixer.init()

window = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['window']
def width(): return window['width']
def height(): return window['height']
def player_speed(): return json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['player']['speed']
Text_font = pygame.font.SysFont('comicsans', 100)
Text_font_30 = pygame.font.SysFont('comicsans', 30)
Text_font_10 = pygame.font.SysFont('comicsans', 20)
dic = "F:/Programme/pygamestuff/pewpew" # Put your Path here so everything can work correct

# Loading Sounds
Attacker_Die = pygame.mixer.Sound(f'{dic}/Data/Sound/AttackerDie.wav')
Attacker_Shoot = pygame.mixer.Sound(f'{dic}/Data/Sound/AttackerShoot.wav')
Attacker_Under_height = pygame.mixer.Sound(f'{dic}/Data/Sound/AttackerUnderHeigth.wav')
Next_wave = pygame.mixer.Sound(f'{dic}/Data/Sound/NextWave.wav')
Player_Colide = pygame.mixer.Sound(f'{dic}/Data/Sound/PlayerColide.wav')
Player_Die = pygame.mixer.Sound(f'{dic}/Data/Sound/PlayerDie.wav')
Player_Shoot = pygame.mixer.Sound(f'{dic}/Data/Sound/PlayerShoot.wav')
Player_Hit = pygame.mixer.Sound(f'{dic}/Data/Sound/PlayerHit.wav')

player = pygame.Rect(width()//2, height()-100, 50, 50) # create the player hitbox
player_hit = pygame.USEREVENT + 1 # create a custom event

# load textures
player_bullet_texture = pygame.transform.scale(pygame.image.load(f"{dic}/Data/Assets/PlayerBullet.png"), (5, 25))
player_texture = pygame.transform.scale(pygame.image.load(f"{dic}/Data/Assets/Player.png"), (50, 50))
attacker_bullet_texture = pygame.transform.scale(pygame.image.load(f"{dic}/Data/Assets/AttackerBullet.png"), (5, 25))
attacker_texture =  pygame.transform.scale(pygame.image.load(f"{dic}/Data/Assets/Attacker.png"), (40, 40))

# store bullets and attackers
player_bullets = []
attacker_bullets = []
attacker_list = []
attacker_in_wave = 0
current_wave = 1

# create the pygame window
WIN = pygame.display.set_mode((width(), height()))

# give a name to the window
pygame.display.set_caption("Pew Pew Game by github.com/flloschy")

def debug(text, col, print_it=True):
    if print_it:
        print(colored(text, col))

def quit_game(): # close and end the game
    debug("Quiting the game.......", "red")
    pygame.quit()
    sys.exit()

def update_window(): # reload the 
    debug("Reloading display...", "green", False)
    pygame.display.update()

def create_window_content(life, current_wave, spawned_attacker):
    WIN.blit(get_background(), (0, 0)) # set Background
    
    # Render Text
    WIN.blit(Text_font_10.render("Controls: a/d: Movement     Space bar: Fire    ESC: Exit",1 ,(200, 100, 0)), (width()//2-180, height()-20))
    WIN.blit(Text_font_30.render(f"Health: {life}", 1, (255, 255, 255)), (10, 10))
    WIN.blit(Text_font_30.render(f"Wave: {current_wave}/10", 1, (255, 255, 255)), (10, 40))

    # Calculate the wave percentage
    wave_spawning = json(open('./Data/Config/pre.json', 'r', encoding='utf-8'))['wave'][f'{current_wave}']['spawn']
    wave_percent = round(spawned_attacker/wave_spawning*100, 1)
    WIN.blit(Text_font_30.render(f"Wave Spawned: {wave_percent}%", 1, (255, 255, 255)), (10, 70))

    # Go throw every Bullet and attacker to render it
    for pb in player_bullets:
        x, y = pb.x, pb.y
        WIN.blit(player_bullet_texture, (x, y)) # place bullet on screen
    for ab in attacker_bullets:
        x, y = ab.x, ab.y
        WIN.blit(attacker_bullet_texture, (x, y)) # place bullet on screen
    for attacker in attacker_list:
        x, y= attacker.x, attacker.y
        WIN.blit(attacker_texture, (x, y)) # place attacker on screen

    WIN.blit(player_texture, (player.x, player.y)) # place player on screen
    update_window() # update the screen


def get_background(): # return the background image
    debug("Loading background...", "green", False)
    back = pygame.image.load("./Data/Assets/Background.png") # load background
    back = pygame.transform.rotate(back, 90) # turn background
    back = pygame.transform.scale(back, (width(), height())) # scale background
    return back # background by https://pbs.twimg.com/media/ECbeOgkXYAAgJ-F.png
def get_keys(): # return all pressed keys
    return pygame.key.get_pressed() 

def move_player_right(wave): # move the player to the right
    if json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['player']['1.5 more speed per wave']:
        if round(player.x + player_speed() + (wave*1.5), 0) <= width()-50:
            player.x += round(player_speed() + (wave*1.5), 0) # reposition the player possition
            debug(f"Moved player to x: {player.x}...", "yellow", False)
    else:
        if player.x + player_speed() <= width()-50:
            player.x += player_speed() # reposition the player possition
            debug(f"Moved player to x: {player.x}...", "yellow", False)
def move_player_left(wave):
    if json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['player']['1.5 more speed per wave']:
        if round(player.x - player_speed() + (wave*1.5), 0) >= 0 :
            player.x -= round(player_speed() + (wave*1.5), 0) # reposition the player possition
            debug(f"Moved player to x: {player.x}...", "yellow", False)
    else:
        if player.x - player_speed() <= width()-50:
            player.x -= player_speed() # reposition the player possition
            debug(f"Moved player to x: {player.x}...", "yellow", False)
def create_bullet(player_shoot_tick, wave):
    json_file = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['player']
    dobble_max_bullets = json_file['dubble bullets per wave']
    if player_shoot_tick <= json_file['bullet timeout tick']: # if shooting is free
        return False
    if dobble_max_bullets:
        if len(player_bullets) < json_file['max bullets']*wave:
            x, y = player.x+23, player.y
            player_bullets.append(pygame.Rect(x, y, 10, 25)) # Place Bullet
            debug("Created Player Bullet...", "green")
            Player_Shoot.play() # Play sound
            return True
    else:
        if len(player_bullets) < json_file['max bullets']:
            x, y = player.x+23, player.y
            player_bullets.append(pygame.Rect(x, y, 10, 25)) # Place Bullet
            debug("Created Player Bullet...", "green")
            Player_Shoot.play() # Play sound
            return True
    return False

def manage_controls(player_shoot_tick, wave):
    keys_pressed = get_keys()
    done = False
    if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
        move_player_right(wave)
    if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
        move_player_left(wave)
    if keys_pressed[pygame.K_SPACE]:
        if create_bullet(player_shoot_tick, wave): # if a bullet was created
            done = True
    if keys_pressed[pygame.K_ESCAPE]:
        quit_game() # Quit the game
    return done


def hit():
    debug("Player got hit...", "red")
    pygame.event.post(pygame.event.Event(player_hit)) # Post a custom event
def manage_bullets(aiw):
    def p_bullets(): # move the player bullets
        speed = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['player']['bullet speed']
        for bullet in player_bullets:
            bullet.y -= speed
        debug("Moved Player Bullets", "cyan", False)
    def a_bullets(): # move the attackers bullets
        speed = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['attacker']['bullet speed']
        for bullet in attacker_bullets:
            bullet.y += speed
        debug("Moved Attacker Bullets", "cyan", False)
    def kill_attacker_and_bullets(aiw):
        for pb in player_bullets: # for every player bullet
            if pb.y <= 0: # if the bullit is above the screen
                try: player_bullets.remove(pb) # delete the bullet
                except: continue
            for ab in attacker_bullets: # for every attack bullet
                if pb.colliderect(ab): # if the player bullet hit a attack bullet
                    try: player_bullets.remove(pb); attacker_bullets.remove(ab); debug("A bullet hits another...", "yellow") # remove both bullets
                    except: continue
            for attacker in attacker_list: # for every attacker
                if pb.colliderect(attacker): # if the bullet hits the attacker
                    try: player_bullets.remove(pb); attacker_list.remove(attacker); Attacker_Die.play(); debug("Attacker Died", "red") # remove the bullet and attacker and play sound
                    except: continue
        for ab in attacker_bullets: # for every attack bullet
            if ab.colliderect(player): # if bullet hits the player 
                try: attacker_bullets.remove(ab); hit(); Player_Hit() # remove bullet and hit player
                except: continue
            if ab.y >= height(): # if the bullet is under the screen
                try: attacker_bullets.remove(ab); debug("Attacker bullet went out of screen", "cyan", False)# remove bullet
                except: continue
            for ab2 in attacker_bullets: # for every attack bullet
                if ab.colliderect(ab2) and ab2 != ab:
                    try: attacker_bullets.remove(ab2); debug("Attack bullet hits an Attck bullet", "can")
                    except: continue
        for attacker in attacker_list: # for every attacker
            if attacker.colliderect(player): # if attacker hits player 
                try: attacker_list.remove(attacker); hit(); Player_Colide.play(); debug("Attacker hit player", "red") # remove attacker and remove a health
                except: continue
            if attacker.y > height(): # if attacker is under the screen 
                try: attacker_list.remove(attacker); hit(); aiw-=1; Attacker_Under_height.play(); debug("Attacker went out of screen", "cyan", False) # remove attacker and hit player and play sound
                except: continue
            # for ab in attacker_bullets: # for every bullet in attack bullets
            #     if attacker.colliderect(ab): # if a attack bullet contacts a attacker
            #         try: attacker_bullets.remove(ab); debug("Attacker hits attacker", "magenta") # remove the bullet 
            #         except: continue
        return aiw

    p_bullets()
    a_bullets()
    return kill_attacker_and_bullets(aiw)

def handle_wave(aiw, current_wave): # manage every wave
    def spawn(): # spawn a attacker
        debug("Spawned attacker...", "green")
        x, y = random.randint(13, width()-40), -10 # get random x possition
        attacker_list.append(pygame.Rect(x, y, 40, 40)) # place attacker
    if aiw < json(open("./Data/Config/pre.json"))['wave'][f'{current_wave}']['spawn']: # if less attackers were spawned than the wave has
        ran_num = random.randint(1, json(open("./Data/Config/pre.json"))['attacker']['spawn chance']) # get a random number
        if ran_num == 1: # if the nummber is one
            spawn() # spawn the attacer
            aiw += 1
    if len(attacker_list) <= 0: # if non attacker are left
        if aiw >= json(open("./Data/Config/pre.json"))['wave'][f'{current_wave}']['spawn']: # and the wave is over
            current_wave += 1 # go to the next wave
            debug(f"\n\nNEXT WAVE STARTED\nNew Wave: {current_wave}\n\n", "white")
            Next_wave.play() # play sound
    if current_wave > 10: # if the stage is higher than 10
        debug("Player had won", "green")
        player_won() # win the game
    return [aiw, current_wave]


def move_attacker(current_wave):
    json_file = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))
    wave = current_wave
    wave_speed = json_file['attacker']['speed']*json_file['wave'][f'{wave}']['speed multiply']
    wave_speed = wave_speed + random.randint(-1, 1)
    for attacker in attacker_list: # for every attacker
        attacker.y += wave_speed # move it down

def shoot_attacker():
    for attacker in attacker_list: # for every attacker
        ran_num = random.randint(1, json(open("./Data/Config/pre.json", "r", encoding="utf-8"))['attacker']['shoot chance']) # get a random number
        if ran_num == 1: # if the nummber is one
            x, y = attacker.x+attacker.width//2-1, attacker.y-20 # get the middle posstion of the attacker
            attacker_bullets.append(pygame.Rect(x, y, 10, 25)) # spawn bullet
            debug("Attacker has shoot", "green")

        for bullet in player_bullets: # for bullet from the player
            if bullet.x in range(attacker.x, attacker.x+attacker.width): #if the bullet is in the width of the attacker
                if bullet.y > attacker.y + 30: # if bullet y cord is higher than the attacker
                    if bullet.y in range(attacker.y, attacker.y+100): # if the bullet is 100 pixl before the attacker
                        ran_num = random.randint(1, 30) # get a random nummber
                        if ran_num == 3: # if the random nummber is 3 create a bullet
                            x, y = attacker.x+attacker.width//2-1, attacker.y-20 # get the middle posstion of the attacker
                            attacker_bullets.append(pygame.Rect(x, y, 10, 25)) # spawn bullet
                            debug("Attacker trys to save him self", "blue")

def player_won():
    draw_text = Text_font.render("You Won", 1, (255, 255, 255)) # print the text
    WIN.blit(draw_text, (width()//2 - draw_text.get_width()//2, height()//2 - draw_text.get_height()//2)) # put it on screen 
    update_window() # update the window
    time.sleep(5) # pause code
    quit_game() # quit the game 
def player_loose():
    draw_text = Text_font.render("You Lose", 1, (255, 255, 255)) # print the text
    WIN.blit(draw_text, (width()//2 - draw_text.get_width()//2, height()//2 - draw_text.get_height()//2)) # put it on screen 
    update_window() # update the window
    Player_Die.play() # play lose sound 
    time.sleep(5) # pause code
    quit_game() # quit the game 

def tick(timeout_tick, aiw, current_wave, player_life):
    debug("new tick", "white", False)
    before_wave = current_wave # store the last wave nummber
    timeout_tick += 1 # add a tick to the tick count
    aiw, current_wave = handle_wave(aiw, current_wave) # run wave handleing
    if manage_controls(timeout_tick, current_wave): # if a bullet was spawn
        timeout_tick = 0 # reset the tick count
    aiw = manage_bullets(aiw) # move bullets
    move_attacker(current_wave ) # move attackers
    for event in pygame.event.get(): # for every event
        if event.type == pygame.QUIT: # if window close
            debug("ESC got pressed", "red")
            quit_game() # quit the game
        if event.type == player_hit: # if the player is hit
            player_life -= 1 # remove one heart 

    if player_life <= 0: # if the player has no health left
        debug("Player has loosed", "red")
        player_loose() # end the game
    after_wave = current_wave # store the current wave nummber
    if before_wave != after_wave: # if the last and new wave are different
        aiw = 0 # reset the in wave count
    create_window_content(player_life, current_wave, aiw) # update screen
    shoot_attacker() # let the attackers spawn
    return [timeout_tick, aiw, current_wave, player_life]
def run(attacker_in_wave, current_wave):
    debug("Starting game.....", "yellow")
    time.sleep(2)
    clock = pygame.time.Clock() # define the clock
    json_file = json(open("./Data/Config/pre.json", "r", encoding="utf-8"))
    player_life = json_file['player']['health']
    player_shoot_tick = 0
    while True:
        clock.tick(json_file['window']['fps']) # get a time delay
        player_shoot_tick, attacker_in_wave, current_wave, player_life = tick(player_shoot_tick, attacker_in_wave, current_wave, player_life) # run tick


run(attacker_in_wave, current_wave) # start game
