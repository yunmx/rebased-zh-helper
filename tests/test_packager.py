import tempfile
import unittest
import zipfile
from pathlib import Path

from rebased_zh_helper.packager import (
    PackagingError, build_package, find_descriptor_jar,
    patch_descriptor, target_branch,
)

XML = '''<?xml version="1.0" encoding="utf-8"?>
<idea-plugin><id>com.example.test.localization</id>
<name>Sample Chinese Language Pack</name><version>263.7307.200</version>
<idea-version since-build="263.7307.200" until-build="263.7307.999"/>
</idea-plugin>'''


def fixture_plugin(root: Path) -> tuple[Path, Path]:
    plugin = root / "localization-zh"
    lib = plugin / "lib"
    lib.mkdir(parents=True)
    jar = lib / "localization-zh.jar"
    with zipfile.ZipFile(jar, "w") as z:
        z.writestr("META-INF/plugin.xml", XML)
        z.writestr("messages/TestBundle.properties", "test.hello=synthetic sample")
    (lib / "plugin-classpath.txt").write_text("synthetic core index - must not ship", encoding="utf-8")
    return plugin, jar


class Tests(unittest.TestCase):
    def test_branch(self):
        self.assertEqual(target_branch("IC-263.7307.SNAPSHOT"), "263.7307")
        self.assertEqual(target_branch("263.7307.200"), "263.7307")
        with self.assertRaises(PackagingError):
            target_branch("bad")

    def test_patch(self):
        new, old = patch_descriptor(XML, "IC-263.7307.SNAPSHOT")
        self.assertEqual(old, "263.7307.200")
        self.assertIn('since-build="263.7307"', new)
        self.assertIn('until-build="263.*"', new)
        with self.assertRaises(PackagingError):
            patch_descriptor(XML, "IC-262.11879.SNAPSHOT")

    def test_package_and_unchanged_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plugin, source_jar = fixture_plugin(root)
            original_bytes = source_jar.read_bytes()
            output, old = build_package(plugin, "IC-263.7307.SNAPSHOT", root / "out.zip")
            self.assertEqual(old, "263.7307.200")
            self.assertEqual(source_jar.read_bytes(), original_bytes)
            self.assertTrue(output.exists())
            with zipfile.ZipFile(output) as pkg:
                self.assertIsNone(pkg.testzip())
                self.assertNotIn("localization-zh/lib/plugin-classpath.txt", pkg.namelist())
                with pkg.open("localization-zh/lib/localization-zh.jar") as nested:
                    with zipfile.ZipFile(nested) as jar:
                        self.assertIn('since-build="263.7307"', jar.read("META-INF/plugin.xml").decode())
                        self.assertEqual(jar.read("messages/TestBundle.properties"), b"test.hello=synthetic sample")
            output2, _ = build_package(plugin, "IC-263.7307.SNAPSHOT", root / "out.zip")
            self.assertEqual(output2.name, "out-2.zip")

    def test_reject_incompatible_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plugin, jar = fixture_plugin(root)
            out = root / "bad.zip"
            with self.assertRaises(PackagingError):
                build_package(plugin, "IC-261.1.SNAPSHOT", out)
            self.assertFalse(out.exists())
            self.assertEqual(find_descriptor_jar(plugin), jar)


if __name__ == "__main__":
    unittest.main()
