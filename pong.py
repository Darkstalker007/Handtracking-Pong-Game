import pygame,sys,cv2,random
from pygame import *
from Hand import HandDetector

pygame.init()
screen= pygame.display.set_mode((500,800))
bg=pygame.image.load('static/bg.png')
pygame.display.set_caption("Pong")
clock= pygame.time.Clock()

#Player Setup
paddleRect1=pygame.Rect(188.5,700, 100, 10)
paddleRect2=pygame.Rect(188.5,100, 100, 10)
img=pygame.image.load('static/img.png')
img = pygame.transform.rotate(img, -90)
img = pygame.transform.scale(img, (paddleRect1.width, paddleRect1.height))  # Scale to fit paddleRect1



ball=pygame.Rect(235,385,30,30)


#Hand set up
cap = cv2.VideoCapture(0)
detector = HandDetector()


# Text
Font=pygame.font.Font("static/pixelFont.ttf", 50)
textSurface=Font.render("PONG!", False, (56, 232, 12))
textRect=textSurface.get_rect(center=(250,400))

endSurf=Font.render("GAME OVER", False, 'Red')
endRect=endSurf.get_rect(center=(250,400))

wonSurf=Font.render("YOU WON!!!", False, 'Yellow')
wonRect=wonSurf.get_rect(center=(250,400))

def rand():
    while True:
        n=[-10,-9,-8,10,9,8]
        return random.choice(n)

changeY=rand()
changeX=rand()

MAX_SPEED = 30

#Sounds
hit= pygame.mixer.Sound('static/hitSound.wav')
hit.set_volume(1)
over= pygame.mixer.Sound('static/gameOver.wav')
over.set_volume(1)
win=pygame.mixer.Sound('static/win.wav')
win.set_volume(1)
theme=pygame.mixer.music.load('static/theme.mp3')
pygame.mixer.music.set_volume(0.25)

def clamp_speed(changex, changey, max_speed=MAX_SPEED):
    if changex > max_speed:
        changex = max_speed
    if changex < -max_speed:
        changex = -max_speed
    if changey > max_speed:
        changey = max_speed
    if changey < -max_speed:
        changey = -max_speed
    return changex, changey

def handle_paddle1_collision(ball, paddleRect1, changex, changey):
    # Move ball out of paddle before processing collision
    ball.bottom = paddleRect1.top - 1
    
    changey *= -1  
    diff = ball.centerx - paddleRect1.centerx
    if abs(diff) < 20:  
        changex *= 1.1
    elif abs(diff) < 40:  
        changex *= 1.2
        if diff < 0:  
            changex = -abs(changex)
        else:  
            changex = abs(changex)
    else:  
        changex *= 1.3
        if diff < 0:  
            changex = -abs(changex)
        else:  
            changex = abs(changex)
            
    changex, changey = clamp_speed(changex, changey)  # Add this line
    return changex, changey

def handle_paddle2_collision(ball, paddleRect2, changex, changey):
    changey *= -1 
    diff = ball.centerx - paddleRect2.centerx
    if abs(diff) < 20:  
        changex *= 1.1
    elif abs(diff) < 40:  
        changex *= 1.2
        if diff < 0:  
            changex = -abs(changex)
        else:  
            changex = abs(changex)
    else:  
        changex *= 1.3
        if diff < 0:  # Hit left side
            changex = -abs(changex)
        else:  
            changex = abs(changex)
            
    changex, changey = clamp_speed(changex, changey)
    return changex, changey

def movement(keys):
    if keys[pygame.K_RIGHT] and paddleRect1.right<=562: paddleRect1.x+=12
    elif keys[pygame.K_LEFT] and paddleRect1.left >=-62:  paddleRect1.x-=12
    
def borderControl(ball, changex, changey):
    if ball.right >= 500 or ball.left <= 0: 
        changex *= -1
        changex, changey = clamp_speed(changex, changey)
        pygame.mixer.Sound.play(hit)  
    return changex, changey    

def homeScreen():
    screen.fill((0, 0, 0))
    screen.blit(textSurface, textRect)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def reset_game():
    global ball, changeX, changeY, paddleRect1, paddleRect2
    ball.center=(250,400)
    changeX, changeY = rand(), rand()
    paddleRect1.x, paddleRect1.y = 188.5, 700
    paddleRect2.x, paddleRect2.y = 188.5, 100
    pygame.mixer.music.play(-1)

def end():
    if ball.top <= 0 or ball.bottom >= 800:
        if ball.bottom > 750:
            screen.fill((0,0,0))
            screen.blit(endSurf,endRect)
            pygame.display.update()
            pygame.mixer.music.pause()
            pygame.mixer.Sound.play(over)
        if ball.top< 90:
            screen.fill((0,0,0))
            screen.blit(wonSurf,wonRect)
            pygame.display.update()
            pygame.mixer.music.pause()
            pygame.mixer.Sound.play(win)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    reset_game()
                    waiting = False
        
def enemyMovement():
    if paddleRect2.centerx - ball.centerx > 0 and paddleRect2.left > 0:
        paddleRect2.x -= 12  # Move left
    elif paddleRect2.centerx - ball.centerx < 0 and paddleRect2.right < 500:
        paddleRect2.x += 12  # Move right           

#Starting of the game
homeScreen()
pygame.mixer.music.play(-1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(bg, (0,0))
    screen.blit(img, paddleRect1) #Paddle 1
    screen.blit(img, paddleRect2) #Paddle 2
    keys=pygame.key.get_pressed()
    # movement(keys)

    if keys[pygame.K_r]: reset_game()

    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        detector.findHands(frame)
        handX = detector.getIndexFingerX(frame)
        if handX is not None:
            cam_width = frame.shape[1]
            game_width = screen.get_width()
            paddleRect1.x = int((handX / cam_width) * game_width - paddleRect1.width / 2)
            # Clamp to screen
            paddleRect1.x = max(0, min(game_width - paddleRect1.width, paddleRect1.x))
    
    pygame.draw.ellipse(screen, "Blue", ball)
    ball.y+=changeY
    ball.x+=changeX

    enemyMovement()

    #Collide Logic
    if ball.colliderect(paddleRect1):  
        changeX, changeY = handle_paddle1_collision(ball, paddleRect1, changeX, changeY)
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(hit)
        pygame.mixer.music.unpause()

    if ball.colliderect(paddleRect2):  
        changeX, changeY = handle_paddle2_collision(ball, paddleRect2, changeX, changeY)
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(hit)
        pygame.mixer.music.unpause()

    #Border Controls
    changeX, changeY = borderControl(ball, changeX, changeY)

    end()

    pygame.display.update()
    clock.tick(60)