import pygame, sys, cv2
from pygame import *
from Hand import HandDetector

pygame.init()
screen = pygame.display.set_mode((500, 800))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Player Setup
paddleRect1 = pygame.Rect(188.5, 700, 100, 10)
paddleRect2 = pygame.Rect(188.5, 100, 100, 10)
img = pygame.image.load('/Users/satviksingh/Desktop/PongGame/img.png')
img = pygame.transform.rotate(img, -90)
img = pygame.transform.scale(img, (paddleRect1.width, paddleRect1.height))

x = 250
y = 500
ball = pygame.Rect(x, y, 30, 30)

# Text
Font = pygame.font.Font("/Users/satviksingh/Desktop/PongGame/pixelFont.ttf", 50)
textSurface = Font.render("PONG!", False, (56, 232, 12))
textRect = textSurface.get_rect(center=(250, 400))

endSurf = Font.render("GAME OVER", False, 'Red')
endRect = endSurf.get_rect(center=(250, 400))

wonSurf = Font.render("YOU WON!!!", False, 'Yellow')
wonRect = wonSurf.get_rect(center=(250, 400))

changeY = 1.5
changeX = 1.5

MAX_SPEED = 12

# Hand tracking setup
cap = cv2.VideoCapture(0)
detector = HandDetector()

def clamp_speed(changex, changey, max_speed=MAX_SPEED):
    changex = max(-max_speed, min(max_speed, changex))
    changey = max(-max_speed, min(max_speed, changey))
    return changex, changey

def handle_paddle1_collision(ball, paddleRect1, changex, changey):
    changey *= -1
    diff = ball.centerx - paddleRect1.centerx
    changex *= 1 + (abs(diff) / paddleRect1.width)
    changex = -abs(changex) if diff < 0 else abs(changex)
    return clamp_speed(changex, changey)

def handle_paddle2_collision(ball, paddleRect2, changex, changey):
    changey *= -1
    diff = ball.centerx - paddleRect2.centerx
    changex *= 1 + (abs(diff) / paddleRect2.width)
    changex = -abs(changex) if diff < 0 else abs(changex)
    return clamp_speed(changex, changey)

def borderControl(ball, changex, changey):
    if ball.right >= 500 or ball.left <= 0:
        changex *= -1
    if ball.top <= 0 or ball.bottom >= 800:
        changey *= -1
    return clamp_speed(changex, changey)

def homeScreen():
    screen.fill((0, 0, 0))
    screen.blit(textSurface, textRect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def reset_game():
    global ball, changeX, changeY, paddleRect1, paddleRect2
    ball.x, ball.y = 250, 500
    changeX, changeY = 1, 1
    paddleRect1.x, paddleRect1.y = 188.5, 700
    paddleRect2.x, paddleRect2.y = 188.5, 100

def end():
    if ball.top < 90 or ball.bottom > 750:
        screen.fill((0,0,0))
        screen.blit(endSurf if ball.bottom > 750 else wonSurf,
                    endRect if ball.bottom > 750 else wonRect)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    reset_game()
                    return

def enemyMovement():
    if paddleRect2.centerx - ball.centerx > 0 and paddleRect2.left > 0:
        paddleRect2.x -= 2
    elif paddleRect2.centerx - ball.centerx < 0 and paddleRect2.right < 500:
        paddleRect2.x += 2

# Start screen
homeScreen()

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

    # Hand tracking frame
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

    screen.fill((0, 0, 0))
    screen.blit(img, paddleRect1)
    screen.blit(img, paddleRect2)

    pygame.draw.ellipse(screen, "Red", ball)
    ball.y += changeY
    ball.x += changeX

    enemyMovement()

    if ball.colliderect(paddleRect1):
        changeX, changeY = handle_paddle1_collision(ball, paddleRect1, changeX, changeY)
    if ball.colliderect(paddleRect2):
        changeX, changeY = handle_paddle2_collision(ball, paddleRect2, changeX, changeY)

    changeX, changeY = borderControl(ball, changeX, changeY)
    end()

    pygame.display.update()
    clock.tick(60)
