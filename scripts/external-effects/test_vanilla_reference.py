"""Independent JVM naming regressions for mapped and unrenamed classes."""
import tempfile
import unittest
from pathlib import Path

from vanilla_reference import MojangNames


class MojangNamesTests(unittest.TestCase):
    def test_unrenamed_package_names_use_jvm_owners_and_descriptors(self):
        mapping = (
            'net.minecraft.server.MinecraftServer -> net.minecraft.server.MinecraftServer:\n'
            '    java.lang.Iterable getAllLevels() -> K\n'
            'net.minecraft.commands.CommandSourceStack -> ep:\n'
            '    net.minecraft.server.MinecraftServer getServer() -> l\n'
            '    net.minecraft.commands.CommandSourceStack withEntity(net.minecraft.world.entity.Entity) -> a\n'
            'net.minecraft.world.entity.Entity -> bsr:\n'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mappings.txt'
            path.write_text(mapping)
            names = MojangNames(path)
        server = 'net/minecraft/server/MinecraftServer'
        self.assertEqual(names.named[server], server)
        self.assertEqual(names.obfuscated[server], server)
        self.assertEqual(names.descriptor('net.minecraft.server.MinecraftServer'), 'L'+server+';')
        self.assertEqual(names.descriptor('net.minecraft.server.MinecraftServer[]'), '[L'+server+';')
        self.assertEqual(names.member(server, 'K', '()Ljava/lang/Iterable;'), 'getAllLevels')
        self.assertEqual(names.member('ep', 'l', '()L'+server+';'), 'getServer')
        self.assertEqual(names.member('ep', 'a', '(Lbsr;)Lep;'), 'withEntity')


if __name__ == '__main__':
    unittest.main()
