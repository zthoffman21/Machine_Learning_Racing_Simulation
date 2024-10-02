import pygame
import math
import neat
from car import Car

# Initialize Pygame
pygame.init()

# Set up the display
screenWidth, screenHeight = 1000, 900
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Racing Line Simulation")
clock = pygame.time.Clock()

userTrack = screen.copy()

# Set up colors
white = (255, 255, 255)
drawingColor = black  = (0, 0, 0)
darkGreen = (0,100,0)
lightGreen = (144, 238, 144)

# Set the initial position for the images
finishLineX = screenWidth/2
finishLineY = screenHeight * .9 - 50 # 50 = finishLine.height//2

cars = []
numCars = 1
# Create car objects
for x in range(numCars):
    cars.append(Car())
    cars[x].carX = screenWidth/2 - 25 # 25 = car.width//2
    cars[x].carY = screenHeight * .9

# Load the button 
startButtonX = screenWidth/2-60
startButtonY = 30
startButton = pygame.image.load("images/StartButton.png")
startButton = pygame.transform.scale(startButton, (120, 50)) 
startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))


# Fill background with white
screen.fill(white)

# Variables to track drawing state
drawing = False  # Whether the mouse is currently drawing
lastPos = None  # Store the last position to interpolate points

brushRadius = 50  # Default brush size

def clearScreen():
    screen.fill(white)

def drawCircle(screen, color, start, end, radius):
    # Calculate the distance between start and end points
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.hypot(dx, dy)

    # Interpolate between the points and draw circles to make a smooth line
    for i in range(int(distance)):
        x = int(start[0] + dx * (i / distance))
        y = int(start[1] + dy * (i / distance))
        pygame.draw.circle(screen, color, (x, y), radius)

def checkCollisionWithWhitePixels(screen, car):
    # Rotate the car image based on the car's current angle
    rotatedCarImage = pygame.transform.rotate(car.f1CarImage, -math.degrees(car.carAngle))
    # Get the bounding box of the rotated image (car's new location)
    carRect = rotatedCarImage.get_rect(center=(car.carX, car.carY))

    criticalPoints = [
        carRect.midtop,      # Front center
        carRect.topleft,     # Front-left corner
        carRect.topright,    # Front-right corner
        carRect.midleft,     # Middle-left (side)
        carRect.midright,    # Middle-right (side)
    ]
    for point in criticalPoints:
        x, y = point
        # Check if the point is within the screen bounds
        if 0 <= x < screen.get_width() and 0 <= y < screen.get_height():
            # Calculate the relative position in the rotated image
            relativeX = int(x - carRect.x)
            relativeY = int(y - carRect.y)

            if 0 <= relativeX < rotatedCarImage.get_width() and 0 <= relativeY < rotatedCarImage.get_height():
                    pixelColor = screen.get_at((int(x), int(y)))

                    # Check if the screen pixel is white (collision detected)
                    if pixelColor == white:
                        return True 
    return False 

def drawFinishLine(x, y, width, height, numBoxes):
    boxWidth = width // numBoxes
    for col in range(numBoxes):
        for row in range(0,height, 5):
            if col % 2 == 0:
                if row % 2 == 0:
                    pygame.draw.rect(screen, darkGreen, pygame.Rect(x + col * boxWidth, y+row, boxWidth, 5))
                else:
                    pygame.draw.rect(screen, lightGreen, pygame.Rect(x + col * boxWidth, y+row, boxWidth, 5))       
            else:
                if row % 2 == 0:
                    pygame.draw.rect(screen, lightGreen, pygame.Rect(x + col * boxWidth, y+row, boxWidth, 5))
                else:
                    pygame.draw.rect(screen, darkGreen, pygame.Rect(x + col * boxWidth, y+row, boxWidth, 5))       


# Drawing loop
drawingEvent = True
simulating = True
while drawingEvent:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            drawingEvent = False
            simulating = False
        
        # Handle color change keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                clearScreen()  # Clear screen on 'C' key press
            # Change brush size on '1-5' key press
            elif event.key == pygame.K_1:
                brushRadius = 10
            elif event.key == pygame.K_2:
                brushRadius = 20
            elif event.key == pygame.K_3:
                brushRadius = 30
            elif event.key == pygame.K_4:
                brushRadius = 40
            elif event.key == pygame.K_5:
                brushRadius = 50

        # Start drawing when mouse button is pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            if startButtonRect.collidepoint(event.pos):
                # Button clicked, transition to simulation
                drawingEvent = False
            else: 
                drawing = True
                lastPos = event.pos

        # Stop drawing when mouse button is released
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        # Track mouse movement to draw circles
        if event.type == pygame.MOUSEMOTION and drawing:
            currentPos = event.pos
            if lastPos:
                # Draw smooth circles instead of lines
                drawCircle(screen, drawingColor, lastPos, currentPos, brushRadius)
            lastPos = currentPos

    # Draw the images
    drawFinishLine(finishLineX, finishLineY, 30, 100, 3)  # x, y, width, height, number of boxes

    # Draw start button to screen
    screen.blit(startButton, (startButtonX, startButtonY))

    # Update the display
    pygame.display.flip()
    
# Save User's track
startButton.fill((255,255,255))
screen.blit(startButton, (startButtonX, startButtonY))
pygame.display.flip()
userTrack = screen.copy()

# Simulation loop
while simulating:
    dt = clock.tick(60) / 1000 # Get the change in time between framesa

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulating = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                cars[0].throttlePosition = min(cars[0].throttlePosition + .1, 1)
            elif event.key == pygame.K_s:
                cars[0].throttlePosition = max(cars[0].throttlePosition - .1, 0)
            elif event.key == pygame.K_a:
                cars[0].currentWheelAngle = max(cars[0].currentWheelAngle - math.radians(3), -cars[0].calculateMaxSteeringAngle())
            elif event.key == pygame.K_d:
                cars[0].currentWheelAngle = min(cars[0].currentWheelAngle + math.radians(3), cars[0].calculateMaxSteeringAngle())
    
    screen.blit(userTrack, (0,0))
    # Draw cars to screen
    for x in range(numCars):
        cars[x].updateVelocity(dt)
        cars[x].updateCarPosition(dt)
        cars[x].displayCar(screen)
        cars[x].castLines(screen)        

    # Update the display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(60)

pygame.quit()