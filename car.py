import pygame
import math

class Car:
    """
    Represents a car in the F1 simulation.
    """

    def __init__(self, x, y, carColor):
        """
        Initializes the car with position (x, y) and color.

        Args:
            x: Initial x-coordinate.
            y: Initial y-coordinate.
            carColor: Pygame surface representing the car's image.
        """
        # Load the car
        self.f1CarImage = carColor
        self.genomeID = None

        # Status flags
        self.crashed = False
        self.hitFinishLine = True
        self.leftFinishLine = False
        self.lapStart = 0
        self.totalLaps = []
        self.completedLap = False

        # Position and movement
        self.carX = x
        self.carY = y
        self.carAngle = 0  # Angle in relation to the screen (radians)
        self.currentWheelAngle = 0
        self.maxWheelAngle = math.radians(20)

        # Sensor readings
        self.frontCast = 0
        self.leftCast = 0
        self.rightCast = 0
        self.left30AngleCast = 0
        self.right30AngleCast = 0
        self.left45AngleCast = 0
        self.right45AngleCast = 0

        # Physics properties
        self.mass = 1760  # lbs
        self.coefficientOfFriction = 1.8
        self.downforce = 4500  # lbs
        self.downforceNewtons = self.downforce * 4.44822  # Convert to Newtons
        self.wheelBase = 8  # ft

        # Kinematic properties
        self.velocity = 0  # ft/s
        self.minimunVelocity = 200
        self.maxVelocity = 330 * 1.3  # ft/s (~225 mph)
        self.passedMin = False
        self.minVelAch = 0

        self.torque = 1000  # lb-ft
        self.brakingPower = 30000  # Reflects braking forces of 4-5 Gs
        self.wheelRadius = 1.2  # ft
        self.deceleration = self.brakingPower / (self.mass * self.wheelRadius) * 100  # ft/s^2
        self.acceleration = self.torque / (self.mass * self.wheelRadius) * 1000  # ft/s^2
        self.throttlePosition = 0.5  # 0-1 scale

    def updateVelocity(self, dt):
        """
        Updates the car's velocity based on throttle position and time delta.

        Args:
            dt: Delta time since last frame.
        """
        if self.throttlePosition > 0.5:
            throttleValue = (self.throttlePosition - 0.5) * 3
            self.velocity = min(self.velocity + self.acceleration * dt * throttleValue, self.maxVelocity)
        elif self.throttlePosition < 0.5:
            brakeValue = (0.5 - self.throttlePosition) * 2
            self.velocity = max(self.velocity - self.deceleration * dt * brakeValue, 0)

        if self.passedMin:
            self.velocity = max(self.velocity, self.minimunVelocity)
        else:
            self.velocity = max(self.velocity, self.minVelAch)
        if not self.passedMin and self.velocity > self.minimunVelocity:
            self.passedMin = True

        self.maxWheelAngle = self.calculateMaxSteeringAngle()
        if self.currentWheelAngle < 0:
            self.currentWheelAngle = max(-self.maxWheelAngle, self.currentWheelAngle)
        else:
            self.currentWheelAngle = min(self.maxWheelAngle, self.currentWheelAngle)

    def calculateMaxLateralAcceleration(self):
        """
        Calculates the maximum lateral acceleration before losing traction.

        Returns:
            Lateral acceleration in m/s^2.
        """
        massKG = self.mass * 0.453592  # Convert lbs to kg
        g = 9.81  # Gravitational acceleration in m/s^2
        lateralAcceleration = (self.coefficientOfFriction * g) + (self.downforceNewtons / (massKG * 0.075))
        return lateralAcceleration  # m/s^2

    def calculateTurningRadius(self):
        """
        Calculates the turning radius based on current velocity and lateral acceleration.

        Returns:
            Turning radius in meters.
        """
        maxLateralAcceleration = self.calculateMaxLateralAcceleration()
        velocityMeterSecond = self.velocity * 0.3048  # Convert ft/s to m/s

        if maxLateralAcceleration > 0:
            turningRadius = (velocityMeterSecond ** 2) / maxLateralAcceleration
            return turningRadius  # meters
        else:
            return float('inf')

    def calculateMaxSteeringAngle(self):
        """
        Calculates the maximum steering angle before losing traction.

        Returns:
            Maximum steering angle in radians.
        """
        turningRadius = self.calculateTurningRadius()
        if turningRadius == 0:
            return self.maxWheelAngle

        steeringAngleRadians = math.atan(self.wheelBase / (turningRadius / 0.3048))  # Convert radius to ft
        return min(steeringAngleRadians, math.radians(20))

    def updateCarPosition(self, dt):
        """
        Updates the car's position based on velocity, steering angle, and time delta.

        Args:
            dt: Delta time since last frame.
        """
        self.updateVelocity(dt)

        if self.velocity > 0 and self.currentWheelAngle != 0:
            turningRadius = self.wheelBase / math.tan(self.currentWheelAngle)
            angularVelocity = self.velocity / turningRadius
        else:
            angularVelocity = 0

        if angularVelocity != 0:
            self.carAngle += angularVelocity * dt

        self.carX += self.velocity * math.cos(self.carAngle) * dt
        self.carY += self.velocity * math.sin(self.carAngle) * dt

    def displayCar(self, screen):
        """
        Renders the car on the screen.

        Args:
            screen: The pygame surface to draw on.
        """
        rotatedCarImage = pygame.transform.rotate(self.f1CarImage, -math.degrees(self.carAngle))
        rotatedRect = rotatedCarImage.get_rect(center=(self.carX, self.carY))
        screen.blit(rotatedCarImage, rotatedRect.topleft)

    def castLine(self, screen, angleOffset=0, maxDistance=500):
        """
        Casts a line from the car to detect edges of the track.

        Args:
            screen: The pygame surface to use.
            angleOffset: Angle offset from the car's heading.
            maxDistance: Maximum distance to check.

        Returns:
            Distance to the edge of the track, or if not found, returns max distance.
        """
        adjustedAngle = self.carAngle + angleOffset
        directionX = math.cos(adjustedAngle)
        directionY = math.sin(adjustedAngle)

        white = (255, 255, 255)
        width = screen.get_width()
        height = screen.get_height()
        startX = self.carX
        startY = self.carY

        # Get the pixel array
        pixelArray = pygame.surfarray.pixels2d(screen)
        step = 10

        distance = 0
        while distance < maxDistance:
            currentX = int(startX + directionX * distance)
            currentY = int(startY + directionY * distance)

            if 0 <= currentX < width and 0 <= currentY < height:
                color = screen.unmap_rgb(pixelArray[currentX, currentY])
                if color == white:
                    break
            else:
                # Out of bounds; treat as edge
                break

            distance += step  # Increment by step size

        # Refine the edge detection by checking the last few pixels
        for i in range(step):
            testDistance = max(distance - step + i, 0)
            currentX = int(startX + directionX * testDistance)
            currentY = int(startY + directionY * testDistance)

            if 0 <= currentX < width and 0 <= currentY < height:
                color = screen.unmap_rgb(pixelArray[currentX, currentY])
                if color == white:
                    distance = testDistance
                    break
            else:
                distance = testDistance
                break

        # pygame.draw.line(screen, (255, 0, 0), (startX, startY), (int(startX + directionX * distance), int(startY + directionY * distance)), 1)

        return distance

    def castLines(self, screen):
        """
        Casts multiple lines (sensors) from the car in different directions.

        Args:
            screen: The pygame surface to use.
        """
        self.frontCast = self.castLine(screen)
        self.leftCast = self.castLine(screen, math.radians(-90), 300)
        self.rightCast = self.castLine(screen, math.radians(90), 300)
        self.left45AngleCast = self.castLine(screen, math.radians(-45), 300)
        self.right45AngleCast = self.castLine(screen, math.radians(45), 300)
        self.left30AngleCast = self.castLine(screen, math.radians(-30), 300)
        self.right30AngleCast = self.castLine(screen, math.radians(30), 300)