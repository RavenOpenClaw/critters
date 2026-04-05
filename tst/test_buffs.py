"""
Tests for Buff system (Task 24).
"""
import unittest
from unittest.mock import patch
from buff import Buff
from entity import Player

class TestBuff(unittest.TestCase):
    def test_buff_update(self):
        """Buff.update reduces remaining time; returns True while active, False when expired."""
        buff = Buff("Test", {}, 5.0)
        self.assertTrue(buff.update(2.0))
        self.assertEqual(buff.remaining, 3.0)
        self.assertTrue(buff.update(1.0))
        self.assertEqual(buff.remaining, 2.0)
        self.assertTrue(buff.update(1.5))
        self.assertAlmostEqual(buff.remaining, 0.5)
        self.assertFalse(buff.update(1.0))  # Over-expire
        self.assertEqual(buff.remaining, -0.5)

    def test_buff_multiplier_application(self):
        """Buff.multipliers dict can be queried by player."""
        buff = Buff("Speed", {'speed': 1.5}, 10.0)
        self.assertEqual(buff.multipliers['speed'], 1.5)
        self.assertNotIn('gather', buff.multipliers)

class TestPlayerBuffs(unittest.TestCase):
    def test_player_get_speed_multiplier_combines(self):
        """Player._get_speed_multiplier multiplies 'speed' multipliers from all buffs."""
        player = Player(0, 0)
        player.active_buffs = [
            Buff("A", {'speed': 2.0}, 10),
            Buff("B", {'speed': 1.5}, 10),
            Buff("C", {'gather': 2.0}, 10)  # doesn't affect speed
        ]
        self.assertAlmostEqual(player._get_speed_multiplier(), 3.0)

    def test_player_get_gather_multiplier_combines(self):
        """Player.get_gather_multiplier multiplies 'gather' multipliers."""
        player = Player(0, 0)
        player.active_buffs = [
            Buff("A", {'gather': 2.0}, 10),
            Buff("B", {'gather': 1.5}, 10),
            Buff("C", {'speed': 1.2}, 10)
        ]
        self.assertAlmostEqual(player.get_gather_multiplier(), 3.0)

    def test_player_update_removes_expired_buffs(self):
        """Player.update removes buffs that have expired."""
        player = Player(0, 0)
        b1 = Buff("Short", {}, 1.0)
        b2 = Buff("Long", {}, 5.0)
        player.active_buffs = [b1, b2]
        # Advance time: b1 expires, b2 remains
        b1.update(1.5)  # expired
        b2.update(1.0)  # still active
        player.update(dt=0)  # triggers cleanup based on current remaining
        self.assertNotIn(b1, player.active_buffs)
        self.assertIn(b2, player.active_buffs)

    def test_player_update_recalculates_speed(self):
        """Player.update recalculates speed based on active buffs."""
        player = Player(0, 0, speed=100.0)
        player.base_speed = 100.0
        buff = Buff("Speed2", {'speed': 2.0}, 10.0)
        player.active_buffs = [buff]
        player.update(dt=0)
        self.assertEqual(player.speed, 200.0)
        # Remove buff and update again
        player.active_buffs = []
        player.update(dt=0)
        self.assertEqual(player.speed, 100.0)

class TestChairAndCampfire(unittest.TestCase):
    def test_chair_applies_rested_buff(self):
        """Interacting with Chair applies Rested buff (1.5x speed)."""
        from chair import Chair
        chair = Chair(0, 0, cell_size=32)
        player = Player(0, 0)
        # Simulate interaction
        chair.interact(player)
        self.assertEqual(len(player.active_buffs), 1)
        buff = player.active_buffs[0]
        self.assertEqual(buff.name, "Rested")
        self.assertEqual(buff.multipliers['speed'], 1.5)
        self.assertEqual(buff.duration, 30.0)

    def test_campfire_applies_strength_buff(self):
        """Interacting with Campfire applies Strength buff (2.0x gather)."""
        from campfire import Campfire
        campfire = Campfire(0, 0, cell_size=32)
        player = Player(0, 0)
        campfire.interact(player)
        self.assertEqual(len(player.active_buffs), 1)
        buff = player.active_buffs[0]
        self.assertEqual(buff.name, "Warm")
        self.assertEqual(buff.multipliers['gather'], 2.0)
        self.assertEqual(buff.duration, 30.0)

class TestBuffStacking(unittest.TestCase):
    def test_reapplying_same_buff_resets_timer(self):
        """Reapplying a buff with the same name should reset its timer, not stack."""
        player = Player(0, 0)
        buff = Buff("Speed", {'speed': 1.5}, 10.0)
        # Apply first time
        player.apply_buff(buff)
        self.assertEqual(len(player.active_buffs), 1)
        self.assertEqual(player.active_buffs[0].remaining, 10.0)
        # Wait or reduce remaining to simulate time passing
        player.active_buffs[0].update(5.0)  # now 5.0 remaining
        self.assertEqual(player.active_buffs[0].remaining, 5.0)
        # Apply same buff again (new instance with duration 10)
        player.apply_buff(buff)
        self.assertEqual(len(player.active_buffs), 1)
        self.assertEqual(player.active_buffs[0].remaining, 10.0)  # reset to full

    def test_different_buffs_stack(self):
        """Applying different buff names should stack multiplicatively."""
        player = Player(0, 0)
        buff1 = Buff("Speed", {'speed': 1.5}, 10.0)
        buff2 = Buff("Haste", {'speed': 2.0}, 10.0)
        player.apply_buff(buff1)
        player.apply_buff(buff2)
        self.assertEqual(len(player.active_buffs), 2)
        # Speed multiplier should be product
        self.assertAlmostEqual(player._get_speed_multiplier(), 3.0)

if __name__ == '__main__':
    unittest.main()
