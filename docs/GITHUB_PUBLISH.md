# 发布到自己的 GitHub（公开仓库）

这里的公开仓库只存放原创源码、文档和测试，不发布 JetBrains 的原始或修改后翻译资源。

## 方法 A：GitHub 网页 + 本机 Git（不需要安装 gh）

1. 登录 GitHub，访问 <https://github.com/new>。
2. Repository name 输入 `rebased-zh-helper`，设置为 **Public**。
3. 创建时不要勾选自动添加 README、.gitignore、LICENSE（本项目已有）。
4. 把下载的本项目 ZIP 解压，终端进入其目录：

```bash
cd ~/Downloads/rebased-zh-helper
git init
git branch -M main
git add .
git commit -m "Initial release: Rebased Chinese helper"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/rebased-zh-helper.git
git push -u origin main
```

5. 把 `YOUR_GITHUB_USERNAME` 换成你自己的 GitHub 用户名。推送时按 GitHub 的 SSH/PAT 或凭据管理器要求认证，**不要把密码、token 提交到仓库**。
6. 打开公开仓库检查文件：确保没有任何 `localization-zh.jar`、`Rebased-Chinese-*.zip` 或 JetBrains 翻译资源。

## 方法 B：GitHub CLI（已安装并登录时）

```bash
cd ~/Downloads/rebased-zh-helper
git init
git branch -M main
git add .
git commit -m "Initial release: Rebased Chinese helper"
gh auth login
gh repo create rebased-zh-helper --public --source=. --remote=origin --push
```

> 不要用包含第三方语言包 ZIP 的 `GitHub Releases` 来提供下载；可在 Releases 中发布本仓库**源码**及版本说明。

## 后续向 Rebased 作者反馈

优先在已存在的 [Issue #106](https://github.com/DetachHead/rebased/issues/106) 跟帖，说明版本、系统架构和本项目地址。文本模板见 [upstream-comment.md](upstream-comment.md)。

## 发布后维护

- `git add .` 前运行 `git status`，确保只包含源码与测试。
- 使用 `git tag v0.1.0` 标记开源工具版本（不包括原版插件）。
- 在 GitHub 仓库 Settings → General 中可以开启 Discussions，也可以用 Issues 收集适配报告。
