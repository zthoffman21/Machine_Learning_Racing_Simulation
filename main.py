import pygame
import math
import neat
from car import Car

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 1000, 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Racing Line Simulation")
clock = pygame.time.Clock()

userTrack = screen.copy()

# Set up colors
white = (255, 255, 255)
drawing_color = black  = (0, 0, 0)
darkGreen = (0,100,0)
lightGreen = (144, 238, 144)

# Set the initial position for the images
finishLine_x = screen_width/2
finishLine_y = screen_height * .9 - 37

cars = []
numCars = 1
# Create car objects
for x in range(numCars):
    cars.append(Car())
    cars[x].car_x = screen_width/2
    cars[x].car_y = screen_height * .9

# Load the button 
startButtonX = screen_width/2-60
startButtonY = 30
startButton = pygame.image.load("images/StartButton.png")
startButton = pygame.transform.scale(startButton, (120, 50)) 
startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))


# Fill background with white
screen.fill(white)

# Variables to track drawing state
drawing = False  # Whether the mouse is currently drawing
last_pos = None  # Store the last position to interpolate points

brush_radius = 50  # Default brush size

# Button to clear the screen
def clear_screen():
    screen.fill(white)

# Draw a circle with interpolation to avoid gaps
def draw_circle(screen, color, start, end, radius):
    # Calculate the distance between start and end points
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.hypot(dx, dy)

    # Interpolate between the points and draw circles to make a smooth line
    for i in range(int(distance)):
        x = int(start[0] + dx * (i / distance))
        y = int(start[1] + dy * (i / distance))
        pygame.draw.circle(screen, color, (x, y), radius)

def check_collision_with_white_pixels(screen, car_image, car_x, car_y):
    car_rect = car_image.get_rect(topleft=(car_x, car_y))
    
    for x in range(car_rect.width):
        for y in range(car_rect.height):
            # Get the pixel color at the car's position
            pixel_color = screen.get_at((car_x + x, car_y + y))
            
            # Check if the pixel is white
            if pixel_color == white:
                return True  # Collision with white pixel detected
    return False

# Function to draw a simple finish line
def draw_finish_line(x, y, width, height, num_boxes):
    box_width = width // num_boxes
    for i in range(num_boxes):
        # Alternate black and white for the checkered pattern
        color = darkGreen if i % 2 == 0 else lightGreen
        pygame.draw.rect(screen, color, pygame.Rect(x + i * box_width, y, box_width, height))


# Drawing loop
drawingEvent = True
simulating = True
while drawingEvent:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            drawingEvent = False
            simulating = False

            # Update car and finish line locations
            for x in range(numCars):
                cars[x].car_x = screen_width/2
                cars[x].car_y = screen_height * .8
            finishLine_x = screen_width/2
            finishLine_y = screen_height * .8 - 37

        
        # Handle color change keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                clear_screen()  # Clear screen on 'C' key press
            # Change brush size on '1-5' key press
            elif event.key == pygame.K_1:
                brush_radius = 10
            elif event.key == pygame.K_2:
                brush_radius = 20
            elif event.key == pygame.K_3:
                brush_radius = 30
            elif event.key == pygame.K_4:
                brush_radius = 40
            elif event.key == pygame.K_5:
                brush_radius = 50

        # Start drawing when mouse button is pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            if startButtonRect.collidepoint(event.pos):
                # Button clicked, transition to simulation
                drawingEvent = False
            else: 
                drawing = True
                last_pos = event.pos

        # Stop drawing when mouse button is released
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        # Track mouse movement to draw circles
        if event.type == pygame.MOUSEMOTION and drawing:
            current_pos = event.pos
            if last_pos:
                # Draw smooth circles instead of lines
                draw_circle(screen, drawing_color, last_pos, current_pos, brush_radius)
            last_pos = current_pos

    # Draw the images
    draw_finish_line(finishLine_x, finishLine_y, 50, 100, 5)  # x, y, width, height, number of boxes

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
                if cars[0].currentWheelAngle - 1 >= -cars[0].calculate_max_steering_angle():
                    cars[0].currentWheelAngle -= math.radians(3)
            elif event.key == pygame.K_d:
                if cars[0].currentWheelAngle + 1 <= cars[0].calculate_max_steering_angle():
                    cars[0].currentWheelAngle += math.radians(3)
    
    screen.blit(userTrack, (0,0))
    # Draw cars to screen
    for x in range(numCars):
        cars[x].updateVelocity(dt)
        cars[x].update_car_position(dt)
        cars[x].display_car(screen)
        print(cars[x].cast_lines(screen))

    # Update the display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()