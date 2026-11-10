# Rebased 简体中文支持工具 / Rebased Chinese Helper

[English README](README.en.md) · [发布到 GitHub](docs/GITHUB_PUBLISH.md) · [安装排错](docs/TROUBLESHOOTING.md) · [Rebased 官网](https://github.com/DetachHead/rebased)

> **非官方社区工具。** 这是用于检查与本地打包的开源 **Python 工具**，不是 JetBrains 语言包本身。仓库 **不包含** JetBrains 的中文翻译文件、JAR、完整安装包或任何 Rebased 应用二进制文件。

## 它能做什么

- 为 **Rebased 1.1.24 / `IC-263.7307.SNAPSHOT`** 检查匹配的 IntelliJ IDEA 简体中文插件版本。
- 从用户自行提供的 IDEA `localization-zh` 目录读取资源，在**临时目录**生成用于 `Install Plugin from Disk…` 的 ZIP（仅适用于你拥有修改、使用该资源的授权或法律许可的情况）。
- 防止不匹配的 `263.7307` / `262.11879` 混装。
- 不修改 `/Applications/Rebased.app`、IDEA.app、`plugin-classpath.txt` 或 Git 仓库。
- 不上传语言资源到网络；无需第三方 Python 依赖。

**已知验证：** 社区用户在 macOS Apple Silicon + Rebased 1.1.24 + 官方语言包 263.7307.200 组合上曾成功从磁盘安装并显示中文。本仓库的脚本通过的是合成测试；尚未在该用户的 Mac 上重新运行这一版本的工具，不承诺适用所有版本。

## ⚖️ 首先阅读：许可证与第三方版权

此仓库中的原创代码及说明采用 MIT 许可证，**不包括**任何 JetBrains 语言包/翻译资源。根据 [JetBrains Free Plugin License Agreement](https://www.jetbrains.com/legal/docs/terms/jetbrains-free-plugin-license/)（需核实你实际使用的组件所适用的条款），修改和再分发可能受到限制。

本工具**不意味着**对原插件修改、重新打包、传播取得了授权。**只有你确认拥有适用许可或法律依据时**，才运行打包操作。不要把生成的包含原翻译文件的 ZIP 发布到 GitHub Releases、网盘或应用市场，除非有权利人明确许可。希望直接发布完整语言包的用户，应先向 JetBrains 取得许可，或使用完全自主、许可明确的翻译资源。

## 快速开始（macOS）

前置：Python 3.10+、Rebased 和有权使用的 IDEA 中文语言包。查看 Rebased **Help → About** 的 Build Number。

```bash
# 1. 下载本仓库到 Mac（GitHub 网页 Code -> Download ZIP 也可以）
#    在仓库目录运行：
python3 build.py --list-sources

# 2. 了解许可，并确认你有修改该资源的权利后构建
python3 build.py --target-build IC-263.7307.SNAPSHOT --acknowledge-rights
```

如果存在多个 IDEA 或找不到语言包，明确指定自己的 IDEA 安装路径：

```bash
python3 build.py \
  --source "/Applications/IntelliJ IDEA.app/Contents/plugins/localization-zh" \
  --target-build IC-263.7307.SNAPSHOT \
  --acknowledge-rights
```

默认结果输出至：`~/Downloads/Rebased-Chinese-263.7307.zip`。如果同名文件已存在，会追加 `-2` 等后缀，不覆盖已有文件。

> **不要将输出 ZIP 提交到仓库。** 该文件含有 JetBrains 资源，LICENSE（MIT）不适用于其内容。

### 通过磁盘安装到 Rebased

1. 打开 Rebased，进入 `Settings → Plugins`。
2. 点击插件页面上方的齿轮 `⚙` → **Install Plugin from Disk...**。
3. 选择刚刚在 `~/Downloads` 生成的 ZIP。
4. 重启 Rebased。
5. 打开 `Settings → Appearance & Behavior → System Settings → Language and Region`，选择 **Chinese (Simplified)**，按提示重启。

本仓库**不提供** `plugin-classpath.txt` 清理、复制覆盖应用内置插件等危险步骤。

## 适配哪些版本？

| 组件 | 版本 | 状态 |
| --- | --- | --- |
| Rebased | 1.1.24，`IC-263.7307.SNAPSHOT` | 已有社区成功案例 |
| IntelliJ 简体中文语言包 | `263.7307.200` | 与上面主构建系列匹配 |
| Rebased 1.1.23 | `IC-262.11879.SNAPSHOT` | **不能**直接复用 263.7307 中文包 |
| 其他版本 | 未经验证 | 需使用同 `major.minor` 构建分支的中文资源并独立测试 |

工具仅检查、调整插件元数据中的 `since-build` / `until-build`（前提是用户具有此操作的合法权限），不会确保实际的二进制/API 兼容。

## 开发与测试

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 build.py --help
```

自动测试使用自行生成的**合成示例插件**，不会下载、嵌入 JetBrains 翻译资源。欢迎提交 PR，增加版本检测、平台支持、交互体验与许可明确的自主翻译。

## 与上游的关系

这是独立社区项目，与 JetBrains、Rebased 作者无官方关联；Rebased 为各权利人各自持有的商标。

Rebased 上游已有相关 Issue：[#106 语言切换功能](https://github.com/DetachHead/rebased/issues/106)、[#384 中文包构建兼容](https://github.com/DetachHead/rebased/issues/384)。建议**优先在 #106 跟帖**而非重复新开 Issue；示例见 [上游建议文本](docs/upstream-comment.md)。

## 维护原则

- 不修改 Rebased.app/IDEA.app 内文件或系统安全设置。
- 不收集、上传本地文件；仅从本机读取并在本机输出。
- 代码审查和自动测试必须使用合成资源。
- Github 仓库及 Releases 不提供第三方受限制资源。

## License

**MIT for the original repository code/documentation only.** See [LICENSE](LICENSE). JetBrains language packs and translation assets are **not included and not covered**.
