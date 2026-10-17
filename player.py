from constants import *
from shot import Shot
from circleshape import CircleShape
import pygame



class Player(CircleShape):
    def __init__(self, x: float, y: float, radius: float):
        super().__init__(x, y, radius)
        self.rotation = 0
        self.cdt = 0
        


    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            if self.cdt > 0:
                pass
            else:
                self.cdt = PLAYER_SHOOT_COOLDOWN_SECONDS
                self.shoot()

    def move(self, dt: float):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0,1).rotate(self.rotation)
        shot.velocity *= PLAYER_SHOOT_SPEED
        
            #Overrides CircleShape to check Traingle 
    def collides_with(self, other: CircleShape) -> bool:
        vertices = self.triangle()
        circle_center = other.position
        circle_radius = other.radius

        inside = True
        for i in range(3):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % 3]  # '% or modulo' use to loop to the first point. very cool

            # vector along edge
            edge = p2 - p1

            # vector from vertex to asteroids center
            to_circle = circle_center - p1

            # logic to check if center of asteroid is inside player 'cross product'
            cross_product = edge.x * to_circle.y - edge.y * to_circle.x
            if cross_product < 0:
                inside = False
                break
        if inside:
            return True


        for i in range(3):
            p1 = vertices[1]
            p2 = vertices[(i + 1) % 3]
            edge = p2 - p1
            to_circle = circle_center - p1

            # dot projection for calculating closest point along a line segment that is infinte

            edge_length_sq = edge.length_squared()

            # to avoide crashing
            if edge_length_sq == 0:
                continue

            # t is the percentage along the line segment (must be between 0.0 and 1.0)
            t = max(0.0, min(1.0, to_circle.dot(edge) / edge_length_sq))
            closest_point = p1 + edge * t

            # distance from asteroid center to closest point
            distance_to_edge = pygame.Vector2.distance_to(circle_center, closest_point)

            # use that distance with radius to calculate collision
            if distance_to_edge <= circle_radius:
                return True

        return False




























































