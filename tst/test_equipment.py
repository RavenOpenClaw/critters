"""
Property-based tests for equipment system (Task 27).
"""
import unittest
from hypothesis import given, strategies as st
from equipment import Equipment, EQUIPMENT_REGISTRY
from entity import Player

class TestEquipmentSystem(unittest.TestCase):
    def setUp(self):
        # Clear registry before each test to avoid cross-contamination
        EQUIPMENT_REGISTRY.clear()

    def test_equipment_unlock_and_equip(self):
        """Property 31: Unlocked equipment can be equipped."""
        player = Player(0, 0)
        # Create equipment
        eq = Equipment("wooden_gatherer", "Wooden Gatherer", gather_multiplier=1.5)
        # Initially not equipped
        self.assertNotIn(eq.id, player.equipped)
        # Unlock and equip
        player.unlock_equipment(eq)
        self.assertIn(eq.id, player.unlocked_equipment)
        result = player.equip(eq.id)
        self.assertTrue(result)
        self.assertIn(eq.id, player.equipped)

    def test_cannot_equip_locked_equipment(self):
        """Equip fails for equipment that hasn't been unlocked."""
        player = Player(0, 0)
        eq = Equipment("steel_gatherer", "Steel Gatherer", gather_multiplier=2.0)
        # Try to equip without unlocking
        result = player.equip(eq.id)
        self.assertFalse(result)
        self.assertNotIn(eq.id, player.equipped)

    def test_unequip_works(self):
        """Unequip removes equipment from equipped set."""
        player = Player(0, 0)
        eq = Equipment("basic", "Basic", gather_multiplier=1.2)
        player.unlock_equipment(eq)
        player.equip(eq.id)
        self.assertIn(eq.id, player.equipped)
        player.unequip(eq.id)
        self.assertNotIn(eq.id, player.equipped)

    def test_equipment_gather_multiplier_contributes(self):
        """Property 32: Equipped gathering tool increases gather multiplier."""
        player = Player(0, 0)
        # Base multiplier = 1.0
        self.assertEqual(player.get_gather_multiplier(), 1.0)
        # Unlock and equip gear with 1.5x gather
        eq = Equipment("sharp_hands", "Sharp Hands", gather_multiplier=1.5)
        player.unlock_equipment(eq)
        player.equip(eq.id)
        self.assertEqual(player.get_gather_multiplier(), 1.5)

    def test_multiple_equipment_multipliers_stack_multiplicatively(self):
        """Multiple equipped gear multipliers multiply together."""
        player = Player(0, 0)
        eq1 = Equipment("gear1", "Gear1", gather_multiplier=1.5)
        eq2 = Equipment("gear2", "Gear2", gather_multiplier=2.0)
        player.unlock_equipment(eq1)
        player.unlock_equipment(eq2)
        player.equip(eq1.id)
        player.equip(eq2.id)
        self.assertAlmostEqual(player.get_gather_multiplier(), 1.5 * 2.0)

    def test_buffs_and_equipment_multipliers_combine(self):
        """Buff and equipment multipliers are multiplicative."""
        from buff import Buff
        player = Player(0, 0)
        eq = Equipment("strength_ring", "Ring", gather_multiplier=1.5)
        player.unlock_equipment(eq)
        player.equip(eq.id)
        buff = Buff("Gather Buff", {'gather': 2.0}, duration=10.0)
        player.active_buffs.append(buff)
        expected = 1.5 * 2.0
        self.assertAlmostEqual(player.get_gather_multiplier(), expected)

    def test_unequipped_gear_does_not_contribute(self):
        """Unlocked but unequipped gear does not affect gather multiplier."""
        player = Player(0, 0)
        eq = Equipment("lazy_tool", "Lazy", gather_multiplier=0.5)
        player.unlock_equipment(eq)
        # Not equipped yet
        self.assertEqual(player.get_gather_multiplier(), 1.0)
        player.equip(eq.id)
        self.assertEqual(player.get_gather_multiplier(), 0.5)
        player.unequip(eq.id)
        self.assertEqual(player.get_gather_multiplier(), 1.0)

    @given(
        m1=st.floats(min_value=1.0, max_value=10.0),
        m2=st.floats(min_value=1.0, max_value=10.0)
    )
    def test_gather_multiplier_bounds_always_positive(self, m1, m2):
        """Gather multiplier product is always >=1 (since multipliers >=1)."""
        player = Player(0, 0)
        eq1 = Equipment("e1", "E1", gather_multiplier=m1)
        eq2 = Equipment("e2", "E2", gather_multiplier=m2)
        player.unlock_equipment(eq1)
        player.unlock_equipment(eq2)
        player.equip(eq1.id)
        player.equip(eq2.id)
        mult = player.get_gather_multiplier()
        self.assertGreaterEqual(mult, 1.0)
        self.assertLessEqual(mult, m1 * m2)

if __name__ == '__main__':
    unittest.main()
