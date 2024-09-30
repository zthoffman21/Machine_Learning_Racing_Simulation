import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Racing Line Simulation")

# Set up colors
white = (255, 255, 255)
drawing_color = (0, 0, 0)

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

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle window resizing event
        if event.type == pygame.VIDEORESIZE:
            # Update the screen size
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            clear_screen()  # Clear the screen and redraw finish line on resize

        
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

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()