# AIDOC Station (Lite)开源项目

<p align="center">
  <img src="docs/images/AIDoc/logo_banner.png" alt="AIDOC Station Logo" width="600">
</p>

<p align="center">
<img src="https://img.shields.io/badge/Platform-Windows-blue.svg" alt="Platform: Windows">
<img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
<img src="https://img.shields.io/badge/Version-0.2.0--lite-orange.svg" alt="Version: 0.2.0-lite">
<img src="https://img.shields.io/badge/Status-Public--Release-brightgreen.svg" alt="Status: Public Release">
<img src="https://img.shields.io/badge/Core%20Engine-Pandoc%20v3.8.3-purple.svg" alt="PoweredBy: Pandoc v3.8.3">
<img src="https://img.shields.io/badge/Technology-Python%203.10+-blueviolet.svg" alt="Technology: Python 3.10+">
</p>

<p align="center">
  <b><a href="README.md" style="color: #375dfb;">[ZH] 简体中文</a> | <a href="docs/en/README-EN.md" style="color: #375dfb;">[EN] English</a></b>
</p>

## 🌟 项目简介

**AIDOC Station (Lite)** 是 **AIDOC Unified AI Office Suite** 生态的开源离线版桌面核心组件，专为解决 AI 生成内容与办公软件（Word/Excel/WPS）的格式断层问题而生。它以本地 Pandoc 引擎为核心，提供极速、精准的 Markdown/HTML 到 Office 格式转换能力，所有处理过程均在本地完成，兼顾效率与隐私安全。

---
## 🌐 AIDOC Unified AI Office Suite 生态
AIDOC 生态围绕「云端统一身份 + 本地高效处理 + 插件智能创作」的一体化理念构建，包含三大核心组件：

### 1. AiDoc Copilot
嵌入 Microsoft Word 的 AI 创作助手，支持智能配图、格式美化、跨端内容同步，通过本地 RPC 调用 AIDOC Station 的算力，将 AI 生成内容以原生 Office 对象形式插入文档，实现“创作-排版-落地”一站式完成。

### 2. AiDoc Station
生态的桌面核心中枢（**Lite 版为开源离线版本，不提供Releases版本，需要自行编译**），负责本地文档高级格式转换、系统剪贴板监控、单例运行管理、样式映射与模板定制，是连接 Web 端身份与插件端创作的“本地算力桥”，提供 Markdown/HTML 到 Office 格式的极速转换能力，所有处理全程本地化。

### 3. AiDoc Web
生态的统一身份门户、产品官网及用户管理中心，提供跨端单点登录（SSO）、用户资产管理、自定义模板云端同步等能力，是整个生态的“身份源”与配置中心。AiDoc Web 请访问 <a href="https://www.pcfox.cn" style="color: #375dfb; text-decoration: none;">www.pcfox.cn</a>。

## 🚀 核心特性

- **智能样式映射**：支持从 Markdown/HTML 到 Word/WPS 的深度样式绑定，确保排版一致性。
- **跨应用兼容性**：支持 Word 与 WPS 之间的样式互认，解决表格边框丢失、间距异常等排版顽疾。
- **专业公式支持**：内置 LaTeX 到 MathType/可编辑 Office 公式的转换链路，告别公式图片化带来的模糊问题。
- **结构化表格处理**：自动处理复杂表格嵌套、合并单元格，并支持自定义表格边框与对齐模式。
- **支持样式映射配置**：支持段落正文、表格和图片的自定义样式映射配置，实现“一次配置，永久复用”。
- **支持参考模板配置**：支持自定义模板、内置模板一键复制页眉/页脚，同步模板中的样式，实现模板便捷复用。

## 🚨 核心用户痛点 & 解决方案
### 🔍 你是否遇到这些问题？
在将 AI 生成/在线编辑的 Markdown/HTML 内容粘贴到 Office 时，几乎所有用户都会面临以下痛点：
1. **格式彻底错乱**：标题层级丢失、列表变成纯文本、图片位置偏移、换行符失效，粘贴后需手动逐行调整；
2. **样式调整耗时**：不同平台（ChatGPT/Claude/语雀/Notion）的 Markdown 格式不统一，每次粘贴都要重新设置字体、行距、颜色，重复劳动效率极低；
3. **公式/图表兼容差**：LaTeX 数学公式粘贴后变成乱码，Mermaid 流程图仅显示文本，无法生成 Office 原生公式/图表对象；
4. **表格排版崩溃**：Markdown 表格粘贴后列宽失衡、对齐方式丢失，复杂表格甚至需要重新绘制；
5. **模板复用困难**：自定义的 Word 样式模板无法与 Markdown 转换联动，每次转换后仍需套用模板，流程繁琐。

