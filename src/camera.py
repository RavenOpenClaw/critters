"""
Camera system for scrolling the viewport to follow the player.
"""
import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        """
        Initialize the camera.
        
        Args:
            width: Viewport width (screen width).
            height: Viewport height (screen height).
            map_width: Total map width in pixels.
            map_height: Total map height in pixels.
        """
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.offset_x = 0
        self.offset_y = 0
        
        # Deadzone: camera stays still if player is within the center 50%
        # Outer 25% on each side triggers scrolling.
        self.deadzone_left = width * 0.25
        self.deadzone_right = width * 0.75
        self.deadzone_top = height * 0.25
        self.deadzone_bottom = height * 0.75

    def center_on(self, x, y):
        """Immediately center the camera on world coordinates (x, y)."""
        self.offset_x = x - self.width / 2
        self.offset_y = y - self.height / 2
        # Clamp camera to map boundaries
        self.offset_x = max(0, min(self.offset_x, self.map_width - self.width))
        self.offset_y = max(0, min(self.offset_y, self.map_height - self.height))

    def update(self, player_x, player_y):
        """
        Update camera offset to follow the player based on deadzone logic.
        
        Args:
            player_x, player_y: Player's world coordinates.
        """
        # Calculate player position relative to current camera (screen position)
        screen_x = player_x - self.offset_x
        screen_y = player_y - self.offset_y
        
        # Check horizontal deadzone
        if screen_x < self.deadzone_left:
            self.offset_x -= (self.deadzone_left - screen_x)
        elif screen_x > self.deadzone_right:
            self.offset_x += (screen_x - self.deadzone_right)
            
        # Check vertical deadzone
        if screen_y < self.deadzone_top:
            self.offset_y -= (self.deadzone_top - screen_y)
        elif screen_y > self.deadzone_bottom:
            self.offset_y += (screen_y - self.deadzone_bottom)
            
        # Clamp camera to map boundaries
        self.offset_x = max(0, min(self.offset_x, self.map_width - self.width))
        self.offset_y = max(0, min(self.offset_y, self.map_height - self.height))

    def apply(self, x, y):
        """Map world coordinates to screen coordinates."""
        return x - self.offset_x, y - self.offset_y

    def undo(self, screen_x, screen_y):
        """Map screen coordinates to world coordinates."""
        return screen_x + self.offset_x, screen_y + self.offset_y
    
    def apply_rect(self, rect):
        """Return a new Rect shifted by the camera offset."""
        return rect.move(-self.offset_x, -self.offset_y)
