import pygame
from constants import COMMS_CHARS_PER_SECOND, COMMS_HOLD_TIME




class Comms:
    def __init__(self):
        self.queue = []
        self.current_message = None
        self.chars = 0.0        # float: number of characters sent
        self.hold_timer = 0.0   # float: how long the current message stays up
        self.seen = set()       # set: keys for say_once
        self.font = None  # Default font and size

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


    def draw(self, screen, rect):
        # adjust for the screen on comms panel
        if self.font is None:
            self.font = pygame.font.Font(None, 24)  # Default font and size
        comms_screen = rect.inflate(-64, -28)  # Adjust for padding
        pygame.draw.rect(screen, (24, 16, 6), comms_screen)  # Draw the background
        pygame.draw.rect(screen, (120, 125, 135), comms_screen, 2)  # Draw the outline



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