### ✅ AIDOC Station (Lite) 如何解决？
我们基于 Pandoc 引擎深度定制，结合「样式映射 + 模板定制 + 本地算力」三大核心能力，从根源解决排版痛点：

#### 1. 🚀 一键精准转换，格式零错乱
自定义快捷键 Ctrl+Shift+Q（支持自由配置）一键触发，自动读取剪贴板中的 Markdown/HTML 内容，瞬间转译为 Office 原生格式 —— 标题层级、列表结构、图片位置、换行逻辑 1:1 完整还原，彻底告别粘贴后格式错乱的困扰。更支持将 Markdown 语法（如 # 标题1/## 标题2）与 Word 自定义样式提前绑定，转换后直接套用预设模板，无需手动调整，排版一步到位。
> 📸 一键转换 Word 格式：<br><video src="docs/images/one-click-conversion.mp4" muted autoplay loop playsinline width="600"></video>
> *说明：左侧为豆包AI生成的Markdown内容包含Mermaid语法、表格等，右侧为 AIDOC Station 转换后的插入Word文档的规整格式*

#### 2. 🎨 智能样式映射，排版规则一键复用
内置段落、列表、表格、图片等全场景「样式映射配置」，支持将 Markdown 内容直接匹配 Word/WPS 内置样式（含正文、正文文本、正文缩进、题注等高频场景）；自动识别 Markdown 有序 / 无序列表并精准转换为对应段落样式，无需手动调整格式，让排版规则零成本复用，办公效率直线提升。
> 📸 样式映射配置：<br><video src="docs/images/style-mapping.mp4" muted autoplay loop playsinline width="600"></video>
> *说明：样式映射配置面板，可绑定 Markdown 语法转后对应的 Word 样式*

#### 3. 🔬 支持复杂数学公式原生渲染
深度适配 LaTeX/KaTeX 数学公式，自动转译为 Office 原生公式对象，彻底告别粘贴后公式变代码的糟心场景；转换后支持直接编辑、自由缩放、格式微调，像操作本地公式一样灵活省心，学术 / 技术文档排版效率翻倍。
> 📸 数学公式渲染效果：<br><video src="docs/images/formula-conversion.mp4" muted autoplay loop playsinline width="600"></video>
> *说明：LaTeX 公式转换为 Word 原生公式对象，支持编辑、缩放、格式调整*

#### 4. 📋 参考文档一键复用，品牌排版高效落地
支持指定自定义模板，一键复制模板的页眉 / 页脚、全套样式属性，快速复用品牌化排版规范，无需手动复刻格式；搭配可自由编辑的 AIDoc 标准参考模板，既能直接套用现成规范，也能按需调整细节，大幅减少重复排版工作，效率直接拉满。
> 📸 参考文档一键复用：<br><video src="docs/images/reference-document.mp4" muted autoplay loop playsinline width="600"></video>
> *说明：参考文档一键复用，支持复制模板的页眉/页脚、全套样式属性*



## ✨ 核心特性
| 特性           | 详情                                                       |
| -------------- | ---------------------------------------------------------- |
| 🚀 一键直达转换 | 自定义快捷键读取剪贴板内容，Markdown/HTML 秒转 Office 格式 |
| 🎨 样式映射体系 | 绑定 Markdown 语法与 Word 样式，支持内置/自定义模板        |
| 🔬 公式完美解析 | LaTeX/KaTeX 转 Office 原生公式，MathML 映射兼容所有版本    |
| 📊 智能表格处理 | 保留表格对齐、列宽，支持 Excel/WPS 表格一键粘贴            |
| 📝 模板自由定制 | 导出/导入样式模板，支持团队样式统一复用                    |
| 🔒 本地隐私优先 | 全程本地处理，无数据上传，兼容离线使用                     |
| ⚙️ 高度可配置   | 自定义快捷键、转换规则、Pandoc 引擎参数                    |

