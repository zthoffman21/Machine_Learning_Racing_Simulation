#=============================================================
usingExistingTrack = True
usingCheckpoint = True
capturingCheckpoints = False
captureLastGeneration = True

existingTrackPath = "images/hardTest.png"
checkpointPath = "checkpoints/neat-checkpoint-128-hardTrack"
configFiles = [ # Allows user to set multiple config files that will run one after another
    "configFiles/config1.txt"
]

checkpointFrequency = 100
numberOfGenerationsSimulated = 1
#=============================================================
import sys
import pygame
import math
import neat
from car import Car

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

def checkCollisionWithWhitePixels(car):
    angle_degrees = -math.degrees(car.carAngle)

    # Rotate the car image
    rotatedCarImage = pygame.transform.rotate(car.f1CarImage, angle_degrees)
    rotatedCarRect = rotatedCarImage.get_rect(center=(car.carX, car.carY))
    carMask = pygame.mask.from_surface(rotatedCarImage)

    # Calculate the offset between the car and the track
    offsetX = rotatedCarRect.left
    offsetY = rotatedCarRect.top

    # Check for overlap
    overlap = outOfBoundsMask.overlap(carMask, (offsetX, offsetY))
    if overlap:
        car.crashed = True

def checkCollisionWithFinishLine(car):
    angle_degrees = -math.degrees(car.carAngle)

    # Rotate the car image
    rotatedCarImage = pygame.transform.rotate(car.f1CarImage, angle_degrees)
    rotatedCarRect = rotatedCarImage.get_rect(center=(car.carX, car.carY))
    carMask = pygame.mask.from_surface(rotatedCarImage)

    # Calculate the offset between the car and the track
    offsetX = rotatedCarRect.left
    offsetY = rotatedCarRect.top

    # Check for overlap
    overlap = finishLineMask.overlap(carMask, (offsetX, offsetY))
    if overlap:
        car.hitFinishLine = True
    else: 
        car.hitFinishLine = False
    return car.hitFinishLine

def drawFinishLine(x, y, width, height, numBoxes):
    # Calculate the width of the box based on finish line width and number of cols
    boxWidth = width // numBoxes

    # Drawing the finish line to the screen
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

def fitness(genome, car, dt):
    # Encourage cars to move forward by rewarding based on their velocity
    genome.fitness += car.velocity * dt * 10  # Scale factor can be adjusted

    total = len(car.totalLaps)
    # Provide a significant bonus when a car completes a lap
    if total > genome.totalLaps:
        genome.totalLaps = total
        genome.fitness += 1000

    # Encourage maintaining higher speeds even if a lap isn't completed
    if total == genome.totalLaps:
        genome.fitness += car.velocity * dt * 5

    # Discourage cars from getting too close to out-of-bounds areas
    if car.frontCast < 20:
        genome.fitness -= (20 - car.frontCast) * 10 
    else:
        genome.fitness += car.velocity * dt

    # Penalize for crashing
    if car.crashed:
        genome.fitness -= 5000  

def evalGenomes(genomes, config):
    global bestLap
    global bestLapText
    global population

    # Initialize cars and networks
    cars = []
    alive = 0
    networks = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        genome.totalLaps = 0  
        car = Car(screenWidth/2 - 25, screenHeight * .9)
        car.genomeID = genome_id
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        cars.append((car, genome))
        alive += 1
        networks.append(net)

    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()

    # While there are still cars alive and this it is still under the calculated time constraint = ax/(b+x) where a = 30, b = 19, and x = generation
    while any(not car.crashed for car, _ in cars) and (pygame.time.get_ticks() - startTime) / 1000 < (30 * population.generation) / (19 + population.generation) + 3:
        dt = clock.tick(80) / 1000  # Frame time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(userTrack, (0, 0))
        screen.blit(bestLapText, (3,3))

        # Update and draw each car
        for idx, (car, genome) in enumerate(cars):
            if not car.crashed:
                car.castLines(screen)
                inputs = [
                    car.frontCast, 
                    car.leftCast, 
                    car.rightCast, 
                    car.left30AngleCast,
                    car.right30AngleCast,
                    car.left45AngleCast,
                    car.right45AngleCast,
                    car.velocity, 
                    car.maxWheelAngle,
                    car.currentWheelAngle
                    ]

                output = networks[idx].activate(inputs)

                # Forces cars to accelerate and limits turning radius in the first 2 second
                # This helps keep cars from crashing into the wall right away
                if (pygame.time.get_ticks() - startTime) / 1000 < 2:
                    car.throttlePosition = .55
                    car.currentWheelAngle = (output[1] * 2 - 1) * car.maxWheelAngle * .2
                else:
                    car.throttlePosition = output[0] 
                    # Ouputs 0-1 and that determines how far to turn the wheel depending on the max wheen angle
                    # 0-0.5 = left turns and 0.5-1 = right turns
                    car.currentWheelAngle = (output[1] * 2 - 1) * car.maxWheelAngle 

                # Update car
                car.updateVelocity(dt)
                car.updateCarPosition(dt)
                car.displayCar(screen)

                # Check if new position caused it to crash
                checkCollisionWithWhitePixels(car)
                if car.crashed: alive -= 1

                # Check if car hits finish line
                if checkCollisionWithFinishLine(car) and car.leftFinishLine: # Car is on the finish line and wasn't the frame before
                    # Update lap data
                    lapTime = pygame.time.get_ticks() / 1000 - car.lapStart 
                    car.totalLaps.append(lapTime)
                    car.lapStart = pygame.time.get_ticks() / 1000
                    car.leftFinishLine = False

                    if len(car.totalLaps) > 1 and not car.firstLap: 
                        car.firstLap = True
                        del car.totalLaps[0]
                    if car.firstLap:
                        # Prints lap data to the terminal
                        print(f"{'Lap:':<4} {len(car.totalLaps):<8} {'Time:':<5} {lapTime:<25} {'Average:':<8} {sum(car.totalLaps) / len(car.totalLaps):<40}")
                        if lapTime < bestLap[0]:
                            bestLap = (lapTime, population.generation, car.genomeID)
                            print(f"{'Best Lap:':<9} {bestLap[0]:<8} {'Generation:':<11} {bestLap[1]:<3} {'Genome ID:':<8} {bestLap[2]:<3}")
                            bestLapText = bestLapText = pygame.font.Font(None, 30).render((f"{'Best Lap:':<9} {round(bestLap[0], 5):<8} {'Generation:':<11} {bestLap[1]:<3} {'Genome ID:':<8} {bestLap[2]:<3}"), True, (0, 0, 0))

                if not car.hitFinishLine and not car.leftFinishLine: # Car is not on the finish line but was before
                    car.leftFinishLine = True
                
                # Calculate fitness
                fitness(genome, car, dt)

        pygame.display.flip()
    # Prints the number of cars that didn't crash during the generation
    print("Alive", alive)

