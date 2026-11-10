# 故障排查

## 1. 插件市场只能找到繁体中文

Rebased 与 IntelliJ IDEA 同样使用 JetBrains Marketplace 生态，但显示和可安装的插件会受内置插件集、产品类型和构建版本影响。IDEA 2024.2+ 通常已内置简体中文，Rebased 不一定内置。优先参考 JetBrains 与 Rebased 官方说明。

## 2. Cannot update plugin / 无法更新插件

对于本地磁盘 ZIP 安装的插件，Marketplace 无法识别其更新来源是正常现象，不代表当前插件不可用。无需为了消除提示而添加不明第三方更新源。

## 3. 版本不匹配

用 Rebased `Help → About` 的 `Build` 对比 IDEA 插件的 `since-build`：

- Rebased `IC-263.7307.SNAPSHOT` 与插件 `263.7307.200`：同一构建分支，**可能**适用。
- Rebased `IC-262.11879.SNAPSHOT` 与插件 `263.7307.200`：不同分支，脚本会拒绝，不要强装。

即使分支相同也不保证二进制兼容。

## 4. Corrupted Installation / Missing essential plugin: com.intellij

通常与修改 Rebased 应用目录中的核心索引文件有关，不是普通本地 ZIP 打包步骤。本仓库**不会修改** `Rebased.app` 或 `plugin-classpath.txt`，也**不提供**删除这些文件的指令。

如果曾运行其他脚本而导致程序无法启动，优先恢复之前的备份；无法确定备份内容时，使用官方 Rebased 安装包恢复应用本体，保留用户数据并先备份相关配置。

## 5. 已安装语言包仍不显示中文

先确认：插件 Enabled、插件版本与 Rebased 构建匹配、语言设置已选择 Chinese (Simplified)，再重启。Rebased 自定义 UI 可能仍然是英文。

## 6. IDEA 未被自动检测到

运行：

```bash
python3 build.py --list-sources
python3 build.py --source "/Applications/IntelliJ IDEA.app/Contents/plugins/localization-zh" --target-build IC-263.7307.SNAPSHOT --acknowledge-rights
```

如果使用 JetBrains Toolbox，找到 `IntelliJ IDEA.app` 后将其拖到终端查看路径，或者通过 Finder 的“显示包内容”定位 `Contents/plugins/localization-zh`。

## 7. 许可证问题

不要公开提供已修改的 JetBrains 中文语言包、安装 ZIP 或其翻译文件，除非你已取得明确授权。仓库源码开源不自动赋予你重新分发第三方语言资源的权利。