## 🎯 技术决策说明
### 1. **关于Word与WPS的自动化渲染中的底层差异**
- 用户反馈在 Microsoft Word 中使用自定义或内置模板插入时，能明显观察到模板文件“闪现”（打开并迅速关闭）的过程；而在使用 WPS 时，整个同步过程完全静默。
- 这源于两者架构差异：Word 采用单文档界面 (SDI)，每个文档需初始化独立窗口句柄，导致 Visible=False 难以实现物理级静默；而 WPS 是多文档界面 (MDI)，可直接在内存中处理数据流。
- 为实现无感体验，未来技术方案将：
  - 建立资源预热池，在后台预持有模板引用以消除加载延迟；
  - 终极转向 OpenXML 二进制操作技术，完全绕过 COM 自动化层进行离线样式合并，实现零重绘、高性能的品牌同步。

### 2. **Word 智能排版与参考文档使用说明**
为了平衡文档的“专业排版”与操作的“丝滑无感”，AiDoc Station 引入了创新的参考文档管理机制。以下是核心功能说明：

**1. 三态样式控制（点击设置页图标切换）**
【禁用模式】：原汁原字。仅插入内容，不改动文档现有样式，适合日常随笔追加。
【内置模式】：官方范式。自动应用系统预设的专业 Word 模板，确保页眉、字体与行距符合官方标准。
【自定义模式】：品牌定制。允许您上传企业或个人的 .docx 模板，内容插入后将完美继承您的专属品牌属性。
**2. 核心黑科技：智能指纹同步**
系统采用了**“按需初始化”算法**。当您在同一个文档连续操作时，AiDoc 会自动记录“样式指纹”。如果识别到文档已完成过品牌初始化，后续追加内容将自动跳过冗余的样式注入，响应速度提升 50% 以上，并彻底消除页面闪烁现象。

**3. 完美兼容保障**
无论您使用的是后缀为 .doc 的旧版文档还是最新的 .docx，AiDoc 都能精准控制光标位置（插入后光标自动跟随至末尾），并修复了中文排版中常见的字体偏差，确保排版像素级一致。

### 3. Excel 智能填充触发机制与格式要求
为了确保 AI 生成的数据能精准填充到您的 Excel 表格中，请遵循以下触发流程与格式规范：

**1. 触发机制**
快捷键启动：在 Excel 活动窗口中，按下全局热键 Ctrl+Alt+Q (Windows) 或 Cmd+Alt+Q (macOS)。
上下文感知：系统会自动检测当前前台窗口。只有当检测到进程为 excel.exe 或标题包含 “Excel” 特征时，才会引导执行表格填充逻辑。
开关状态：请确保设置中的“启用 Excel 智能填充”开关处于开启状态。
**2. 必须包含的格式（核心）**
系统采用严格的 Markdown 表格解析算法，待填充的内容必须符合以下标准格式：
- 分隔符：每列数据必须使用竖线 | 进行分隔。
- 对齐行：表头下方必须包含由中划线 and 竖线组成的对齐行（例如 |---|---|）。

### 4. 安装包全量内置与零配置部署技术决策
为了实现“开箱即用”的极致用户体验，并彻底消除跨平台部署的复杂性，AiDoc Station 采用了**全量内置与零配置部署**的技术架构。以下是核心决策说明：

**1. **核心依赖全量内置****
- **Pandoc 引擎**：作为跨平台文档转换的核心引擎，Pandoc 已被完整打包进安装程序。用户无需在本地单独安装，下载安装包即可直接使用。
- **Python 运行时**：集成了轻量级 Python 运行时环境，确保程序在无 Python 的 Windows 系统上也能稳定运行。
- **放弃依赖用户环境，执行全量资源包围**：在发布包中强制内置：
    - **Portable Node.js 运行时**：不依赖用户系统是否安装 Node.exe。
    - **全量过滤器插件 (Lua/Node_modules)**：无需用户执行 `npm install`。

**2. **零配置部署策略****
- **自动环境检测**：程序启动时自动检测系统环境，智能配置路径与依赖，无需用户手动配置任何路径。
- **一键式安装**：提供标准 Windows 安装向导，支持自定义安装路径，安装完成后自动注册为系统服务。

