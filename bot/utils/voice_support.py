from importlib.util import find_spec

import discord


def voice_stack_ready() -> bool:
    version = discord.version_info
    supports_dave = (version.major, version.minor) >= (2, 7)
    return supports_dave and all(
        find_spec(module_name) is not None for module_name in ("nacl", "davey")
    )
