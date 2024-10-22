import sys
import pygame
import math
import random
import neat
from configWindow import *
from car import Car

#====================================================================================================
# Configuration Parameters
capturingCheckpoints = False
captureLastGeneration = False

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

def createMasks():
    global trackMaskSurface, pixelArray, outOfBoundsMask, finishLineMask
    # Creating the masks
    trackMaskSurface = userTrack.convert_alpha()
    pixelArray = pygame.surfarray.array2d(trackMaskSurface)

    outOfBoundsMask = pygame.mask.from_threshold(
        trackMaskSurface, (255, 255, 255, 255), (1, 1, 1, 255)
    )
    finishLineMask = pygame.mask.from_threshold(
        trackMaskSurface, (144, 238, 144, 255), (1, 1, 1, 255)
    )

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

    if overlap or car.carX > screenWidth or car.carX < 0 or car.carY > screenHeight or car.carY < 0:
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
    From extensive testing, this simple fitness function seems to promote the fastest lap times because the main contributing factor are its lap times themselves. 
    However, the velocity bonus is needed so the cars are promoted to completed their first lap fast or else the ones that complete the first lap will go slowly and then 
    they will breed only slow cars giving an endless cycle. The other is a simple survival bonus needed because withtout it, the cars run into a wall endlessly or until one luckily 
    turns the corner. 

    Args:
        genome: The genome being evaluated.
        car: The car object.
        dt: Delta time since last frame.
    """

    genome.fitness += car.velocity * dt * 0.01
    genome.fitness += 10

    if car.completedLap:
        genome.fitness += 10000 / car.totalLaps[-1]
        car.completedLap = False

def evalGenomesBestTime(genomes, config):
    """
    Evaluates each genome in the population.
    During testing, I tried normalizing the inputs, but that seemed to make the cars worse. I believe this is because the front sensor is the most important, and when it is normalized, its magnitude,
    and thus impact is reduced.  

    Args:
        genomes: List of genomes to evaluate.
        config: NEAT configuration.
    """
    global font, bestLap, bestLapText, bestFirstLap, bestFirstLapText, population, fastestGenome, initialCarX, initialCarY, timeAddition

    # Initialize cars and networks
    cars = []
    alive = 0
    networks = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        car = Car(initialCarX, initialCarY, random.choice(carOptions[:3]))
        car.genomeID = genome_id
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        cars.append((car, genome))
        car.lapStart = pygame.time.get_ticks() / 1000
        alive += 1
        networks.append(net)

        car.acceleration *= racingConfigWindow.accelerationMult
        car.deceleration *= racingConfigWindow.decelerationMult
        car.downforceNewtons *= racingConfigWindow.downforceMult
        car.maxVelocity *= racingConfigWindow.maxSpeedMult

    if fastestGenome is not None:
        cars[0] = (cars[0][0], fastestGenome)
        cars[0][0].f1CarImage = carOptions[3]

    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()

    # Simulation loop
    while any(not car.crashed for car, _ in cars) and (pygame.time.get_ticks() - startTime) / 1000 < (30 * population.generation) / (19 + population.generation) + 3 + timeAddition:
        dt = clock.tick(80) / 1000  # Frame time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if plusButtonRect.collidepoint(event.pos):
                    timeAddition += 1
                    print("plus 1   Total:", timeAddition)
                if minusButtonRect.collidepoint(event.pos):
                    timeAddition -= 1
                    print("edit 1   Total:", timeAddition)
                if editButtonRect.collidepoint(event.pos):
                    if not drawingEvent():
                        pygame.quit()
                        sys.exit()
                    print("edit")

        screen.blit(userTrack, (0, 0))
        screen.blit(bestLapText, (10, 3))
        screen.blit(bestFirstLapText, (10, 3 + bestLapText.get_height() + 5))
        screen.blit(editButton, (editButtonX, editButtonY))
        screen.blit(minusButton, (minusButtonX, minusButtonY))
        screen.blit(plusButton, (plusButtonX, plusButtonY))
        

        # Update and draw each car
        for idx, (car, genome) in enumerate(cars):
            if not car.crashed:
                car.castLines(screen, pixelArray)

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
                if math.cos(car.carAngle) > 0 and checkCollisionWithFinishLine(car) and car.leftFinishLine and pygame.time.get_ticks() / 1000 - car.lapStart  >= 2:
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
                        bestLapText = font.render(
                            f"{'Best Lap:':>15} {bestLap[0]:<6.2f}  Generation: {bestLap[1]:<4}  Genome ID: {bestLap[2]:<8}",
                            True, 
                            (0, 0, 0)
                        )
                    if len(car.totalLaps) == 1 and lapTime < bestFirstLap[0]:
                        car.f1CarImage = carOptions[3]
                        bestFirstLap = (lapTime, population.generation, car.genomeID)
                        genome.fitness += 2000
                        print(f"Best First Lap: {bestFirstLap[0]:.2f} Generation: {bestFirstLap[1]} Genome ID: {bestFirstLap[2]}")
                        bestFirstLapText = font.render(
                            f"{'Best First Lap:':>15} {bestFirstLap[0]:<6.2f}  Generation: {bestFirstLap[1]:<4}  Genome ID: {bestFirstLap[2]:<8}",
                            True, 
                            (0, 0, 0)
                        )

                if not car.hitFinishLine and not car.leftFinishLine:
                    car.leftFinishLine = True

                # Calculate fitness
                fitness(genome, car, dt)

        # Display the fastest on top of the others so it can always be seen
        if fastestGenome is not None and not cars[0][0].crashed:
            cars[0][0].displayCar(screen)
        pygame.display.flip()

    print("Number of cars survived:", alive)

def evalGenomesHeadToHead(genomesRed, genomesGreen, config):
    """
    Evaluates genomes for both the Red and Green teams, displays them on the same track.
    """
    global screen, bestLapRed, bestLapGreen, bestLapRedText, bestLapGreenText, font, populationRed, populationGreen, timeAddition

    # Initialize Red and Green team cars
    carsRed = []
    carsGreen = []
    networksRed = []
    networksGreen = []

    # Initialize cars for Red team
    for genome_id, genome in genomesRed:
        genome.fitness = 0
        car = Car(initialCarX, initialCarY, carOptions[0])  # Red car
        car.genomeID = genome_id
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        carsRed.append((car, genome))
        networksRed.append(net)
        car.lapStart = pygame.time.get_ticks() / 1000

        car.acceleration *= racingConfigWindow.accelerationMultRed
        car.deceleration *= racingConfigWindow.decelerationMultRed
        car.downforceNewtons *= racingConfigWindow.downforceMultRed
        car.maxVelocity *= racingConfigWindow.maxSpeedMultRed

    # Initialize cars for Green team
    for genome_id, genome in genomesGreen:
        genome.fitness = 0
        car = Car(initialCarX, initialCarY, carOptions[2])  # Green car
        car.genomeID = genome_id
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        carsGreen.append((car, genome))
        networksGreen.append(net)
        car.lapStart = pygame.time.get_ticks() / 1000

        car.acceleration *= racingConfigWindow.accelerationMultGreen
        car.deceleration *= racingConfigWindow.decelerationMultGreen
        car.downforceNewtons *= racingConfigWindow.downforceMultGreen
        car.maxVelocity *= racingConfigWindow.maxSpeedMultGreen

    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()

    # Simulation loop
    while any(not car.crashed for car, _ in carsRed + carsGreen) and (pygame.time.get_ticks() - startTime) / 1000 < (30 * populationRed.generation) / (19 + populationRed.generation) + 3 + timeAddition:
        dt = clock.tick(60) / 1000  # Frame time

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if plusButtonRect.collidepoint(event.pos):
                    timeAddition += 1
                    print("plus 1   Total:", timeAddition)
                if minusButtonRect.collidepoint(event.pos):
                    timeAddition -= 1
                    print("edit 1   Total:", timeAddition)
                if editButtonRect.collidepoint(event.pos):
                    if not drawingEvent():
                        pygame.quit()
                        sys.exit()
                    print("edit")

        # Clear the screen and display the track
        screen.blit(userTrack, (0, 0))
        screen.blit(bestLapRedText, (10, 3))
        screen.blit(bestLapGreenText, (10, 3 + bestLapRedText.get_height() + 5))
        screen.blit(editButton, (editButtonX, editButtonY))
        screen.blit(minusButton, (minusButtonX, minusButtonY))
        screen.blit(plusButton, (plusButtonX, plusButtonY))

        # Simulate Red team
        for idx, (car, genome) in enumerate(carsRed):
            if not car.crashed:
                car.castLines(screen, pixelArray)

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
                output = networksRed[idx].activate(inputs)

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

                # Check for finish line crossing
                if math.cos(car.carAngle) > 0 and checkCollisionWithFinishLine(car) and car.leftFinishLine and pygame.time.get_ticks() / 1000 - car.lapStart  >= 2:
                    lapTime = pygame.time.get_ticks() / 1000 - car.lapStart
                    car.totalLaps.append(lapTime)
                    car.lapStart = pygame.time.get_ticks() / 1000
                    car.leftFinishLine = False
                    car.completedLap = True  # Set the flag

                    print(f"Lap: {len(car.totalLaps)} Time: {lapTime:.2f} Average: {sum(car.totalLaps) / len(car.totalLaps):.2f}")
                    if lapTime < bestLapRed[0]:
                        bestLapRed = (lapTime, populationRed.generation, car.genomeID)
                        genome.fitness += 5000
                        print(f"Best Lap: {bestLapRed[0]:.2f} Generation: {bestLapRed[1]} Genome ID: {bestLapRed[2]}")
                        bestLapRedText = font.render(
                            f"{'Best Lap:':>15} {bestLapRed[0]:<6.2f}  Generation: {bestLapRed[1]:<4}  Genome ID: {bestLapRed[2]:<8}",
                            True, 
                            (111, 0, 39)
                        )

                if not car.hitFinishLine and not car.leftFinishLine:
                    car.leftFinishLine = True

                # Calculate fitness
                fitness(genome, car, dt)

        # Simulate Green team
        for idx, (car, genome) in enumerate(carsGreen):
            if not car.crashed:
                car.castLines(screen, pixelArray)
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
                output = networksGreen[idx].activate(inputs)

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

                # Check for finish line crossing
                if math.cos(car.carAngle) > 0 and checkCollisionWithFinishLine(car) and car.leftFinishLine and pygame.time.get_ticks() / 1000 - car.lapStart  >= 2:
                    lapTime = pygame.time.get_ticks() / 1000 - car.lapStart
                    car.totalLaps.append(lapTime)
                    car.lapStart = pygame.time.get_ticks() / 1000
                    car.leftFinishLine = False
                    car.completedLap = True  # Set the flag

                    print(f"Lap: {len(car.totalLaps)} Time: {lapTime:.2f} Average: {sum(car.totalLaps) / len(car.totalLaps):.2f}")
                    if lapTime < bestLapGreen[0]:
                        bestLapGreen = (lapTime, populationGreen.generation, car.genomeID)
                        genome.fitness += 5000
                        print(f"Best Lap: {bestLapGreen[0]:.2f} Generation: {bestLapGreen[1]} Genome ID: {bestLapGreen[2]}")
                        bestLapGreenText = font.render(
                            f"{'Best Lap:':>15} {bestLapGreen[0]:<6.2f}  Generation: {bestLapGreen[1]:<4}  Genome ID: {bestLapGreen[2]:<8}",
                            True, 
                            (2, 106, 55)
                        )

                if not car.hitFinishLine and not car.leftFinishLine:
                    car.leftFinishLine = True

                # Calculate fitness
                fitness(genome, car, dt)


        # Update the display
        pygame.display.flip()

def runNeatBestTime():
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
    if racingConfigWindow.usingExistingNetwork:
        population = neat.Checkpointer.restore_checkpoint(racingConfigWindow.existingNetworkPath)
        if isinstance(population.population, neat.Population):
            population = population.population
    else:
        population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    if capturingCheckpoints:
        population.add_reporter(neat.Checkpointer(checkpointFrequency, filename_prefix='checkpoints/'))

    # Creating text variables
    global font
    font = pygame.font.SysFont("Lucida Console", 17)

    global bestLap, bestLapText
    bestLap = (math.inf, 0, 0)
    bestLapText = font.render(
        f"{'Best Lap:':>15} {bestLap[0]:<6.2f}  Generation: {bestLap[1]:<4}  Genome ID: {bestLap[2]:<8}",
        True, 
        (0, 0, 0)
    )

    global bestFirstLap, bestFirstLapText
    bestFirstLap = (math.inf, 0, 0)
    bestFirstLapText = font.render(
        f"{'Best First Lap:':>15} {bestFirstLap[0]:<6.2f}  Generation: {bestFirstLap[1]:<4}  Genome ID: {bestFirstLap[2]:<8}",
        True, 
        (0, 0, 0)
    )

    global fastestGenome
    fastestGenome = None

    winner = population.run(evalGenomesBestTime, numberOfGenerationsSimulated)

    print(f"Best genome: {winner}")
    print(f"Best Lap: {bestLap[0]:.2f} Generation: {bestLap[1]} Genome ID: {bestLap[2]}")
    print(f"Best First Lap: {bestFirstLap[0]:.2f} Generation: {bestFirstLap[1]} Genome ID: {bestFirstLap[2]}")

def runNeatHeadToHead():
    """
    Runs the NEAT algorithm with two populations (Red vs Green) concurrently.
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configFile
    )

    # Initialize populations for both teams
    global populationRed, populationGreen
    populationRed = neat.Population(config)
    populationGreen = neat.Population(config)

    # populationRed.add_reporter(neat.StdOutReporter(True))
    populationRed.add_reporter(neat.StatisticsReporter())
    # populationGreen.add_reporter(neat.StdOutReporter(True))
    populationGreen.add_reporter(neat.StatisticsReporter())

    bestRedGenome = None  # Track the best Red team genome
    bestGreenGenome = None  # Track the best Green team genome

    global font
    font = pygame.font.SysFont("Lucida Console", 17)

    global bestLapRed, bestLapRedText
    bestLapRed = (math.inf, 0, 0)
    bestLapRedText = font.render(
        f"{'Best Lap:':>15} {bestLapRed[0]:<6.2f}  Generation: {bestLapRed[1]:<4}  Genome ID: {bestLapRed[2]:<8}",
        True, 
        (111, 0, 39)
    )
    global bestLapGreen, bestLapGreenText
    bestLapGreen = (math.inf, 0, 0)
    bestLapGreenText = font.render(
        f"{'Best Lap:':>15} {bestLapGreen[0]:<6.2f}  Generation: {bestLapGreen[1]:<4}  Genome ID: {bestLapGreen[2]:<8}",
        True, 
        (2, 106, 55)
    )


    # Run evaluation for both populations
    while True:
        # Get next generation of genomes
        genomesRed = list(populationRed.population.items())
        genomesGreen = list(populationGreen.population.items())

        # Evaluate both populations head-to-head
        evalGenomesHeadToHead(genomesRed, genomesGreen, config)

        # Find the best genomes from the Red and Green teams
        bestRedGenome = max(genomesRed, key=lambda genome: genome[1].fitness)[1]
        bestGreenGenome = max(genomesGreen, key=lambda genome: genome[1].fitness)[1]

        # Report the best genomes
        populationRed.reporters.post_evaluate(config, populationRed.population, populationRed.species, bestRedGenome)
        populationGreen.reporters.post_evaluate(config, populationGreen.population, populationGreen.species, bestGreenGenome)

        # Advance both populations to the next generation
        populationRed.population = populationRed.reproduction.reproduce(
            config, populationRed.species, config.pop_size, populationRed.generation
        )
        populationGreen.population = populationGreen.reproduction.reproduce(
            config, populationGreen.species, config.pop_size, populationGreen.generation
        )

        # Handle species extinction
        populationRed.species.speciate(config, populationRed.population, populationRed.generation)
        populationGreen.species.speciate(config, populationGreen.population, populationGreen.generation)

        # Check if either population has reached its goal (e.g., a minimum fitness)
        if bestRedGenome.fitness > 25000 or bestGreenGenome.fitness > 25000 or populationRed.generation >= numberOfGenerationsSimulated:
            print(f"Simulation complete. Best Red Genome Fitness: {bestRedGenome.fitness}, Best Green Genome Fitness: {bestGreenGenome.fitness}")
            break  # End the simulation when a target fitness is reached

        populationRed.generation += 1
        populationGreen.generation += 1

