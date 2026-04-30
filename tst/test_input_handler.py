import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

import unittest
from unittest.mock import patch, MagicMock
from input_handler import InputHandler

class TestInputHandler(unittest.TestCase):
    def setUp(self):
        self.ih = InputHandler()

    @patch('input_handler.pygame.event.get')
    def test_handle_events_quit(self, mock_event_get):
        mock_event_get.return_value = [MagicMock(type=pygame.QUIT)]
        result = self.ih.handle_events()
        self.assertFalse(result)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_f3_toggle(self, mock_event_get):
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_F3)]
        self.assertFalse(self.ih.show_debug)
        self.ih.handle_events()
        self.assertTrue(self.ih.show_debug)
        # Toggle back
        self.ih.handle_events()
        self.assertFalse(self.ih.show_debug)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_interact_held(self, mock_event_get):
        # Test E
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.assertTrue(self.ih.interact_held)
        
        mock_event_get.return_value = [MagicMock(type=pygame.KEYUP, key=pygame.K_e)]
        self.ih.handle_events()
        self.assertFalse(self.ih.interact_held)
        
        # Test Space
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_SPACE)]
        self.ih.handle_events()
        self.assertTrue(self.ih.interact_held)
        
        mock_event_get.return_value = [MagicMock(type=pygame.KEYUP, key=pygame.K_SPACE)]
        self.ih.handle_events()
        self.assertFalse(self.ih.interact_held)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_build_toggle(self, mock_event_get):
        event = MagicMock(type=pygame.KEYDOWN, key=pygame.K_b)
        mock_event_get.return_value = [event]
        self.ih.handle_events()
        self.assertTrue(self.ih.build_toggle)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_mouse_click(self, mock_event_get):
        event = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(123, 456))
        mock_event_get.return_value = [event]
        self.ih.handle_events()
        self.assertTrue(self.ih.mouse_clicked)
        self.assertEqual(self.ih.mouse_pos, (123, 456))

    @patch('input_handler.pygame.key.get_pressed')
    def test_update_movement_wasd(self, mock_get_pressed):
        def make_state(keys):
            state = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False}
            state.update(keys)
            return state
        mock_get_pressed.return_value = make_state({pygame.K_w: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, -1))

if __name__ == '__main__':
    unittest.main()
