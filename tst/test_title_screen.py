"""
Tests for the title screen and its actions (New Game, Continue, Quit).
"""

import pytest
import pygame
from unittest.mock import patch, MagicMock
from title_screen import TitleScreen
from game_state import load_game


class TestTitleScreenContinue:
    """Test the Continue action from the title screen."""

    @pytest.fixture
    def mock_screen(self):
        """Mock Pygame screen for testing."""
        return MagicMock()

    @pytest.fixture
    def mock_save_exists(self, tmp_path):
        """Fixture to simulate an existing save file."""
        save_path = tmp_path / "save.json"
        save_path.write_text("{}")  # Minimal valid JSON
        return str(save_path)

    @pytest.fixture
    def mock_load_game_success(self):
        """Mock load_game to simulate a successful load."""
        with patch("game_state.load_game") as mock_load:
            mock_load.return_value = (MagicMock(), MagicMock())
            yield mock_load

    @pytest.fixture
    def mock_load_game_failure(self):
        """Mock load_game to simulate a failed load."""
        with patch("game_state.load_game") as mock_load:
            mock_load.side_effect = Exception("Load failed")
            yield mock_load

    def test_continue_action_sets_selected_action(self, mock_screen, mock_save_exists):
        """Test that selecting Continue sets the selected_action to continue."""
        # Setup
        title = TitleScreen(800, 600, save_path=mock_save_exists)
        
        # Simulate clicking Continue
        with patch("title_screen.load_game", return_value=(MagicMock(), MagicMock())) as mock_load:
            with patch.object(title, "check_save_exists", return_value=True):
                title.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                    "button": 1, "pos": title.continue_rect.center
                }))
        
        # Verify
        assert title.selected_action == "continue"
        mock_load.assert_called_once_with(mock_save_exists)

    def test_continue_action_falls_back_to_new_game_on_failure(self, mock_screen, mock_save_exists):
        """Test that Continue falls back to New Game if load fails."""
        # Setup
        title = TitleScreen(800, 600, save_path=mock_save_exists)
        
        # Simulate clicking Continue
        with patch("title_screen.load_game", side_effect=Exception("Load failed")) as mock_load:
            with patch.object(title, "check_save_exists", return_value=True):
                title.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                    "button": 1, "pos": title.continue_rect.center
                }))
        
        # Verify
        assert title.selected_action == "new_game"
        mock_load.assert_called_once_with(mock_save_exists)

    def test_continue_action_not_available_without_save(self, mock_screen):
        """Test that Continue is not available if no save file exists."""
        # Setup
        title = TitleScreen(800, 600, save_path="/nonexistent/save.json")
        
        # Verify
        assert title.continue_rect is None
        assert title.selected_action is None

    def test_continue_keyboard_shortcut(self, mock_screen, mock_save_exists):
        """Test that pressing 'C' triggers Continue."""
        # Setup
        title = TitleScreen(800, 600, save_path=mock_save_exists)
        
        # Simulate pressing 'C'
        with patch("title_screen.load_game", return_value=(MagicMock(), MagicMock())) as mock_load:
            with patch.object(title, "check_save_exists", return_value=True):
                title.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c}))
        
        # Verify
        assert title.selected_action == "continue"
        mock_load.assert_called_once_with(mock_save_exists)
