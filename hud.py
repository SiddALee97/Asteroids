from enum import Enum, auto
from upgrades_shop import affordable_slots, auto_buy, buy, SlotState, LIGHT_COLORS, slot_state, repair
from constants import PANEL_OPEN_TIME_SCALE, PANEL_IDLE_TIME
from ships import HARRY_SLOTS, BARRY_SLOTS
import math
import pygame
from constants import (
    PANEL_CLOSE_TIME, SCREEN_WIDTH, SCREEN_HEIGHT, COMMS_WIDTH,
    COMMS_HEIGHT, HUD_MARGIN, H_PANEL_WIDTH,
    H_PANEL_HEIGHT, B_PANEL_WIDTH, B_PANEL_HEIGHT,
    PANEL_BOTTOM_GAP, PANEL_SLIDE_TIME, PANEL_BOOT_TIME,
    H_SLOT_RECTS, B_SLOT_RECTS, H_LIGHT_RECTS, B_LIGHT_RECTS,
    H_SCREEN_RECT, B_SCREEN_RECT, H_AUTO_RECT, B_AUTO_RECT,
    PANEL_PULSE_SPEED, REPAIR_TIME, REPAIR_COST, REPAIR_RUSH_COST,
    PLAYER_TURN_SPEED, PLAYER_SPEED, HUD_ACCEL_PIXELS, HUD_HIT_KICK, HUD_LEAN_PIXELS,
    HUD_SWAY_PIXELS, COMMS_STIFFNESS, COMMS_DAMPING, HARRY_STIFFNESS, HARRY_DAMPING,
    BARRY_STIFFNESS, BARRY_DAMPING, HUD_INWARD_SCALE,
    HUD_DEPTH_BARRY, HUD_DEPTH_HARRY,
)


_hud_time = 0.0
_last_rotation = None
_last_velocity = None
_kick = pygame.Vector2(0, 0)


comms_rect = pygame.Rect(
    (SCREEN_WIDTH - COMMS_WIDTH) // 2,
    SCREEN_HEIGHT - HUD_MARGIN - COMMS_HEIGHT,
    COMMS_WIDTH,
    COMMS_HEIGHT,
)


harry_rect = pygame.Rect(
    HUD_MARGIN,
    SCREEN_HEIGHT - PANEL_BOTTOM_GAP - H_PANEL_HEIGHT,
    H_PANEL_WIDTH,
    H_PANEL_HEIGHT,
)


barry_rect = pygame.Rect(
    SCREEN_WIDTH - HUD_MARGIN - B_PANEL_WIDTH,
    SCREEN_HEIGHT - PANEL_BOTTOM_GAP - B_PANEL_HEIGHT,
    B_PANEL_WIDTH,
    B_PANEL_HEIGHT,
)


def draw_panel(screen, rect):
    pygame.draw.rect(screen, (42, 45, 51), rect)        # fill color first
    pygame.draw.rect(screen, (120, 125, 135), rect, 2)  # then the outline


def draw_hud(screen):
    pass

def mouse_over_panel(pos):
    for p in (harry_panel, barry_panel):
        if p.state is PanelState.OPEN and p.drawn_rect and p.drawn_rect.collidepoint(pos):
            return True
    return False

def bias_outward(target, side):
    t = target.copy()
    if t.x * side < 0:     # pointing inward since sides are 1 and -1
        t.x *= HUD_INWARD_SCALE
    return t

