from camera import camera
from world import world
from shockwave import Shockwave
from constants import *
from shot import Shot
from circleshape import CircleShape
import pygame
import math


class Player(CircleShape):
    def __init__(self, x: float, y: float, radius: float):
        super().__init__(x, y, radius)
        self.rotation = 0
        self.cdt = 0

        # added mutables for upgrades
        self.speed = PLAYER_SPEED
        self.turn_speed = PLAYER_TURN_SPEED
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        self.shoot_speed = PLAYER_SHOOT_SPEED
        self.radius = PLAYER_RADIUS
        self.weapon = "DEFAULT"
        self.weapon_level = 0

        # adding base velocity and friction coefficient for momentum calcs
        self.velocity = pygame.Vector2(0, 0)
        self.friction = 0.98 # loses 2% speed per second


    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        # triangle will stay in world space because collides with () uses it
        # convert to screen space at last moment before drawing

        pts = [camera.world_to_screen(p) for p in self.triangle()]
        pygame.draw.polygon(screen, "white", pts, camera.line(LINE_WIDTH))

    def rotate(self, dt: float):
        self.rotation += self.turn_speed * dt

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

        # new momentum code
        # 1. apply friction over time (import math to use math.pow (ensures friction scales evenly regardless of frame rate))
        self.velocity *= math.pow(self.friction, dt * 60) # instead of just multiplying by friction we use math.pow to tie the reduction to the frame rate so it is independent of computer speed

        # 2. update your position based on new velocity
        self.position += self.velocity * dt


        if keys[pygame.K_SPACE] and self.cdt <= 0:
                self.cdt = self.current_cooldown()
                self.shoot()

        # no more screen wrapping! time for soft border!
        world.pull_inside(self, dt, margin=60, strength=15)


    def move(self, dt: float):
        # instead of moving position, we add "thrust" to velocity
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        
        # accelerate
        self.velocity += rotated_vector * self.speed * dt


    def shoot(self):
        # refactoring shoot so we can change the weapon type
        if self.weapon == "MULTISHOT":
            self.fire_parallel(self.weapon_level + 1)
        elif self.weapon == "SHOCKWAVE":
            self.fire_shockwave()
        else:
            self.fire_bullet(self.rotation)

        # adding logic for shockwave
    def fire_shockwave(self):
        max_radius = 150 + 50 * (self.weapon_level - 1)
        Shockwave(self.position.x, self.position.y, max_radius)

    def current_cooldown(self) -> float:
        cd = self.shoot_cooldown
        if self.weapon == "SHOCKWAVE":
            cd *= 4.0
        return max(0.08, cd)

        # adding logic for multishot
    def fire_parallel(self, count: int, spacing: float = 12):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        side = direction.rotate(90) # makes bullets line up with width of player
        for i in range(count):
            offset = (i - (count - 1) /2) * spacing # spaces shots evenly and centers the group on player
            pos = self.position + side * offset
            shot = Shot(pos.x, pos.y)
            shot.velocity = direction * self.shoot_speed

        # adding fire_bullet
    def fire_bullet(self, angle: float):
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(angle) * self.shoot_speed

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
            p1 = vertices[i]
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




























































