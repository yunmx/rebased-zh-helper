# Rebased Chinese Helper

[中文说明](README.md)

An unofficial open-source CLI for inspecting a Rebased build and **locally** preparing an install-from-disk plugin archive **only when you have the legal rights/permissions to modify and use the input language pack**.

This repository **does not bundle or redistribute** JetBrains' language pack, translations, JARs, or a modified plugin ZIP.

JetBrains' [Free Plugin License](https://www.jetbrains.com/legal/docs/terms/jetbrains-free-plugin-license/) may restrict modification and redistribution of components to which it applies. The MIT license in this repository covers **our original code only**. Do not publish generated archives without authorization.

## Quick start

Requirements: Python 3.10+, macOS, Rebased, access to a compatible and properly licensed `localization-zh` plugin.

```bash
python3 build.py --list-sources
# Only after checking your rights/license:
python3 build.py --target-build IC-263.7307.SNAPSHOT --acknowledge-rights
# Or explicitly select a plugin directory:
python3 build.py --source "/Applications/IntelliJ IDEA.app/Contents/plugins/localization-zh" \
  --target-build IC-263.7307.SNAPSHOT --acknowledge-rights
```

Output is created locally in `~/Downloads/Rebased-Chinese-263.7307.zip` by default. The script never changes Rebased.app, IDEA.app, or their plugin classpath indexes. Existing output files are never overwritten.

Install from Rebased **Settings → Plugins → ⚙ → Install Plugin from Disk...**, select your local ZIP, restart, then choose Chinese (Simplified) from **Appearance & Behavior → System Settings → Language and Region**.

This has a **community success report** with Rebased 1.1.24, build `IC-263.7307.SNAPSHOT`, and language pack `263.7307.200`, but the repository's automated tests are synthetic and do not establish compatibility with every build.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Upstream discussions: [#106](https://github.com/DetachHead/rebased/issues/106) and [#384](https://github.com/DetachHead/rebased/issues/384). See [draft comment](docs/upstream-comment.md).
