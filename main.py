import sys
import pygame
import math
import random
import neat
from car import Car

#====================================================================================================
# Configuration Parameters
usingExistingTrack = True
usingCheckpoint = False
capturingCheckpoints = False
captureLastGeneration = False

existingTrackPath = "images/hardTest.png"
checkpointPath = "checkpoints/50"
configFiles = [  # Allows user to set multiple config files that will run one after another
    "configFiles/config1.txt"
]

checkpointFrequency = 50
numberOfGenerationsSimulated = 200
#====================================================================================================
# CAR COLOR OPTIONS
redCar = pygame.transform.scale(pygame.image.load("images/f1CarRed.png"), (50, 25))
blueCar = pygame.transform.scale(pygame.image.load("images/f1CarBlue.png"), (50, 25))
greenCar = pygame.transform.scale(pygame.image.load("images/f1CarGreen.png"), (50, 25))
yellowCar = pygame.transform.scale(pygame.image.load("images/f1CarYellow.png"), (50, 25))
carOptions = [redCar, blueCar, greenCar, yellowCar]
#====================================================================================================

def drawCircle(screen, color, start, end, radius):
    """
    Draws a smooth line between start and end points by drawing circles along the path.

    Args:
        screen: The pygame surface to draw on.
        color: The color of the circles.
        start: Starting point (x, y).
        end: Ending point (x, y).
        radius: Radius of the circles.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.hypot(dx, dy)

    for i in range(int(distance)):
        x = int(start[0] + dx * (i / distance))
        y = int(start[1] + dy * (i / distance))
        pygame.draw.circle(screen, color, (x, y), radius)

def checkCollisionWithWhitePixels(car):
    """
    Checks if the car has collided with white pixels (off-track areas).

    Args:
        car: The car object.
    """
    angle_degrees = -math.degrees(car.carAngle)
    rotatedCarImage = pygame.transform.rotate(car.f1CarImage, angle_degrees)
    rotatedCarRect = rotatedCarImage.get_rect(center=(car.carX, car.carY))
    carMask = pygame.mask.from_surface(rotatedCarImage)
    offsetX = rotatedCarRect.left
    offsetY = rotatedCarRect.top
    overlap = outOfBoundsMask.overlap(carMask, (offsetX, offsetY))
    if overlap:
        car.crashed = True

def checkCollisionWithFinishLine(car):
    """
    Checks if the car has crossed the finish line.

    Args:
        car: The car object.

    Returns:
        Boolean indicating if the car has hit the finish line.
    """
    angle_degrees = -math.degrees(car.carAngle)
    rotatedCarImage = pygame.transform.rotate(car.f1CarImage, angle_degrees)
    rotatedCarRect = rotatedCarImage.get_rect(center=(car.carX, car.carY))
    carMask = pygame.mask.from_surface(rotatedCarImage)
    offsetX = rotatedCarRect.left
    offsetY = rotatedCarRect.top
    overlap = finishLineMask.overlap(carMask, (offsetX, offsetY))
    if overlap:
        car.hitFinishLine = True
    else:
        car.hitFinishLine = False
    return car.hitFinishLine

def drawFinishLine(x, y, width, height, numBoxes):
    """
    Draws a checkered finish line.

    Args:
        x, y: Position of the finish line.
        width, height: Dimensions of the finish line.
        numBoxes: Number of columns in the finish line.
    """
    boxWidth = width // numBoxes
    for col in range(numBoxes):
        for row in range(0, height, 5):
            color = darkGreen if (col + row // 5) % 2 == 0 else lightGreen
            pygame.draw.rect(screen, color, pygame.Rect(x + col * boxWidth, y + row, boxWidth, 5))

def fitness(genome, car, dt):
    """
    Calculates and updates the fitness of a genome based on the car's performance.

    Args:
        genome: The genome being evaluated.
        car: The car object.
        dt: Delta time since last frame.
    """
    # Base fitness to prevent negative starting fitness
    genome.fitness += 1

    # Reward for moving forward (scaled by velocity)
    speed_reward = (car.velocity / car.maxVelocity) * dt * 50
    genome.fitness += speed_reward

    # Penalize for crashing
    if car.crashed:
        genome.fitness -= 100  # Reduced penalty

    # Reward for completing a lap quickly
    if car.completedLap:
        genome.fitness += 5000 /  car.totalLaps[-1]  
        car.completedLap = False

    # Mild penalty for excessive steering
    steering_penalty = (abs(car.currentWheelAngle) / car.maxWheelAngle) * dt * 5
    genome.fitness -= steering_penalty

def evalGenomes(genomes, config):
    """
    Evaluates each genome in the population.

    Args:
        genomes: List of genomes to evaluate.
        config: NEAT configuration.
    """
    global bestLap
    global bestLapText
    global population
    global fastestGenome

    # Initialize cars and networks
    cars = []
    alive = 0
    networks = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        car = Car(screenWidth / 2 - 23, screenHeight * 0.9, random.choice(carOptions[:3]))
        car.genomeID = genome_id
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        cars.append((car, genome))
        car.lapStart = pygame.time.get_ticks() / 1000
        alive += 1
        networks.append(net)

    if fastestGenome is not None:
        cars[0] = (cars[0][0], fastestGenome)
        cars[0][0].f1CarImage = carOptions[3]

    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()

    # Simulation loop
    while any(not car.crashed for car, _ in cars) and (pygame.time.get_ticks() - startTime) / 1000 < (30 * population.generation) / (19 + population.generation) + 3:
        dt = clock.tick(80) / 1000  # Frame time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(userTrack, (0, 0))
        screen.blit(bestLapText, (3, 3))

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

                # Initial acceleration and steering limitations
                if (pygame.time.get_ticks() - startTime) / 1000 < 2:
                    car.throttlePosition = 0.55
                    car.currentWheelAngle = (output[1] * 2 - 1) * car.maxWheelAngle * 0.2
                else:
                    car.throttlePosition = output[0]
                    car.currentWheelAngle = (output[1] * 2 - 1) * car.maxWheelAngle

                # Update car
                car.updateVelocity(dt)
                car.updateCarPosition(dt)
                car.displayCar(screen)

                # Check for collisions
                checkCollisionWithWhitePixels(car)
                if car.crashed:
                    alive -= 1

                # Check for finish line crossing
                if checkCollisionWithFinishLine(car) and car.leftFinishLine:
                    lapTime = pygame.time.get_ticks() / 1000 - car.lapStart
                    car.totalLaps.append(lapTime)
                    car.lapStart = pygame.time.get_ticks() / 1000
                    car.leftFinishLine = False
                    car.completedLap = True  # Set the flag

                    print(f"Lap: {len(car.totalLaps)} Time: {lapTime:.2f} Average: {sum(car.totalLaps) / len(car.totalLaps):.2f}")
                    if lapTime < bestLap[0]:
                        car.f1CarImage = carOptions[3]
                        bestLap = (lapTime, population.generation, car.genomeID)
                        fastestGenome = genome
                        genome.fitness += 5000
                        print(f"Best Lap: {bestLap[0]:.2f} Generation: {bestLap[1]} Genome ID: {bestLap[2]}")
                        bestLapText = pygame.font.Font(None, 30).render(
                            f"Best Lap: {bestLap[0]:.2f} Generation: {bestLap[1]} Genome ID: {bestLap[2]}", True, (0, 0, 0)
                        )

                if not car.hitFinishLine and not car.leftFinishLine:
                    car.leftFinishLine = True

                # Calculate fitness
                fitness(genome, car, dt)

        pygame.display.flip()

    print("Number of cars survived:", alive)

def runNeat():
    """
    Runs the NEAT algorithm with the provided configuration.
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configFile
    )
    global population
    if usingCheckpoint:
        population = neat.Checkpointer.restore_checkpoint(checkpointPath)
        if isinstance(population.population, neat.Population):
            population = population.population
    else:
        population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    if capturingCheckpoints:
        population.add_reporter(neat.Checkpointer(checkpointFrequency, filename_prefix='checkpoints/'))

    global bestLap
    bestLap = (math.inf, 0, 0)
    global bestLapText
    bestLapText = pygame.font.Font(None, 30).render(
        f"Best Lap: {bestLap[0]:.2f} Generation: {bestLap[1]} Genome ID: {bestLap[2]}", True, (0, 0, 0)
    )
    global fastestGenome
    fastestGenome = None

    winner = population.run(evalGenomes, numberOfGenerationsSimulated)

    print(f"Best genome: {winner}")
    print(f"Best Lap: {bestLap[0]:.2f} Generation: {bestLap[1]} Genome ID: {bestLap[2]}")

    if captureLastGeneration:
        fileName = (
            'checkpoints/configFile-'
            + configFile.split("/")[1].replace(".txt", "")
            + "_Time-"
            + str(round(bestLap[0], 5))
            + "_Track-"
        )
        if usingExistingTrack:
            fileName += existingTrackPath.split("/")[1].replace(".png", "") + "_Gen-"
        else:
            fileName += "userTrack_Gen-"
        checkpointer = neat.Checkpointer(filename_prefix=fileName)
        checkpointer.save_checkpoint(
            config=config,
            generation=population.generation,
            population=population,
            species_set=population.species,
        )

