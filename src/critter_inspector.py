"""
Critter Inspector UI: displays stats of a selected critter.
"""
import pygame
from critter import Critter, CritterState

class CritterInspector:
    """Shows detailed stats for a selected critter in a fixed side panel."""
    def __init__(self, cell_size, font, screen_width, screen_height):
        self.cell_size = cell_size
        self.font = font
        self.visible = False
        self.selected_critter = None
        # Panel dimensions
        self.panel_width = 220
        self.panel_height = 360 # Increased slightly for stat totals
        self.panel_margin = 10
        self.reposition(screen_width, screen_height)
        
        # Follow button rect (below stats)
        self.follow_button_rect = None
        self.stat_rects = {} # Map stat names to rects for 'Use Candy' clicks

    def reposition(self, screen_width, screen_height):
        """Update panel position to stay anchored to the top-right corner."""
        self.panel_rect = pygame.Rect(
            screen_width - self.panel_width - self.panel_margin,
            self.panel_margin,
            self.panel_width,
            self.panel_height
        )
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - self.close_button_size - 5,
            self.panel_rect.top + 5,
            self.close_button_size,
            self.close_button_size
        )

    def toggle(self, critter=None):
        """Toggle visibility. If a critter is provided, show that critter's stats."""
        if critter is not None:
            self.selected_critter = critter
            self.visible = True
        else:
            self.visible = not self.visible

    def hide(self):
        self.visible = False
        self.selected_critter = None

    def handle_mouse_click(self, pos, player=None, world=None):
        """Check if click is within the inspector panel; consume it. If on close button, hide panel.
        Returns True if click was consumed (panel visible and click inside panel), False otherwise."""
        if not self.visible:
            return False
        # If click inside panel rect, consume
        if self.panel_rect.collidepoint(pos):
            # If on close button, hide panel
            if self.close_button_rect.collidepoint(pos):
                self.hide()
            elif self.follow_button_rect and self.follow_button_rect.collidepoint(pos):
                if player and world:
                    self.toggle_follow(player, world)
            else:
                # Check for stat candy clicks
                for stat_name, rect in self.stat_rects.items():
                    if rect.collidepoint(pos):
                        if player and world:
                            self.use_candy_on_stat(player, world, stat_name)
            return True
        return False

    def use_candy_on_stat(self, player, world, stat_name):
        """Use a candy from player inventory to boost the selected critter's stat."""
        if self.selected_critter is None:
            return
        
        from constants import ITEM_CANDY_STR, ITEM_CANDY_SPD, ITEM_CANDY_END
        candy_map = {
            "strength": ITEM_CANDY_STR,
            "speed_stat": ITEM_CANDY_SPD,
            "endurance": ITEM_CANDY_END
        }
        candy_item = candy_map.get(stat_name)
        if not candy_item:
            return

        # Check if player has the candy
        if player.inventory.get_item_count(candy_item) > 0:
            current_val = getattr(self.selected_critter, stat_name)
            if current_val < 100:
                player.inventory.remove(candy_item, 1)
                setattr(self.selected_critter, stat_name, current_val + 1)
                world.set_message(f"Used {candy_item}! {stat_name.replace('_stat','').capitalize()} increased to {current_val+1}.", 2.0)
            else:
                world.set_message("Stat is already at maximum (100).", 1.5)
        else:
            world.set_message(f"You don't have any {candy_item}.", 1.5)

    def toggle_follow(self, player, world):
        """Toggle follow mode for the selected critter.
        - If critter already following, stop following.
        - If not following, start following the player.
        Provides feedback via world.message.
        """
        if self.selected_critter is None:
            return
        c = self.selected_critter
        from critter import CritterState
        from constants import MESSAGE_FOLLOW_STOP, MESSAGE_FOLLOW_START
        if c.state == CritterState.FOLLOW:
            c.stop_follow()
            world.set_message(MESSAGE_FOLLOW_STOP, 2.0)
        else:
            # Start following; this will also stop any existing following critter
            c.start_follow(player)
            world.set_message(MESSAGE_FOLLOW_START, 2.0)

    def draw(self, screen, player=None):
        if not self.visible or self.selected_critter is None:
            return
        # Draw panel background
        pygame.draw.rect(screen, (240, 240, 240), self.panel_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.panel_rect, 2)
        # Draw close button (X)
        pygame.draw.rect(screen, (200, 200, 200), self.close_button_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.close_button_rect, 1)
        # X lines
        x, y, s = self.close_button_rect.x, self.close_button_rect.y, self.close_button_size
        pygame.draw.line(screen, (0, 0, 0), (x+4, y+4), (x+s-4, y+s-4), 2)
        pygame.draw.line(screen, (0, 0, 0), (x+s-4, y+4), (x+4, y+s-4), 2)
        # Prepare stats text
        from constants import (
            INSPECTOR_TITLE, LABEL_STATE, LABEL_STRENGTH, LABEL_SPEED,
            LABEL_ENDURANCE, LABEL_CAPACITY, LABEL_HELD, LABEL_GATHER_SPEED,
            LABEL_MOVE_SPEED, ITEM_CANDY_STR, ITEM_CANDY_SPD, ITEM_CANDY_END
        )
        c = self.selected_critter
        
        # Helper to render lines and track stat rects
        x0 = self.panel_rect.x + 10
        y0 = self.panel_rect.y + 10
        line_spacing = self.font.get_linesize()
        self.stat_rects = {}

        # Title
        text = self.font.render(INSPECTOR_TITLE, True, (0, 0, 0))
        screen.blit(text, (x0, y0))
        y_curr = y0 + line_spacing

        # State
        text = self.font.render(f"{LABEL_STATE}{c.state.name}", True, (0, 0, 0))
        screen.blit(text, (x0, y_curr))
        y_curr += line_spacing

        # Core Stats with Candy Indicators
        stat_configs = [
            (LABEL_STRENGTH, c.strength, "strength", ITEM_CANDY_STR, (200, 50, 50)), # Red
            (LABEL_SPEED, c.speed_stat, "speed_stat", ITEM_CANDY_SPD, (50, 150, 50)), # Green
            (LABEL_ENDURANCE, c.endurance, "endurance", ITEM_CANDY_END, (50, 50, 200)) # Blue
        ]

        for label, val, attr, candy, color in stat_configs:
            stat_str = f"{label}{val}"
            text = self.font.render(stat_str, True, color)
            screen.blit(text, (x0, y_curr))
            
            # If player has candy, show a clickable (+) next to stat
            if player and player.inventory.get_item_count(candy) > 0 and val < 100:
                plus_text = self.font.render(" (+)", True, (0, 150, 0))
                plus_rect = plus_text.get_rect(topleft=(x0 + text.get_width(), y_curr))
                screen.blit(plus_text, plus_rect)
                self.stat_rects[attr] = plus_rect
            
            y_curr += line_spacing

        # Stat Total
        total_str = f"Stat Total: {c.strength + c.speed_stat + c.endurance}"
        total_text = self.font.render(total_str, True, (0, 0, 0))
        screen.blit(total_text, (x0, y_curr))
        y_curr += line_spacing

        # Derived stats and inventory
        der_lines = [
            f"{LABEL_CAPACITY}{c.carry_capacity}",
            LABEL_HELD,
        ]
        if c.inventory.items:
            for res, qty in c.inventory.items.items():
                der_lines.append(f"  {res}: {qty}")
        else:
            der_lines.append(f"  (none)")
            
        der_lines.extend([
            f"{LABEL_GATHER_SPEED}{c.get_gather_speed():.2f}/s",
            f"{LABEL_MOVE_SPEED}{c.get_movement_speed():.1f}",
        ])
        
        from constants import LABEL_BUFFS, VALUE_ASSIGNED_NONE, LABEL_ASSIGNED
        if c.active_buffs:
            der_lines.append(LABEL_BUFFS)
            for b in c.active_buffs:
                der_lines.append(f"  {b.name} ({b.remaining:.1f}s)")
        else:
            der_lines.append(f"{LABEL_BUFFS} {VALUE_ASSIGNED_NONE}")
        
        assigned_hut = getattr(c, 'assigned_hut', None)
        if assigned_hut is not None:
            hut_name = type(assigned_hut).__name__
            der_lines.append(f"{LABEL_ASSIGNED} {hut_name}")
        else:
            der_lines.append(f"{LABEL_ASSIGNED} {VALUE_ASSIGNED_NONE}")

        for line in der_lines:
            text = self.font.render(line, True, (0, 0, 0))
            screen.blit(text, (x0, y_curr))
            y_curr += line_spacing

        # Draw "Follow" button below stats
        btn_y = y_curr + 8
        is_following = (c.state == CritterState.FOLLOW)
        btn_text = "Stop Following" if is_following else "Follow"
        text_surf = self.font.render(btn_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect()
        btn_rect = pygame.Rect(
            x0,
            btn_y,
            text_rect.width + 16,
            line_spacing + 6
        )
        self.follow_button_rect = btn_rect
        pygame.draw.rect(screen, (100, 200, 100) if is_following else (100, 100, 200), btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 1)
        text_rect.center = btn_rect.center
        screen.blit(text_surf, text_rect)
