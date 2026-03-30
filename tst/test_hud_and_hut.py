def test_hud_shows_player_inventory():
    """Test that HUD displays player inventory correctly."""
    from unittest.mock import Mock, patch
    from entity import Player
    from main import render_hud

    # Create player with inventory
    player = Player(0, 0)
    player.inventory.add("food", 5)
    player.inventory.add("wood", 2)

    # Mock font and screen
    mock_font = Mock()
    def mock_render(text, antialias, fg_color, bg=None):
        surf = Mock()
        surf.get_rect.return_value = Mock(center=(0,0))
        surf.get_width.return_value = len(text) * 6
        return surf
    mock_font.render.side_effect = mock_render

    mock_screen = Mock()

    # Patch pygame.draw.rect to avoid needing a real Surface
    with patch('pygame.draw.rect') as mock_draw_rect:
        render_hud(mock_screen, player, mock_font, margin=10, icon_size=12)
        # Should draw one rect per resource (icon)
        assert mock_draw_rect.call_count == 2
        # Verify blit called for text (food, wood)
        assert mock_screen.blit.call_count == 2
