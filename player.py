from hit import HitKind
from camera import camera
from world import world
from shockwave import Shockwave
from constants import PLAYER_SPEED, PLAYER_TURN_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS, PLAYER_SHOOT_SPEED, PLAYER_RADIUS, SHOCKWAVE_COOLDOWN_MULT, SHOCKWAVE_FORCE, SHOCKWAVE_SPLITS, SHOCKWAVE_DAMAGE, LASER_FORCE, LASER_GENERATIONS, LASER_BASE_DAMAGE, LASER_DAMAGE_PER_LEVEL, LASER_SPEED_PER_LEVEL, LASER_MAX_SPEED_MULT, LASER_TRAIL_LENGTH, LASER_TRAIL_PER_LEVEL, LINE_WIDTH, LASER_COOLDOWN_MULT, TURRET_LENGTH, TURRET_WIDTH, TURRET_TURN_SPEED
from shot import Shot
from circleshape import CircleShape
import pygame
import math
import viewport

class Player(CircleShape):
    def __init__(self, x: float, y: float, radius: float):
        super().__init__(x, y, radius)
        self.rotation = 0
        self.cdt = 0

        # added mutables for upgrades
        self.image = pygame.image.load("assets/ship.png").convert_alpha()
        self.speed = PLAYER_SPEED
        self.turn_speed = PLAYER_TURN_SPEED
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        self.shoot_speed = PLAYER_SHOOT_SPEED
        self.radius = PLAYER_RADIUS
        self.weapon_levels = {"MULTISHOT": 0, "SHOCKWAVE": 0, "LASER": 0}
        self.weapon_cooldowns = {"SHOCKWAVE": 0.0, "LASER": 0.0}

        # adding base velocity and friction coefficient for momentum calcs
        self.velocity = pygame.Vector2(0, 0)
        self.friction = 0.98 # loses 2% speed per second

        # adding mouse tracker for aiming
        self.aim = pygame.Vector2(0, 1)


    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw_turret(self, screen):
        if self.weapon_levels["LASER"] > 0:
            front = self.position - self.aim * TURRET_LENGTH * 0.25
            back = self.position + self.aim * TURRET_LENGTH * 0.75
            side = self.aim.rotate(90) * TURRET_WIDTH / 2
            tip = self.aim * TURRET_LENGTH * 0.75
            pts = [back + side, front + side, front - side, back - side]
            pts = [camera.world_to_screen(p) for p in pts]
            pygame.draw.polygon(screen, "white", pts, camera.line(LINE_WIDTH))


    def draw(self, screen: pygame.Surface) -> None:
        # triangle will stay in world space because collides with () uses it
        # convert to screen space at last moment before drawing

        pts = [camera.world_to_screen(p) for p in self.triangle()]
        pygame.draw.polygon(screen, "white", pts, camera.line(LINE_WIDTH))
        self.draw_turret(screen)

        # testing sprite 

        pos = camera.world_to_screen(self.position)
        rotated = pygame.transform.rotate(self.image, -self.rotation + 180)
        rect = rotated.get_rect(center=pos)
        screen.blit(rotated, rect)

    def rotate(self, dt: float):
        self.rotation += self.turn_speed * dt

    def update_aim(self, dt):
        # mouse aiming code
        offset = camera.screen_to_world(viewport.mouse_pos()) - self.position
        if offset.length_squared() == 0:
            return self.aim
        target = offset.normalize()
        angle = self.aim.angle_to(target)      # signed angle, can be -360..360
        angle = (angle + 180) % 360 - 180      # wrap into -180..180
        step = max(-TURRET_TURN_SPEED * dt, min(TURRET_TURN_SPEED * dt, angle))
        self.aim = self.aim.rotate(step)
        return 

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()


        # tick every cd here so main.py() doesn't need player.cdt -= dt
        self.cdt -= dt
        for name in self.weapon_cooldowns:
            self.weapon_cooldowns[name] = max(0.0, self.weapon_cooldowns[name] - dt)

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

        # 3. update aim based on mouse position
        self.update_aim(dt)

        if keys[pygame.K_SPACE] and self.cdt <= 0:
                self.cdt = max(0.08, self.shoot_cooldown)
                self.fire_parallel(self.weapon_levels["MULTISHOT"] + 1)

        # time to add some more weapon buttons!
        if keys[pygame.K_q]:
            self.try_fire("SHOCKWAVE", self.fire_shockwave, SHOCKWAVE_COOLDOWN_MULT)
        if keys[pygame.K_e] or pygame.mouse.get_pressed()[0]:  # left mouse button (a held commence click could fire on frame 1 if the laser is unlocked)
            self.try_fire("LASER", self.fire_laser, LASER_COOLDOWN_MULT)

        # no more screen wrapping! time for soft border!
        world.pull_inside(self, dt, margin=60, strength=15)


    def move(self, dt: float):
        # instead of moving position, we add "thrust" to velocity
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)

        # accelerate
        self.velocity += rotated_vector * self.speed * dt

    def try_fire(self, name, fire_func, cooldown_mult):
        # lvl 0 or still cooling down do nothing
        if self.weapon_levels[name] <= 0 or self.weapon_cooldowns[name] > 0:
            return
        self.weapon_cooldowns[name] = max(0.08, self.shoot_cooldown * cooldown_mult)
        fire_func()

        # refactoring logic for shockwave
    def fire_shockwave(self):
        level = self.weapon_levels["SHOCKWAVE"]
        max_radius = 150 + 50 * (level - 1)
        force = SHOCKWAVE_FORCE[level]
        breakage = SHOCKWAVE_SPLITS[level]
        damage = SHOCKWAVE_DAMAGE[level]
        Shockwave(self.position.x, self.position.y, max_radius, damage = damage, breakage = breakage, force = force)

        # adding laser logic
    def fire_laser(self):
        kind = HitKind.LASER
        level = self.weapon_levels["LASER"]
        force = LASER_FORCE[level]
        breakage = LASER_GENERATIONS[level]
        damage = LASER_BASE_DAMAGE + LASER_DAMAGE_PER_LEVEL * (level - 1)
        speed_mult = min(1 + LASER_SPEED_PER_LEVEL * (level - 1), LASER_MAX_SPEED_MULT)
        direction = self.aim

        # shoot from the tip instead
        trail = LASER_TRAIL_LENGTH + LASER_TRAIL_PER_LEVEL * (level - 1)
        nose = self.position + self.aim * TURRET_LENGTH * 0.75
        shot = Shot(nose.x, nose.y, damage = damage, pierce = True, kind = kind, breakage = breakage, trail_length = trail, force = force)
        shot.velocity = direction * self.shoot_speed * speed_mult

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




























































