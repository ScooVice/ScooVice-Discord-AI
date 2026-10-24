import unittest
from types import SimpleNamespace

from bot.cogs.admin import Admin


def make_admin_and_interaction(
    actor_id: int = 10,
    actor_role: int = 5,
    target_id: int = 20,
    target_role: int = 4,
    bot_role: int = 10,
    owner_id: int = 1,
):
    bot_user = SimpleNamespace(id=99)
    guild = SimpleNamespace(
        me=SimpleNamespace(top_role=bot_role),
        owner_id=owner_id,
    )
    interaction = SimpleNamespace(
        guild=guild,
        user=SimpleNamespace(id=actor_id, top_role=actor_role),
    )
    target = SimpleNamespace(id=target_id, top_role=target_role)
    admin = Admin.__new__(Admin)
    admin.bot = SimpleNamespace(user=bot_user)
    return admin, interaction, target


class AdminTargetChecksTests(unittest.TestCase):
    def test_rejects_self_moderation(self):
        admin, interaction, target = make_admin_and_interaction(
            actor_id=10, target_id=10
        )

        self.assertEqual(
            admin._target_error(interaction, target),
            "You cannot target yourself.",
        )

    def test_rejects_target_at_or_above_moderator_role(self):
        admin, interaction, target = make_admin_and_interaction(target_role=5)

        self.assertEqual(
            admin._target_error(interaction, target),
            "You cannot moderate a member with an equal or higher role.",
        )

    def test_guild_owner_can_moderate_above_their_role(self):
        admin, interaction, target = make_admin_and_interaction(
            actor_id=1,
            actor_role=1,
            target_role=8,
            bot_role=10,
            owner_id=1,
        )

        self.assertIsNone(admin._target_error(interaction, target))

    def test_bot_hierarchy_still_blocks_guild_owner(self):
        admin, interaction, target = make_admin_and_interaction(
            actor_id=1,
            actor_role=10,
            target_role=10,
            bot_role=10,
            owner_id=1,
        )

        self.assertEqual(
            admin._target_error(interaction, target),
            "I cannot moderate a member with an equal or higher role.",
        )


if __name__ == "__main__":
    unittest.main()
