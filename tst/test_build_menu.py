"""
Tests for BuildMenu mouse interaction and placement logic.
Regression: Ensure that clicking on build menu buttons does not also place a building.
"""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

import unittest
from unittest.mock import MagicMock, patch
from build_menu import BuildMenu
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire

class DummyPlayer:
    def __init__(self):
        self.inventory = MagicMock()
        self.inventory.items = {"wood": 10, "stone": 10, "stick": 10, "food": 10}

class DummyWorld:
    def __init__(self):
        self.current_map = MagicMock()
        self.current_map.width = 20
        self.current_map.height = 15
        self.current_map.cell_size = 32

class DummyGrid:
    def __init__(self):
        self.cell_size = 32
        self.width = 25
        self.height = 18
    def world_to_grid(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)
    def is_within_bounds(self, gx, gy):
        return 0 <= gx < self.width and 0 <= gy < self.height

class TestBuildMenuMouseHandling(unittest.TestCase):
    def setUp(self):
        self.cell_size = 32
        self.build_menu = BuildMenu(self.cell_size)
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)

    def _render_menu(self):
        """Helper to render the menu with visibility enabled."""
        self.build_menu.visible = True
        screen = pygame.Surface((800, 600))
        self.build_menu.render(screen, self.font)
        return screen

    def test_button_rects_are_created_after_render(self):
        """After render, button_rects should map each building class to a rect."""
        self._render_menu()
        self.assertIn(GatheringHut, self.build_menu.button_rects)
        self.assertIn(Chair, self.build_menu.button_rects)
        self.assertIn(Campfire, self.build_menu.button_rects)

    def test_handle_mouse_click_selects_building_when_inside_button(self):
        """Clicking inside a building button should select that building and return True."""
        self._render_menu()
        rect = self.build_menu.button_rects[GatheringHut]
        # Choose a point inside the rect (use center)
        click_pos = (rect.centerx, rect.centery)
        result = self.build_menu.handle_mouse_click(click_pos)
        self.assertTrue(result)
        self.assertIs(self.build_menu.selected_building_class, GatheringHut)

        # Click on Chair button
        rect = self.build_menu.button_rects[Chair]
        click_pos = (rect.centerx, rect.centery)
        result = self.build_menu.handle_mouse_click(click_pos)
        self.assertTrue(result)
        self.assertIs(self.build_menu.selected_building_class, Chair)

    def test_handle_mouse_click_returns_false_outside_buttons(self):
        """Clicking outside any button should return False and not change selection."""
        self._render_menu()
        self.build_menu.selected_building_class = GatheringHut
        # Click far from any button (e.g., top-right of menu area)
        click_pos = (self.build_menu.menu_width - 10, 40)
        result = self.build_menu.handle_mouse_click(click_pos)
        self.assertFalse(result)
        # Selection should remain unchanged
        self.assertIs(self.build_menu.selected_building_class, GatheringHut)

    def test_placement_attempt_requires_selected_building(self):
        """attempt_placement should return False if no building is selected."""
        grid = DummyGrid()
        world = DummyWorld()
        player = DummyPlayer()
        result = self.build_menu.attempt_placement(player, world, grid, 5, 5)
        self.assertFalse(result)

    def test_hud_button_toggle(self):
        """HUD button should toggle the build menu visibility."""
        self.assertFalse(self.build_menu.visible)
        self.build_menu.toggle()
        self.assertTrue(self.build_menu.visible)
        self.build_menu.toggle()
        self.assertFalse(self.build_menu.visible)

    def test_clicking_button_returns_true_to_indicate_consumed(self):
        """
        Regression: When a button is clicked, handle_mouse_click returns True.
        The main loop uses this return value to skip placement.
        """
        self._render_menu()
        rect = self.build_menu.button_rects[GatheringHut]
        click_pos = (rect.centerx, rect.centery)
        result = self.build_menu.handle_mouse_click(click_pos)
        self.assertTrue(result, "Clicking a build menu button should return True to indicate the event was consumed")

if __name__ == '__main__':
    unittest.main()