**3. **跨平台兼容性****
- **Windows 优先发布**：当前版本专注于 Windows 平台，提供最佳的系统集成体验（如右键菜单、全局热键）。
- **未来规划**：未来将推出 Linux 和 macOS 版本，同样遵循全量内置与零配置原则，确保各平台用户都能获得一致的无感体验。

## 🚀 快速开始
### 1. 环境准备
- **操作系统**：Windows 10 / 11 (x64)
- **核心依赖**：安装包已内置 Pandoc 引擎 (v3.8.3)，无需额外安装

### 2. 下载与安装
1. 前往 <a href="https://github.com/AIDriveLab/AIDOCStation/releases" style="color: #375dfb; text-decoration: none;">Releases</a> 页面下载最新版 `AiDoc_Station_Setup_v*.exe`；
2. 运行安装程序，按照指引完成安装（支持自定义安装路径）；
3. 安装完成后，桌面右下角将出现 AIDOC Station 托盘图标。

### 3. 基础操作
1. **复制内容**：在 ChatGPT/Claude/语雀/Notion 等平台复制 Markdown/HTML 文本；
2. **定位光标**：打开 Word/WPS/Excel，将光标定位到目标位置；
3. **一键转换**：按下默认快捷键 `Ctrl + Shift + B`，内容自动转换并粘贴到文档中。

## 📚 技术指南
为开发者与高级用户提供深度功能说明：
- ⚙️ **<a href="docs/zh/general-settings.md" style="color: #375dfb; text-decoration: none;">常规设置指南</a>**：可配置外观、环境路径、交互行为、AIDOC 服务及启动通知，优化 AiDocStation 使用体验。
- 📝 **<a href="docs/zh/format-processing.md" style="color: #375dfb; text-decoration: none;">格式处理引擎</a>**：针对 Markdown/HTML 转 Office 的细节优化，含转换规则、文档清洗、后处理及 Excel 适配等精准配置。
- 🎨 **<a href="docs/zh/style-mapping.md" style="color: #375dfb; text-decoration: none;">样式映射标准</a>**：可配置段落、表格、图片的 Word 样式及处理策略，统一文档排版，提升输出美观度与专业性。
- ➗ **<a href="docs/zh/formula-conversion.md" style="color: #375dfb; text-decoration: none;">公式转换规范</a>**：LaTeX 修复方案、MathML 映射逻辑、公式样式定制

## 🤝 贡献与反馈
- **参与贡献**：欢迎提交 Pull Request！详细流程请参阅 **<a href="CONTRIBUTING.md" style="color: #375dfb; text-decoration: none;">CONTRIBUTING.md</a>**。
- **问题反馈**：请提交 <a href="https://github.com/AIDriveLab/AIDOCStation/issues" style="color: #375dfb; text-decoration: none;">Issue</a> 或在 Discussions 板块交流。
- **安全与隐私**：有关漏洞报告和隐私声明，请参阅 **<a href="SECURITY.md" style="color: #375dfb; text-decoration: none;">SECURITY.md</a>**。

## 📄 开源协议
本项目基于 MIT 协议开源，详见 <a href="LICENSE" style="color: #375dfb; text-decoration: none;">LICENSE</a> 文件。


---

<p align="center">
  由 <b><a href="https://www.pcfox.cn" style="color: #375dfb; text-decoration: none;">AIDriveLab / AI驱动创新</a></b> 打造 · 让 AI 内容无缝落地办公场景
</p>

<p align="center">
  <img src="docs/images/AIDoc/aidrivelogo.png" alt="AIDriveLab Logo" height="60">
  <img src="docs/images/year_horse_2026_logo.png" alt="Year of Horse 2026" height="60" style="margin-left: 10px;">
  <img src="docs/images/year_horse_2026_logo_text.png" alt="Year of Horse 2026" height="40" style="margin-left: 5px;">
</p>

<p align="center">
  <img src="docs/images/AIDoc/AIDriveQR.jpg" alt="AIDriveLab QR" width="150" style="margin-right: 20px;">
  <img src="docs/images/AIDoc/AIDriveVQR.jpg" alt="AIDriveLab Video QR" width="140">
</p>