def update_hud(dt, player):

    global _last_rotation, _last_velocity, _hud_time, _kick

    if player is None or dt <= 0:
        _last_rotation = None
        _last_velocity = None
        for s in (comms_spring, harry_spring, barry_spring):
            s.reset()
        return
    
    if _last_rotation is None:
        _last_rotation = player.rotation
    if _last_velocity is None:
        _last_velocity = player.velocity.copy()       

    # turn lean
    angular_speed = (player.rotation - _last_rotation) / dt
    turn = angular_speed / PLAYER_TURN_SPEED
    turn = max(-1.0, min(1.0, turn))
    lean = pygame.Vector2(-turn * HUD_LEAN_PIXELS, 0)

    # thrust / bump shove
    acceleration = (player.velocity - _last_velocity) / dt
    accel_normal = acceleration / PLAYER_SPEED
    if accel_normal.length() > 1.0:
        accel_normal.scale_to_length(1.0)  
    shove = -accel_normal * HUD_ACCEL_PIXELS

    # idle sway 
    _hud_time += dt
    sway = pygame.Vector2(
        math.sin(_hud_time * 0.8) + 0.5 * math.sin(_hud_time * 1.9 + 1.3),           # sin and cos at different rates so it doesnt oscilate in a perfect circle (cool math)
        math.cos(_hud_time * 0.6) + 0.5 * math.sin(_hud_time * 1.4 + 0.7),     # need more variance so adding more layers
    ) * HUD_SWAY_PIXELS       # scaled



    target = lean + shove + sway + _kick
    # trying a spring for each panel
    comms_spring.update(target, dt)
    harry_spring.update(bias_outward(target, -1), dt)
    barry_spring.update(bias_outward(target, 1), dt)

    _kick *= 0.85
    _last_rotation = player.rotation
    _last_velocity = player.velocity.copy()


def kick_hud(direction):
    global _kick
    if direction.length_squared() > 0:
        _kick = direction.normalize() * HUD_HIT_KICK


class PanelState(Enum):
    CLOSED = auto()
    OPENING = auto()
    BOOTING = auto()
    OPEN = auto()
    CLOSING = auto()

PANEL_DURATION = {
    PanelState.OPENING: PANEL_SLIDE_TIME,
    PanelState.BOOTING: PANEL_BOOT_TIME,
    PanelState.CLOSING: PANEL_CLOSE_TIME,
}

PANEL_NEXT = {
    PanelState.OPENING: PanelState.BOOTING,
    PanelState.BOOTING: PanelState.OPEN,
    PanelState.CLOSING: PanelState.CLOSED,
}


class Spring:
    def __init__(self, stiffness, damping):
        self.stiffness = stiffness
        self.damping = damping
        self.offset = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)

    def update(self, target, dt):
        force = (target - self.offset) * self.stiffness - self.vel * self.damping
        self.vel += force * dt
        self.offset += self.vel * dt

    def reset(self):
        self.offset.update(0, 0)
        self.vel.update(0, 0)

comms_spring = Spring(COMMS_STIFFNESS, COMMS_DAMPING)
harry_spring = Spring(HARRY_STIFFNESS, HARRY_DAMPING)
barry_spring = Spring(BARRY_STIFFNESS, BARRY_DAMPING)

