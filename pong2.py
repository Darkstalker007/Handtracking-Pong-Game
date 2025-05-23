import pygame,sys,cv2
from pygame import *
from Hand import HandDetector

pygame.init()
screen= pygame.display.set_mode((500,800))
pygame.display.set_caption("Pong")
clock= pygame.time.Clock()

#Player Setup
paddleRect1=pygame.Rect(188.5,700, 100, 10)
paddleRect2=pygame.Rect(188.5,100, 100, 10)
img=pygame.image.load('/Users/satviksingh/Desktop/PongGame/img.png')
img = pygame.transform.rotate(img, -90)
img = pygame.transform.scale(img, (paddleRect1.width, paddleRect1.height))  # Scale to fit paddleRect1


x=250; y= 500
ball=pygame.Rect(x,y,30,30)

#Hand set up
cap = cv2.VideoCapture(0)
detector = HandDetector()


# Text
Font=pygame.font.Font("/Users/satviksingh/Desktop/PongGame/pixelFont.ttf", 50)
textSurface=Font.render("PONG!", False, (56, 232, 12))
textRect=textSurface.get_rect(center=(250,400))

endSurf=Font.render("GAME OVER", False, 'Red')
endRect=endSurf.get_rect(center=(250,400))

wonSurf=Font.render("YOU WON!!!", False, 'Yellow')
wonRect=wonSurf.get_rect(center=(250,400))

changeY=7
changeX=7

MAX_SPEED = 20 

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
            
    # Remove this line since we're already clamping in the main loop
    # changex, changey = clamp_speed(changex, changey)
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
    if keys[pygame.K_RIGHT] and paddleRect1.right<=562: paddleRect1.x+=2
    elif keys[pygame.K_LEFT] and paddleRect1.left >=-62:  paddleRect1.x-=2
    # if keys[pygame.K_RIGHT] and paddleRect2.right<=562: paddleRect2.x+=2
    # elif keys[pygame.K_LEFT] and paddleRect2.left >=-62:  paddleRect2.x-=2
    
def borderControl(ball, changex, changey):
    if ball.right >= 500 or ball.left <= 0: 
        changex *= -1
        changex, changey = clamp_speed(changex, changey)
    if ball.top <= 0 or ball.bottom >= 800: 
        changey *= -1
        changex, changey = clamp_speed(changex, changey)
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
homeScreen()

def reset_game():
    global ball, changeX, changeY, paddleRect1, paddleRect2
    ball.x, ball.y = 250, 500
    changeX, changeY = 7, 7
    paddleRect1.x, paddleRect1.y = 188.5, 700
    paddleRect2.x, paddleRect2.y = 188.5, 100

def end():
    if ball.top < 90 or ball.bottom > 750:
        if ball.bottom > 750:
            screen.fill((0,0,0))
            screen.blit(endSurf,endRect)
            pygame.display.update()
        if ball.top< 90:
            screen.fill((0,0,0))
            screen.blit(wonSurf,wonRect)
            pygame.display.update()
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    screen.blit(img, paddleRect1) #Paddle 1
    screen.blit(img, paddleRect2) #Paddle 2
    keys=pygame.key.get_pressed()
    #movement(keys)

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
    
    pygame.draw.ellipse(screen, "Red", ball)
    ball.y+=changeY
    ball.x+=changeX

    enemyMovement()

    #Ball logic
    if ball.colliderect(paddleRect1):  
        changeX, changeY = handle_paddle1_collision(ball, paddleRect1, changeX, changeY)
        # Remove duplicate clamp_speed call
        # changeX, changeY = clamp_speed(changeX, changeY)

    if ball.colliderect(paddleRect2):  
        changeX, changeY = handle_paddle2_collision(ball, paddleRect2, changeX, changeY)
        # Remove duplicate clamp_speed call
        # changeX, changeY = clamp_speed(changeX, changeY)

    #Border Controls
    changeX, changeY = borderControl(ball, changeX, changeY)

    end()

    pygame.display.update()
    clock.tick(60)