def drawingEvent():
    """
    Handles the drawing event where the user can draw the track.
    """
    drawing = False
    lastPos = None
    brushRadius = 50

    drawingEvent = True
    while drawingEvent:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawingEvent = False
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    screen.fill(white)
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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if startButtonRect.collidepoint(event.pos):
                    drawingEvent = False
                else:
                    drawing = True
                    lastPos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False

            if event.type == pygame.MOUSEMOTION and drawing:
                currentPos = event.pos
                if lastPos:
                    drawCircle(screen, drawingColor, lastPos, currentPos, brushRadius)
                lastPos = currentPos

        drawFinishLine(finishLineX, finishLineY, 30, 100, 3)
        screen.blit(startButton, (startButtonX, startButtonY))
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
drawingColor = black = (0, 0, 0)
darkGreen = (0, 100, 0)
lightGreen = (144, 238, 144)

# Set the initial position for the images
finishLineX = screenWidth / 2
finishLineY = screenHeight * 0.9 - 50  # 50 = finishLine.height // 2

# Load the button
startButtonX = screenWidth / 2 - 60
startButtonY = 30
startButton = pygame.image.load("images/StartButton.png")
startButton = pygame.transform.scale(startButton, (120, 50))
startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))

# Fill background with white
screen.fill(white)

simulating = drawingEvent()  # Flag if the user wants to simulate

# Save User's track
startButton.fill((255, 255, 255))
screen.blit(startButton, (startButtonX, startButtonY))
pygame.display.flip()

if not usingExistingTrack:
    userTrack = screen.copy()  # Use user's drawn track
else:
    userTrack = pygame.image.load(existingTrackPath)  # Use existing track

# Creating the masks
trackMaskSurface = userTrack.convert_alpha()
outOfBoundsMask = pygame.mask.from_threshold(
    trackMaskSurface, (255, 255, 255, 255), (1, 1, 1, 255)
)
finishLineMask = pygame.mask.from_threshold(
    trackMaskSurface, (144, 238, 144, 255), (1, 1, 1, 255)
)

if simulating:
    for path in configFiles:
        configFile = path
        runNeat()

pygame.quit()