class Panel:
    def __init__(self, rect, side, slots, slot_rects, lights, screen_rect, auto_rect, depth, spring):
        self.side = side
        self.rect = rect
        self.state = PanelState.CLOSED
        self.timer = 0.0

        self.drawn_rect = None
        self.image = None
        self.slots = slots
        self.selected = 0

        self.slot_rects = slot_rects
        self.label_font = None
        self.screen_font = None
        self.title_font = None
        self.light_rects = lights
        self.screen_rect = screen_rect

        self.auto_enabled = True
        self.auto_timer = 0.0
        self.auto_rect = auto_rect
        self.anim_time = 0.0

        self.repair_progress = 0.0
        self.repairing = False
        self.has_repair = any(s.key == "repair" for s in slots)  # to check for barrys panel

        self.depth = depth
        self.spring = spring 

    def enable_fonts(self):
        if self.label_font is None:
            self.label_font = pygame.font.Font(None, 16)
            self.screen_font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 26)
            self.wallet_font = pygame.font.Font(None, 20)

    def set_state(self, state):
        self.state = state
        self.timer = 0.0
    

    def toggle(self):
        if self.state is PanelState.CLOSED:
            self.set_state(PanelState.OPENING)
        elif self.state in (PanelState.OPEN, PanelState.BOOTING): 
            self.set_state(PanelState.CLOSING)


    def update(self, dt, player):

        if player is None:
            return
        
        # pulseing lights
        self.anim_time += dt

        # repair: standing order that outranks cheapest-first
        if self.repairing:
            self.repair_progress += dt / REPAIR_TIME
            if self.repair_progress >= 1.0:
                player.hull = min(player.hull + 1, player.max_hull)
                self.repair_progress = 0.0
                self.repairing = False
            
        else:
            self.repair_progress = 0.0

        # standing order: repair selected -> keep repairing until full
        if (self.has_repair
                and self.slots[self.selected].key == "repair"
                and not self.repairing
                and player.hull < player.max_hull):
            self.start_repair(player)

        # animation state machine always runs
        if self.state in PANEL_DURATION:
            self.timer += dt
            if self.timer >= PANEL_DURATION[self.state]:
                self.set_state(PANEL_NEXT[self.state])


        # auto buy machine always runs
        if self.auto_enabled and (affordable_slots(player, self.slots) or self.can_auto_repair(player)):
            scale = PANEL_OPEN_TIME_SCALE if self.state is PanelState.OPEN else 1.0
            self.auto_timer += dt * scale
            if self.auto_timer >= PANEL_IDLE_TIME:
                if not (self.can_auto_repair(player) and self.start_repair(player)):
                    auto_buy(player, self.slots)
                self.auto_timer = 0.0
        else:
            self.auto_timer = 0.0

    def can_auto_repair(self, player):
        return (
            self.has_repair
            and not self.repairing
            and player.hull <= player.max_hull / 2
            and player.scrap >= REPAIR_COST
        )

    def reset(self):
        self.set_state(PanelState.CLOSED)
        self.repair_progress = 0.0
        self.repairing = False
        self.selected = 0
        self.auto_enabled = True

    def draw(self, screen, player):
        if player is None:
            return
        
        if self.state is PanelState.CLOSED:
            return
        if self.state is PanelState.OPENING:
            progress = self.timer / PANEL_SLIDE_TIME
        elif self.state is PanelState.BOOTING:
            progress = 1.0
        elif self.state is PanelState.CLOSING:
            progress = 1.0 - (self.timer / PANEL_CLOSE_TIME)
        else:
            progress = 1.0
        progress = max(0.0, min(1.0, progress))

        r = self.rect.move(self.side * (1.0 - progress) * (self.rect.width + HUD_MARGIN), 0)
        r = r.move(round(self.spring.offset.x * self.depth), round(self.spring.offset.y * self.depth))
        self.drawn_rect = r

        if self.image is None:
            draw_panel(screen, r)
            return
        
        self.draw_lights(screen, r, player)
        screen.blit(self.image, r.topleft)

        if self.state == PanelState.OPEN:
            
            panel_screen = pygame.Rect(self.screen_rect)   
            pygame.draw.rect(screen, (24, 16, 6), panel_screen.move(r.topleft))  # Draw the background
            pygame.draw.rect(screen, (120, 125, 135), panel_screen.move(r.topleft), 2)  # Draw the outline

            self.draw_contents(screen, r, player)


    def draw_contents(self, screen, r, player):
        self.enable_fonts()

        #-------- auto toggle button -------------------
        box = pygame.Rect(self.auto_rect).move(r.topleft)
        color = (255, 220, 120) if self.auto_enabled else (190, 170, 110)
        surf = self.label_font.render("AUTO", True, color)
        screen.blit(surf, surf.get_rect(center = box.center))

        #-------- slots: label text, highlight selected one -------
        for index, s in enumerate(self.slots):   # enumerate to get indexes as well
            box = pygame.Rect(self.slot_rects[index]).move(r.topleft)
            color = (255, 220, 120) if index == self.selected else (190, 170, 110) # highlights the selected rect
            surf = self.label_font.render(s.label, True, color)
            screen.blit(surf, surf.get_rect(center = box.center))
            if index == self.selected:
                pygame.draw.rect(screen, color, box, 2)  # thicker outline

        #--------- screen readout ---------------
        screen_box = pygame.Rect(self.screen_rect).move(r.topleft)
        slot = self.slots[self.selected]
        wallet = f"{slot.currency.upper()}: {getattr(player, slot.currency)}"
        lines = [
            slot.label,           
        ]

        if slot.kind == "mode":
            if slot.key == "repair":
                lines.append(f"STATUS: {player.hull} / {player.max_hull}")
            if slot.key == "maintenance":
                lines.append(f"STATUS: ")
        else:
            level = player.levels[slot.key]
            if level >= len(slot.costs):
                lines.append("MAX")
            else:
                lines.append(f"LEVEL {level}")
                lines.append(f"NEXT: {slot.costs[level]}")

        # add level and next price lines
        y = screen_box.y + 16
        
        for index, text in enumerate(lines): # using index to filter just the title
            font = self.title_font if index == 0 else self.screen_font
            color = (255, 220, 120) if index == 0 else (224, 160, 48)
            surf = font.render(text, True, color)
            screen.blit(surf, (screen_box.x + 8, y))
            y += font.get_linesize() + (10 if index == 0 else 0) # extra spacing for the title

        # repair progress bar
        if slot.key == "repair":
            track = pygame.Rect(screen_box.x + 8, screen_box.y + 100, screen_box.width - 16, 14)
            pygame.draw.rect(screen, (40, 28, 10), track)
            fill = track.copy()
            fill.width = int(track.width * self.repair_progress)
            pygame.draw.rect(screen, (224, 160, 48), fill)
            pygame.draw.rect(screen, (120, 125, 135), track, 1)

            if self.repairing:
                text = "TURNING WRENCHES"
            elif player.hull < player.max_hull:
                text = f"COST: {REPAIR_COST}  RUSH: {REPAIR_RUSH_COST}"
            else:
                text = "HEALTHY"
            surf = self.screen_font.render(text, True, (224, 160, 48))
            screen.blit(surf, (track.x, track.bottom + 4))

        # drawing wallet seperate
        font = self.wallet_font
        color = (255, 220, 120)
        surf = font.render(wallet, True, color)
        screen.blit(surf, (screen_box.x + 75, screen_box.y + 150))




    def draw_lights(self, screen, r, player):
        for index, slot in enumerate(self.slots):
            rect = pygame.Rect(self.light_rects[index]).move(r.topleft)
            state = slot_state(player, slot)
            dark = LIGHT_COLORS[SlotState.UNAFFORDABLE]
            bright = LIGHT_COLORS[state]

            if state is SlotState.PURCHASEABLE:
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * PANEL_PULSE_SPEED)
                color = tuple(int(d + (b - d) * pulse) for d, b in zip(dark, bright))
            else:
                color = bright

            pygame.draw.circle(screen, (0, 0, 0), rect.center, 10)
            pygame.draw.circle(screen, color, rect.center, 8)


    def set_image(self, image):
        self.image = pygame.transform.scale(
            image, (image.get_width() * 2, image.get_height() * 2)
        )

    def handle_click(self, pos, player):

        if self.state is not PanelState.OPEN or self.drawn_rect is None:
            return


        # auto toggle loops
        toggle_rect = pygame.Rect(self.auto_rect).move(self.drawn_rect.topleft)
        if toggle_rect.collidepoint(pos):
            self.auto_enabled = not self.auto_enabled
            self.auto_timer = 0.0
            return

        # slot loops
        for index, s in enumerate(self.slot_rects):
            rect = pygame.Rect(self.slot_rects[index]).move(self.drawn_rect.topleft)
            if rect.collidepoint(pos):
                self.selected = index
                return
        # light button loops
        for index in range(len(self.light_rects)):
            rect = pygame.Rect(self.light_rects[index]).move(self.drawn_rect.topleft)
            if rect.collidepoint(pos):
                slot = self.slots[index]
                bought = buy(player, slot)
                if slot.key == "repair":
                    if self.repairing:
                        extra = REPAIR_RUSH_COST - REPAIR_COST
                        if player.scrap >= extra:
                            player.scrap -= extra
                            player.hull = min(player.hull + 1, player.max_hull)
                            self.repairing = False
                            self.repair_progress = 0.0
                    else:
                        repair(player, REPAIR_RUSH_COST)                   

    def start_repair(self, player):
        if self.repairing or player.hull == player.max_hull or player.scrap < REPAIR_COST:
            return False
        player.scrap -= REPAIR_COST
        self.repairing = True
        self.repair_progress = 0.0
        return True
    



harry_panel = Panel(harry_rect, -1, HARRY_SLOTS, H_SLOT_RECTS, H_LIGHT_RECTS, H_SCREEN_RECT, H_AUTO_RECT, HUD_DEPTH_HARRY, harry_spring)
barry_panel = Panel(barry_rect, 1, BARRY_SLOTS, B_SLOT_RECTS, B_LIGHT_RECTS, B_SCREEN_RECT, B_AUTO_RECT, HUD_DEPTH_BARRY, barry_spring)
            