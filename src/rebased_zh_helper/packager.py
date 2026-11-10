"""A self-contained, conservative local JetBrains plugin ZIP packager.

This project contains no JetBrains binaries or translations. This module must
never modify an installed IDE or source plugin. Build only with proper rights.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import zipfile
from pathlib import Path


class PackagingError(Exception):
    """Safe, actionable errors for an unsupported plugin layout/build."""


BUILD_RE = re.compile(r"^(?:[A-Z]{2,8}-)?(?P<branch>\d{3}\.\d+)(?:\.(?:\d+|SNAPSHOT))?$", re.I)
IDEA_VERSION_RE = re.compile(r"<idea-version\b[^>]*?/?>", re.I | re.S)
SOURCE_FOLDER = "localization-zh"


def target_branch(build: str) -> str:
    match = BUILD_RE.fullmatch(build.strip())
    if not match:
        raise PackagingError(
            f"不支持的构建号 / unsupported target build: {build!r}. "
            "例如 IC-263.7307.SNAPSHOT"
        )
    return match.group("branch")


def find_installed_sources() -> list[Path]:
    """Only scans common macOS installation locations. Never modifies files."""
    home = Path.home()
    roots = [Path("/Applications"), home / "Applications"]
    apps: set[Path] = set()
    for root in roots:
        if root.is_dir():
            apps.update(root.glob("IntelliJ IDEA*.app"))
            apps.update(root.glob("JetBrains Toolbox/IntelliJ IDEA*.app"))
            apps.update(root.glob("JetBrains Toolbox/IntelliJ IDEA*/*.app"))
    toolbox = home / "Library/Application Support/JetBrains/Toolbox/apps"
    if toolbox.is_dir():
        apps.update(toolbox.glob("IDEA-*/ch-*/**/IntelliJ IDEA*.app"))
    found = [app / "Contents/plugins" / SOURCE_FOLDER for app in apps]
    return sorted((p for p in found if p.is_dir() and (p / "lib").is_dir()), key=str)


def normalize_source(path: Path) -> Path:
    """Accept an IDEA .app path or localization-zh directory."""
    p = path.expanduser().resolve()
    if p.suffix == ".app":
        p = p / "Contents/plugins" / SOURCE_FOLDER
    if not p.is_dir() or p.name != SOURCE_FOLDER or not (p / "lib").is_dir():
        raise PackagingError(
            f"语言包目录无效 / invalid source: {p}\n"
            "需要 IDEA.app/Contents/plugins/localization-zh"
        )
    return p


def _read_descriptor(jar: Path) -> str:
    try:
        with zipfile.ZipFile(jar) as z:
            return z.read("META-INF/plugin.xml").decode("utf-8")
    except (KeyError, UnicodeError, zipfile.BadZipFile) as e:
        raise PackagingError(f"无法读取插件描述文件 / invalid descriptor in {jar}: {e}") from e


def find_descriptor_jar(source: Path) -> Path:
    for jar in sorted((source / "lib").glob("*.jar")):
        try:
            xml = _read_descriptor(jar)
        except PackagingError:
            continue
        if "localization" in xml.lower() or "language pack" in xml.lower():
            return jar
    raise PackagingError("语言包 lib/*.jar 中没有找到 META-INF/plugin.xml")


def patch_descriptor(xml: str, target: str) -> tuple[str, str]:
    """Narrow metadata change; rejects mismatching branches and unknown XML."""
    branch = target_branch(target)
    match = IDEA_VERSION_RE.search(xml)
    if not match:
        raise PackagingError("plugin.xml 缺少 <idea-version>，拒绝修改")
    tag = match.group()
    attr_match = re.search(r"\bsince-build\s*=\s*(['\"])([^'\"]+)\1", tag)
    if not attr_match:
        raise PackagingError("plugin.xml 缺少 since-build，拒绝修改")
    original_since = attr_match.group(2)
    if target_branch(original_since) != branch:
        raise PackagingError(
            f"版本不匹配：语言包 {original_since}，目标 {target}；"
            "仅允许相同 major.minor 构建分支"
        )

    def set_attribute(tag_text: str, name: str, value: str) -> str:
        pattern = re.compile(r"\b" + re.escape(name) + r"\s*=\s*(['\"])[^'\"]+\1")
        if pattern.search(tag_text):
            return pattern.sub(f'{name}="{value}"', tag_text, count=1)
        return tag_text.replace("<idea-version", f'<idea-version {name}="{value}"', 1)

    new_tag = set_attribute(tag, "since-build", branch)
    new_tag = set_attribute(new_tag, "until-build", branch.split(".")[0] + ".*")
    return xml[: match.start()] + new_tag + xml[match.end() :], original_since


def _copy_and_patch_jar(source_jar: Path, destination_jar: Path, build: str) -> str:
    """Preserves non-descriptor archive entries; never edits the source jar."""
    with zipfile.ZipFile(source_jar) as src:
        descriptor = src.read("META-INF/plugin.xml").decode("utf-8")
        patched, original_since = patch_descriptor(descriptor, build)
        with zipfile.ZipFile(destination_jar, "w") as dst:
            for item in src.infolist():
                if re.fullmatch(r"META-INF/[^/]+\.(?:SF|RSA|DSA|EC)", item.filename, flags=re.I):
                    raise PackagingError("原 JAR 包包含签名元数据；为安全起见停止修改")
                data = patched.encode("utf-8") if item.filename == "META-INF/plugin.xml" else src.read(item)
                dst.writestr(item, data)
    with zipfile.ZipFile(destination_jar) as check:
        if check.testzip():
            raise PackagingError("生成的 JAR 校验失败")
    return original_since


def _safe_files(source: Path) -> list[Path]:
    files = []
    for p in source.rglob("*"):
        if p.is_symlink():
            raise PackagingError(f"不支持语言包中的符号链接: {p}")
        if p.is_file():
            if p.name == "plugin-classpath.txt":
                continue
            files.append(p)
    return sorted(files)


def next_free_path(output: Path) -> Path:
    if not output.exists():
        return output
    n = 2
    while True:
        alt = output.with_name(f"{output.stem}-{n}{output.suffix}")
        if not alt.exists():
            return alt
        n += 1


def build_package(source: Path, build: str, output: Path) -> tuple[Path, str]:
    """Creates plugin ZIP in output parent. No writes inside IDEA or Rebased."""
    source = normalize_source(source)
    branch = target_branch(build)
    jar = find_descriptor_jar(source)
    original_xml = _read_descriptor(jar)
    _, original_since = patch_descriptor(original_xml, build)
    output = next_free_path(output.expanduser().resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rebased-zh-helper-") as td:
        work = Path(td) / SOURCE_FOLDER
        shutil.copytree(source, work, symlinks=False)
        original_in_copy = work / "lib" / jar.name
        patched_in_copy = work / "lib" / (jar.stem + ".patched.jar")
        _copy_and_patch_jar(original_in_copy, patched_in_copy, build)
        patched_in_copy.replace(original_in_copy)
        candidate = Path(td) / "candidate.zip"
        with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in _safe_files(work):
                z.write(p, arcname=str(Path(SOURCE_FOLDER) / p.relative_to(work)))
        with zipfile.ZipFile(candidate) as check:
            if check.testzip():
                raise PackagingError("生成的 ZIP 校验失败")
            embedded = f"{SOURCE_FOLDER}/lib/{jar.name}"
            if embedded not in check.namelist():
                raise PackagingError(f"ZIP 缺少 {embedded}")
            with check.open(embedded) as f:
                with zipfile.ZipFile(f) as inner:
                    patched_xml = inner.read("META-INF/plugin.xml").decode("utf-8")
                    if f'since-build="{branch}"' not in patched_xml:
                        raise PackagingError("最终包的 since-build 校验失败")
        shutil.copyfile(candidate, output)
    return output, original_since
