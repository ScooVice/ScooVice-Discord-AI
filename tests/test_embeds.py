import unittest
from types import SimpleNamespace

from bot.utils.embeds import error_embed, info_embed, success_embed, warning_embed


class EmbedStyleTests(unittest.TestCase):
    def setUp(self):
        self.bot = SimpleNamespace(
            user=SimpleNamespace(
                name="ScooVice",
                display_avatar=SimpleNamespace(url="https://example.invalid/avatar.png"),
            )
        )

    def test_status_embeds_share_branding_and_distinct_icons(self):
        builders = (
            (info_embed, "✨"),
            (success_embed, "✅"),
            (warning_embed, "⚠️"),
            (error_embed, "⛔"),
        )

        for builder, icon in builders:
            with self.subTest(builder=builder.__name__):
                embed = builder("Example", "Details", self.bot)

                self.assertTrue(embed.title.startswith(icon))
                self.assertEqual(embed.description, "Details")
                self.assertEqual(embed.author.name, "ScooVice  •  Discord Assistant")
                self.assertTrue(embed.footer.text.startswith("ScooVice"))
                self.assertEqual(
                    embed.author.icon_url,
                    "https://example.invalid/avatar.png",
                )
                self.assertIsNotNone(embed.timestamp)


if __name__ == "__main__":
    unittest.main()
