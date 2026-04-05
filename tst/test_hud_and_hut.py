"""Tests for HUD rendering and GatheringHut interaction (Task 25)."""
import unittest
from unittest.mock import Mock, patch
from entity import Player
from main import render_hud
from gathering_hut import GatheringHut
from world import World
from grid_system import GridSystem
from critter import Critter


def test_hud_shows_player_inventory():
    """Test that HUD displays player inventory correctly."""
    player = Player(0, 0)
    player.inventory.add("food", 5)
    player.inventory.add("wood", 2)

    mock_font = Mock()
    def mock_render(text, antialias, fg_color, bg=None):
        surf = Mock()
        surf.get_rect.return_value = Mock(center=(0,0))
        surf.get_width.return_value = len(text) * 6
        return surf
    mock_font.render.side_effect = mock_render

    mock_screen = Mock()

    with patch('pygame.draw.rect') as mock_draw_rect:
        render_hud(mock_screen, player, mock_font, margin=10, icon_size=12)
        assert mock_draw_rect.call_count == 2
        assert mock_screen.blit.call_count == 2


def test_gathering_hut_withdraw_interaction():
    """Test that interacting with GatheringHut transfers storage to player."""
    grid = GridSystem(cell_size=32, width=25, height=19)
    world = World(grid)
    hut = GatheringHut(0, 0, 32)
    hut.storage.add("food", 10)
    world.add_object(hut)

    player = Player(60, 60)  # within interaction radius
    player.inventory.add("wood", 5)

    player.interact(world)

    assert player.inventory.get_item_count("food") == 10
    assert player.inventory.get_item_count("wood") == 5
    assert hut.storage.items == {}


def test_gathering_hut_interaction_prompt():
    """Test that hut shows prompt only when storage nonempty."""
    empty_hut = GatheringHut(0, 0, 32)
    assert empty_hut.get_interaction_text() is None

    full_hut = GatheringHut(0, 0, 32)
    full_hut.storage.add("food", 3)
    assert full_hut.get_interaction_text() == "Press E to collect resources"


def test_gathering_hut_interaction_at_edge():
    """Player can interact with large hut even when center is far beyond interaction_radius,
    as long as interact circle touches the hut's collision box."""
    grid = GridSystem(cell_size=32, width=25, height=19)
    world = World(grid)
    hut = GatheringHut(0, 0, 32)  # rectangle: (0,0) to (96,96)
    hut.storage.add("food", 10)
    world.add_object(hut)

    # Player at (130, 48): center distance ~82 > 45, but circle overlaps right edge (96) because leftmost point = 85.
    player = Player(130, 48)
    player.inventory.add("wood", 5)

    player.interact(world)

    assert player.inventory.get_item_count("food") == 10
    assert hut.storage.items == {}


def test_gathering_hut_no_interaction_when_far():
    """Player cannot interact if even the interact circle does not touch the hut."""
    grid = GridSystem(cell_size=32, width=25, height=19)
    world = World(grid)
    hut = GatheringHut(0, 0, 32)
    hut.storage.add("food", 10)
    world.add_object(hut)

    # Player at x=200, far enough that circle (radius 45) does not reach hut (right edge 96)
    player = Player(200, 48)
    player.inventory.add("wood", 5)

    player.interact(world)

    assert player.inventory.get_item_count("food") == 0
    assert hut.storage.get_item_count("food") == 10


class TestGatheringHutAssignmentViaInteract(unittest.TestCase):
    def test_assigns_following_critter(self):
        """GatheringHut.interact assigns player's following critter when present."""
        grid = GridSystem(cell_size=32, width=10, height=10)
        world = World(grid)
        hut = GatheringHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        player.following_critter = critter
        hut.interact(player)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIs(critter.assigned_hut, hut)
        self.assertIsNone(player.following_critter)
        self.assertEqual(world.message, "Critter assigned to Gathering Hut.")

    def test_assign_clears_following_even_if_already_assigned(self):
        """Assignment clears following flag even if critter already assigned to this hut."""
        grid = GridSystem(cell_size=32, width=10, height=10)
        world = World(grid)
        hut = GatheringHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        hut.assign_critter(critter)
        player.following_critter = critter
        hut.interact(player)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIsNone(player.following_critter)

    def test_assign_unassigns_from_previous_hut(self):
        """Assigning a following critter to this hut unassigns it from any other hut."""
        grid = GridSystem(cell_size=32, width=20, height=20)
        world = World(grid)
        hut1 = GatheringHut(5, 5, 32)
        hut2 = GatheringHut(15, 15, 32)
        world.add_object(hut1)
        world.add_object(hut2)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        hut1.assign_critter(critter)
        self.assertIn(critter, hut1.assigned_critters)
        self.assertIs(critter.assigned_hut, hut1)
        player.following_critter = critter
        hut2.interact(player)
        self.assertNotIn(critter, hut1.assigned_critters)
        self.assertIn(critter, hut2.assigned_critters)
        self.assertIs(critter.assigned_hut, hut2)
        self.assertIsNone(player.following_critter)

    def test_assign_does_not_assign_non_player(self):
        hut = GatheringHut(0, 0, 32)
        try:
            hut.interact("not a player")
        except Exception as e:
            self.fail(f"interact raised an exception with non-player: {e}")
