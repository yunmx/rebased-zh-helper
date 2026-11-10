# 给 Rebased 上游的建议（优先在 #106 跟帖）

相关： https://github.com/DetachHead/rebased/issues/106
       https://github.com/DetachHead/rebased/issues/384

## Proposed comment

**Simplified Chinese localization on Rebased 1.1.24 (macOS, Apple Silicon)**

I have confirmed that the Simplified Chinese language pack from IntelliJ IDEA (version 263.7307.200) can be installed in Rebased 1.1.24 (Build IC-263.7307.SNAPSHOT) using **Install Plugin from Disk**, after a local compatibility metadata adjustment. The plugin is enabled, Chinese UI is visible after restart, and Git Log/Settings appear localized.

Could Rebased consider improving language-pack discovery and documenting a supported, properly licensed localization workflow? There is an existing discussion in #384. JetBrains' distribution/license restrictions should be reviewed before bundling any language resources.

I have prepared an **open-source local compatibility helper** (no JetBrains binaries, translations, or redistributed plugin archives). Repo: https://github.com/zhaozhxcn/rebased-zh-helper

Thanks for considering this!

---

注意：无需声称上游已支持中文，也不要附带已经修改过的受版权保护的语言包。