def drawingEvent():
    """
    Handles the drawing event where the user can draw the track.
    """
    global screen, userTrack, initialCarX, initialCarY, screenWidth, screenHeight, finishLineX, finishLineY, startButtonX, startButtonY, startButtonRect, drawingColor, editButton, editButtonRect, minusButton, minusButtonRect, plusButton, plusButtonRect

    drawing = False
    lastPos = None
    brushRadius = 50

    screen.blit(userTrack, (0,0))
    startButton = pygame.image.load("images/StartButton.png")
    startButton = pygame.transform.scale(startButton, (100, 100))

    drawingEvent = True
    while drawingEvent:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawingEvent = False
                return False
            
            if event.type == pygame.VIDEORESIZE:
                # Update the screen size to the new window size
                screenWidth, screenHeight = event.w, event.h
                screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
                screen.fill(white)

                startButtonX = screenWidth / 2 - 50
                startButtonY = 15
                startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))

                editButtonX = screenWidth - editButton.get_width() - 5
                editButtonY = 5
                minusButtonX = screenWidth - minusButton.get_width() - 110
                minusButtonY = 5
                plusButtonX = screenWidth - plusButton.get_width() -55
                plusButtonY = 5

                editButtonRect = editButton.get_rect(topleft=(editButtonX, editButtonY))
                minusButtonRect = minusButton.get_rect(topleft=(minusButtonX, minusButtonY))
                plusButtonRect = plusButton.get_rect(topleft=(plusButtonX, plusButtonY))

                finishLineX = screenWidth / 2
                finishLineY = screenHeight * 0.9 - 50  # 50 = finishLine.height // 2
                initialCarX = screenWidth / 2 - 23
                initialCarY =  screenHeight * 0.9

                

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
                elif event.key == pygame.K_b:
                    drawingColor = black
                elif event.key == pygame.K_w:
                    drawingColor = white

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
        drawFinishLine(finishLineX-15, finishLineY, 30, 100, 3)
        screen.blit(startButton, (startButtonX, startButtonY))
        pygame.display.flip()

    # Save User's track
    startButton.fill((255, 255, 255))
    screen.blit(startButton, (startButtonX, startButtonY))
    pygame.display.flip()

    userTrack = screen.copy()  # Use user's drawn track
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    createMasks()

    return True

