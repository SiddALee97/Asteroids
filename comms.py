import pygame
from constants import (
    COMMS_CHARS_PER_SECOND, COMMS_HOLD_TIME, COMMS_SPRITE_SCALE,
    COMMS_LIGHTS, LIGHT_BLINK_INVUL, LIGHT_BLINK_SLOW, LIGHT_BLINK_FAST,
    PANEL_IDLE_TIME,
)
from upgrades_shop import affordable_slots

LIGHT_ON = ((255, 68, 74), (140, 171, 255), (179, 255, 85))
LIGHT_OFF = (75, 61, 68)

class Comms:
    def __init__(self):
        self.queue = []
        self.current_message = None
        self.chars = 0.0        # float: number of characters sent
        self.hold_timer = 0.0   # float: how long the current message stays up
        self.seen = set()       # set: keys for say_once
        self.font = None  # Default font and size
        self.light_phase = [0.0, 0.0, 0.0]
        self.light_lit = [False, False, False]
        
    def say(self, message):
        # Add a message to the queue
        self.queue.append(message)

    def say_once(self, key, message):
        if key not in self.seen:
            self.seen.add(key)
            self.say(message)

    def wrap_text(self, text, font, width):
        # Wrap text to fit within a given width
        lines = []
        words = text.split(' ')
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())
        return lines

    def update(self, dt):
        # Update the hold timer and check if we need to move to the next message
        if self.current_message is None:
            if not self.queue:
                return
            self.current_message = self.queue.pop(0)
            self.chars = 0.0
            self.hold_timer = 0.0

        # type and hold once finished    
        if self.chars < len(self.current_message):
            self.chars += COMMS_CHARS_PER_SECOND * dt  # Adjust the speed of character display here


        else:
            self.hold_timer += dt
            if self.hold_timer >= COMMS_HOLD_TIME:
                self.current_message = None

    def update_lights(self, dt, player, harry, barry):
        if player is None:
            self.light_lit = [False, False, False]
            return
        # blink rate per light
        rates = [0.0, 0.0, 0.0]
        solid = [False, False, False]
        if player.invulnerability_timer > 0:
            rates[0] = LIGHT_BLINK_INVUL
        for i, panel in ((1, harry), (2, barry)):
            can_buy = bool(affordable_slots(player, panel.slots))
            if panel.auto_enabled:
                if panel.auto_timer > 0 or barry.repairing:
                    progress = min(1.0, panel.auto_timer / PANEL_IDLE_TIME)
                    rates[i] = LIGHT_BLINK_SLOW + (LIGHT_BLINK_FAST - LIGHT_BLINK_SLOW) * progress
            elif can_buy:
                solid[i] = True
        
        for i in range(3):

            if solid[i]:
                self.light_lit[i] = True

            elif rates[i] == 0.0:
                self.light_phase[i] = 0.0       # reset lit next t
                self.light_lit[i] = False
            else:
                self.light_phase[i] += rates[i] * dt
                self.light_lit[i] = (self.light_phase[i] % 1.0) < 0.5



    def draw_lights(self, screen, origin, player, harry, barry):
        states = self.light_lit
        for i, light in enumerate(COMMS_LIGHTS):
            box = pygame.Rect(light).move(origin)
            pygame.draw.rect(screen, (0, 0, 0), box.inflate(2, 2))
            color = LIGHT_ON[i] if states[i] else LIGHT_OFF
            pygame.draw.rect(screen, color, box)


    def draw(self, screen, rect, image, player, harry, barry):
        # adjust for the screen on comms panel
        if self.font is None:
            self.font = pygame.font.Font(None, 24)  # Default font and size
        comms_screen = rect.inflate(-64, -28)  # Adjust for padding
        pygame.draw.rect(screen, (24, 16, 6), comms_screen)  # Draw the background
        pygame.draw.rect(screen, (120, 125, 135), comms_screen, 2)  # Draw the outline
        # scale the comms panel image to fit the rect
        size_h = int(image.get_height() * COMMS_SPRITE_SCALE)
        size_w = int(image.get_width() * COMMS_SPRITE_SCALE)
        scaled_image = pygame.transform.scale(image, (size_w, size_h))
        # Draw the scaled image centered in the rect
        image_rect = scaled_image.get_rect(center=rect.center)

        # lights before so image is overlayed
        self.draw_lights(screen, image_rect.topleft, player, harry, barry)

        screen.blit(scaled_image, image_rect)



        if self.current_message is None:
            surf = self.font.render("STANDBY", True, (110, 75, 25))
            text_rect = surf.get_rect(center=comms_screen.center)
            screen.blit(surf, text_rect)

        else:
            # Draw the current message up to the number of characters typed
            lines = self.wrap_text(self.current_message, self.font, comms_screen.width - 16)  
            remaining = int(self.chars)
            y = comms_screen.y + 8
            for line in lines:
                if remaining <= 0:
                    break
                surf = self.font.render(line[:remaining], True, (115, 90, 70))
                screen.blit(surf, (comms_screen.x + 8, y))
                remaining -= len(line)
                y += self.font.get_linesize()

        
        

    def reset(self):
        self.queue.clear()
        self.current_message = None
        self.chars = 0.0
        self.hold_timer = 0.0


# shared instance of Comms for the game
hud_comms = Comms()