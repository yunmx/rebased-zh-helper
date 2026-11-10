"""Command line entry point for Rebased Chinese helper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from .packager import (
    PackagingError, build_package, find_installed_sources,
    normalize_source, target_branch,
)

DEFAULT_BUILD = "IC-263.7307.SNAPSHOT"


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rebased-zh-helper",
        description="Rebased 中文语言包兼容性检查与本地打包（不修改 Rebased.app）",
    )
    p.add_argument("--list-sources", action="store_true", help="列出常见 macOS 路径中找到的 IDEA 语言包")
    p.add_argument("--source", type=Path, help="IDEA.app 或 IDEA.app/Contents/plugins/localization-zh")
    p.add_argument("--target-build", default=DEFAULT_BUILD, help=f"Rebased 的 Build 编号，默认 {DEFAULT_BUILD}")
    p.add_argument("--output", type=Path, help="生成 ZIP 的路径（默认为 ~/Downloads）")
    p.add_argument(
        "--acknowledge-rights", action="store_true",
        help="确认你对所使用的语言包有适用的修改/使用授权或法律许可",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        if args.list_sources:
            paths = find_installed_sources()
            if paths:
                for path in paths:
                    print(path)
            else:
                print("未自动找到语言包，请使用 --source 指定路径")
            return 0
        branch = target_branch(args.target_build)
        if not args.acknowledge_rights:
            raise PackagingError(
                "请先阅读 README 中的许可说明。JetBrains 许可可能限制修改原语言包。\n"
                "只有在你拥有适用授权或法律许可时，才添加 --acknowledge-rights 执行。"
            )
        if args.source:
            source = normalize_source(args.source)
        else:
            sources = find_installed_sources()
            if len(sources) != 1:
                raise PackagingError(
                    "需要唯一的 IDEA 语言包来源；使用 --list-sources 查看，然后用 --source 指定。"
                )
            source = sources[0]
        output = args.output or (Path.home() / "Downloads" / f"Rebased-Chinese-{branch}.zip")
        package, original_since = build_package(source, args.target_build, output)
        print("✅ 本地打包成功 / Local packaging complete")
        print(f"来源 / source: {source}")
        print(f"原 since-build: {original_since}")
        print(f"目标 since-build: {branch}")
        print(f"目标 until-build: {branch.split('.')[0]}.*")
        print(f"输出 / output: {package}")
        print("安装：Rebased → Settings → Plugins → ⚙ → Install Plugin from Disk…")
        print("重启后：Settings → Appearance & Behavior → System Settings → Language and Region")
        print("提醒：此 ZIP 含有第三方资源，未获授权请勿上传 GitHub 或分发。")
        return 0
    except (PackagingError, OSError, ValueError, RuntimeError) as e:
        print("❌ 已安全停止：", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