def runNeat():
    # Load config file
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configFile
    )
    # Create population
    global population
    if usingCheckpoint:
        population = neat.Checkpointer.restore_checkpoint(checkpointPath)  # ** USE THIS TO RESTORE FROM CHECKPOINT **
    else:
        population = neat.Population(config) # ** USE THIS TO CREATE A NEW POPULATION **
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    if capturingCheckpoints:
        population.add_reporter(neat.Checkpointer(checkpointFrequency, filename_prefix='checkpoints/'))
    
    # Allows other functions to see the bestLap
    # Initialized in runNeat() because I want the best lap time for the model
    global bestLap
    bestLap = (math.inf, 0, 0) 
    global bestLapText
    bestLapText = pygame.font.Font(None, 30).render((f"{'Best Lap:':<9} {round(bestLap[0], 4):<8} {'Generation:':<11} {bestLap[1]:<3} {'Genome ID:':<8} {bestLap[2]:<3}"), True, (0, 0, 0))

    # Run NEAT for n generations
    winner = population.run(evalGenomes, numberOfGenerationsSimulated)
    
    print(f"Best genome: {winner}")
    print((f"{'Best Lap:':<9} {round(bestLap[0], 4):<8} {'Generation:':<11} {bestLap[1]:<3} {'Genome ID:':<8} {bestLap[2]:<3}"), True, (0, 0, 0))

    # Saves the checkpoint after all generations have run
    if captureLastGeneration:
        fileName = 'checkpoints/configFile-' + configFile.split("/")[1].replace(".txt","") + "_Time-" + str(round(bestLap[0], 5)) + "_Track-"
        if usingExistingTrack:
            fileName += existingTrackPath.split("/")[1].replace(".png", "") + "_Gen-"
        else:
            fileName += "userTrack_Gen-"
        checkpointer = neat.Checkpointer(filename_prefix=fileName)
        checkpointer.save_checkpoint(config=config, generation=population.generation, population=population, species_set=population.species)

def drawingEvent():
    # Variables to track drawing state
    drawing = False 
    lastPos = None 
    brushRadius = 50  # Default brush size

    # Drawing loop
    drawingEvent = True
    while drawingEvent:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawingEvent = False
                return False
            
            # Handle color change keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    screen.fill(white)  # Clear screen on 'C' key press
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
    return True

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

# Load the button 
startButtonX = screenWidth/2-60
startButtonY = 30
startButton = pygame.image.load("images/StartButton.png")
startButton = pygame.transform.scale(startButton, (120, 50)) 
startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))


# Fill background with white
screen.fill(white)

simulating = drawingEvent() # Flag if the user wants to simulate

# Save User's track
startButton.fill((255,255,255))
screen.blit(startButton, (startButtonX, startButtonY))
pygame.display.flip()

if not usingExistingTrack:
    userTrack = screen.copy() # ** USE THIS TO HAVE IT LEARN ON YOUR DRAWN TRACK **
else:
    userTrack = pygame.image.load(existingTrackPath) # ** USE THIS TO HAVE IT LEARN ON A GIVEN TRACK **

# Creating the masks
trackMaskSurface = userTrack.convert_alpha()
outOfBoundsMask = pygame.mask.from_threshold(
    trackMaskSurface,
    (255, 255, 255, 255),   # Color to match (white)
    (1, 1, 1, 255)           # Tolerance
)
finishLineMask = pygame.mask.from_threshold(
    trackMaskSurface, 
    (144, 238, 144, 255),
    (1, 1, 1, 255)
)

if simulating:
    for path in configFiles:
        configFile = path
        runNeat()

pygame.quit()