if __name__ == "__main__":
    racingConfigWindow = RacingConfig()
    racingConfigWindow.run()

    # Initialize Pygame
    pygame.init()

    # Set up the display
    global screenWidth, screenHeight
    screenWidth, screenHeight = 1000, 900

    global screen, userTrack
    screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
    pygame.display.set_caption("Racing Line Simulation")
    pygame.display.set_icon(pygame.image.load("images/f1Car.png"))
    clock = pygame.time.Clock()
    screen.fill((255,255,255))
    userTrack = screen.copy()

    # Set up colors
    global drawingColor
    white = (255, 255, 255)
    drawingColor = black = (0, 0, 0)
    darkGreen = (0, 100, 0)
    lightGreen = (144, 238, 144)

    # Set the initial position for the images
    global finishLineX, finishLineY
    finishLineX = screenWidth / 2
    finishLineY = screenHeight * 0.9 - 50  # 50 = finishLine.height // 2

    # Load the button
    global startButtonX, startButtonY, startButtonRect
    startButtonX = screenWidth / 2 - 50
    startButtonY = 15
    startButton = pygame.image.load("images/StartButton.png")
    startButton = pygame.transform.scale(startButton, (100, 100))
    startButtonRect = startButton.get_rect(topleft=(startButtonX, startButtonY))

    global editButton, editButtonRect, minusButton, minusButtonRect, plusButton, plusButtonRect, timeAddition
    timeAddition = 0
    editButton = pygame.transform.scale(pygame.image.load("images/editButton.png"), (40,40))
    minusButton = pygame.transform.scale(pygame.image.load("images/minusButton.png"), (40,40))
    plusButton = pygame.transform.scale(pygame.image.load("images/plusButton.png"), (40,40))

    editButtonX = screenWidth - editButton.get_width() - 5
    editButtonY = 5
    minusButtonX = screenWidth - minusButton.get_width() - 95
    minusButtonY = 5
    plusButtonX = screenWidth - plusButton.get_width() -50
    plusButtonY = 5

    editButtonRect = editButton.get_rect(topleft=(editButtonX, editButtonY))
    minusButtonRect = minusButton.get_rect(topleft=(minusButtonX, minusButtonY))
    plusButtonRect = plusButton.get_rect(topleft=(plusButtonX, plusButtonY))

    # Set up initial Positions for the cars
    global initialCarX, initialCarY
    initialCarX = screenWidth / 2 - 23
    initialCarY =  screenHeight * 0.9

    screen.fill(white)

    simulating = racingConfigWindow.headToHeadMode is not None
    if not racingConfigWindow.usingExistingTrack and racingConfigWindow.headToHeadMode is not None:
        simulating = drawingEvent()  # Flag if the user wants to simulate

    if racingConfigWindow.usingExistingTrack:
        userTrack = pygame.image.load(racingConfigWindow.existingTrackPath)  # Use existing track
        screen = pygame.display.set_mode((userTrack.get_width(), userTrack.get_height()))
        screenWidth, screenHeight = userTrack.get_width(), userTrack.get_height()
        finishLineX = screenWidth / 2
        finishLineY = screenHeight * 0.9 - 50  # 50 = finishLine.height // 2
        initialCarX = screenWidth / 2 - 23
        initialCarY =  screenHeight * 0.9

    global trackMaskSurface, pixelArray, outOfBoundsMask, finishLineMask
    if racingConfigWindow.usingExistingTrack:
        createMasks()

    # Simulating
    if simulating:
        if racingConfigWindow.headToHeadMode:
            configFile = "configFiles/configHeadToHead.txt"
            runNeatHeadToHead()
        else:
            configFile = "configFiles/config.txt"
            runNeatBestTime()


    del pixelArray
    pygame.quit()