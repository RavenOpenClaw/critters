import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

import unittest
from unittest.mock import patch, MagicMock
from input_handler import InputHandler, HOLD_INTERACT_DELAY, BASE_AUTO_INTERACT_INTERVAL

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
    def test_handle_events_interact(self, mock_event_get):
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.assertFalse(self.ih.interact)
        self.ih.handle_events()
        self.assertTrue(self.ih.interact)
        # interact resets each call to handle_events
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.assertFalse(self.ih.interact)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_build_toggle(self, mock_event_get):
        event = MagicMock(type=pygame.KEYDOWN, key=pygame.K_b)
        # First call: event sets build_toggle True
        mock_event_get.return_value = [event]
        self.ih.handle_events()
        self.assertTrue(self.ih.build_toggle)
        # Second call: no events, should reset to False
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.assertFalse(self.ih.build_toggle)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_select_gathering_hut(self, mock_event_get):
        event = MagicMock(type=pygame.KEYDOWN, key=pygame.K_g)
        mock_event_get.return_value = [event]
        self.assertFalse(self.ih.select_gathering_hut)
        self.ih.handle_events()
        self.assertTrue(self.ih.select_gathering_hut)
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.assertFalse(self.ih.select_gathering_hut)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_mouse_click(self, mock_event_get):
        event = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(123, 456))
        mock_event_get.return_value = [event]
        self.assertFalse(self.ih.mouse_clicked)
        self.ih.handle_events()
        self.assertTrue(self.ih.mouse_clicked)
        self.assertEqual(self.ih.mouse_pos, (123, 456))
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.assertFalse(self.ih.mouse_clicked)

    @patch('input_handler.pygame.event.get')
    def test_handle_events_multiple_events(self, mock_event_get):
        mock_event_get.return_value = [
            MagicMock(type=pygame.KEYDOWN, key=pygame.K_b),
            MagicMock(type=pygame.KEYDOWN, key=pygame.K_g),
        ]
        self.ih.handle_events()
        self.assertTrue(self.ih.build_toggle)
        self.assertTrue(self.ih.select_gathering_hut)

    @patch('input_handler.pygame.key.get_pressed')
    def test_update_movement_wasd(self, mock_get_pressed):
        # Simulate a dict-like key state
        def make_state(keys):
            state = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False}
            state.update(keys)
            return state

        mock_get_pressed.return_value = make_state({})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, 0))

        mock_get_pressed.return_value = make_state({pygame.K_w: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, -1))

        mock_get_pressed.return_value = make_state({pygame.K_s: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, 1))

        mock_get_pressed.return_value = make_state({pygame.K_a: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (-1, 0))

        mock_get_pressed.return_value = make_state({pygame.K_d: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (1, 0))

        # Diagonal: W + D
        mock_get_pressed.return_value = make_state({pygame.K_w: True, pygame.K_d: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (1, -1))

        # Opposite keys cancel: W and S -> Y=0; A and D -> X=0
        mock_get_pressed.return_value = make_state({pygame.K_w: True, pygame.K_s: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, 0))

        mock_get_pressed.return_value = make_state({pygame.K_a: True, pygame.K_d: True})
        self.ih.update_movement()
        self.assertEqual((self.ih.move_x, self.ih.move_y), (0, 0))

if __name__ == '__main__':
    unittest.main()


class TestHoldToInteract(unittest.TestCase):
    def setUp(self):
        self.ih = InputHandler()

    @patch('input_handler.pygame.event.get')
    def test_tap_produces_one_interact_count(self, mock_event_get):
        """A single tap of E should produce exactly 1 interact_count."""
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.016)
        self.assertEqual(self.ih.interact_count, 1)

    @patch('input_handler.pygame.event.get')
    def test_no_key_produces_zero_interact_count(self, mock_event_get):
        """No E press should produce 0 interact_count."""
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.ih.update(dt=0.016)
        self.assertEqual(self.ih.interact_count, 0)

    @patch('input_handler.pygame.event.get')
    def test_hold_before_delay_produces_no_extra_interactions(self, mock_event_get):
        """Holding E for less than HOLD_INTERACT_DELAY should not auto-repeat."""
        # Press E
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.016)
        # Consume the initial tap
        self.assertEqual(self.ih.interact_count, 1)

        # Hold for just under the delay threshold
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.ih.update(dt=HOLD_INTERACT_DELAY - 0.05)
        self.assertEqual(self.ih.interact_count, 0)

    @patch('input_handler.pygame.event.get')
    def test_hold_past_delay_triggers_auto_interact(self, mock_event_get):
        """Holding E past HOLD_INTERACT_DELAY should trigger auto-repeat interactions."""
        # Press E
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.016)

        # Hold: advance past delay + one full interval
        mock_event_get.return_value = []
        self.ih.handle_events()
        self.ih.update(dt=HOLD_INTERACT_DELAY + BASE_AUTO_INTERACT_INTERVAL)
        self.assertGreaterEqual(self.ih.interact_count, 1)

    @patch('input_handler.pygame.event.get')
    def test_release_stops_auto_interact(self, mock_event_get):
        """Releasing E should stop auto-repeat interactions."""
        # Press E and advance past delay
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=HOLD_INTERACT_DELAY + BASE_AUTO_INTERACT_INTERVAL)

        # Release E
        mock_event_get.return_value = [MagicMock(type=pygame.KEYUP, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=BASE_AUTO_INTERACT_INTERVAL * 5)
        self.assertEqual(self.ih.interact_count, 0)

    @patch('input_handler.pygame.event.get')
    def test_auto_interact_rate_is_correct(self, mock_event_get):
        """Auto-repeat should fire at 1/BASE_AUTO_INTERACT_INTERVAL per second."""
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.0)

        mock_event_get.return_value = []
        self.ih.handle_events()
        # At exactly delay: _auto_timer pre-loaded to interval, auto_dt=0 -> 1 fire
        self.ih.update(dt=HOLD_INTERACT_DELAY)
        self.assertEqual(self.ih.interact_count, 1)

    @patch('input_handler.pygame.event.get')
    def test_auto_interact_rate_fires_again_after_interval(self, mock_event_get):
        """Second auto-fire should happen one interval after the first."""
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.0)

        mock_event_get.return_value = []
        self.ih.handle_events()
        # delay + 1 interval: pre-load fires once, then auto_dt=interval fires again -> 2
        self.ih.update(dt=HOLD_INTERACT_DELAY + BASE_AUTO_INTERACT_INTERVAL)
        self.assertEqual(self.ih.interact_count, 2)

    @patch('input_handler.pygame.event.get')
    def test_auto_interact_multiplier_speeds_up_rate(self, mock_event_get):
        """A multiplier of 0.5 should double the auto-interact rate."""
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=0.0)

        mock_event_get.return_value = []
        self.ih.handle_events()
        # interval = BASE*0.5; at delay: pre-load fires 1, auto_dt=BASE -> BASE/(BASE*0.5)=2 more -> 3
        self.ih.update(dt=HOLD_INTERACT_DELAY + BASE_AUTO_INTERACT_INTERVAL,
                       auto_interact_multiplier=0.5)
        self.assertEqual(self.ih.interact_count, 3)

    @patch('input_handler.pygame.event.get')
    def test_hold_state_resets_on_keyup(self, mock_event_get):
        """Internal hold state should be clean after key release."""
        mock_event_get.return_value = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_e)]
        self.ih.handle_events()
        self.ih.update(dt=HOLD_INTERACT_DELAY + 0.1)

        mock_event_get.return_value = [MagicMock(type=pygame.KEYUP, key=pygame.K_e)]
        self.ih.handle_events()

        self.assertFalse(self.ih._e_held)
        self.assertEqual(self.ih._hold_timer, 0.0)
        self.assertEqual(self.ih._auto_timer, 0.0)


if __name__ == '__main__':
    unittest.main()
