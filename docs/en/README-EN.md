# AIDOC Station (Lite) Open Source Project

<p align="center">
  <img src="../../docs/images/AIDoc/logo_banner.png" alt="AIDOC Station Logo" width="600">
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
  <b><a href="../../README.md" style="color: #375dfb;">[ZH] 简体中文</a> | <a href="README-EN.md" style="color: #375dfb;">[EN] English</a></b>
</p>

## 🌟 Introduction

**AIDOC Station (Lite)** is the open-source offline desktop core component of the **AIDOC Unified AI Office Suite** ecosystem, specifically designed to bridge the format gap between AI-generated content and office software (Word/Excel/WPS). Powered by the local Pandoc engine, it provides ultra-fast and precise conversion of Markdown/HTML to Office formats. All processing is handled locally, ensuring both efficiency and privacy security.

---
## 🌐 AIDOC Unified AI Office Suite Ecosystem
The AIDOC ecosystem is built on the integrated concept of "Unified Cloud Identity + Local High-Efficiency Processing + Intelligent Plugin Creation," consisting of three core components:

### 1. AiDoc Copilot
An AI creation assistant embedded in Microsoft Word, supporting intelligent image matching, format beautification, and cross-terminal content synchronization. It leverages the computing power of AIDOC Station via local RPC calls to insert AI-generated content as native Office objects, achieving a seamless "Creation-Typesetting-Landing" workflow.

### 2. AiDoc Station
The desktop core hub of the ecosystem (**Lite version is the open-source offline version; no pre-built releases are provided, compilation is required**). It is responsible for advanced local document format conversion, system clipboard monitoring, singleton management, style mapping, and template customization. It acts as the "Local Power Bridge" connecting Web identity and plugin creation, providing rapid Markdown/HTML to Office format conversion entirely offline.

### 3. AiDoc Web
The unified identity portal, official website, and user management center. It provides cross-terminal Single Sign-On (SSO), user asset management, and cloud synchronization of custom templates. It serves as the "Identity Source" and configuration center for the entire ecosystem. Visit AiDoc Web at <a href="https://www.pcfox.cn" style="color: #375dfb; text-decoration: none;">www.pcfox.cn</a>.

## 🚀 Core Features

- **Smart Style Mapping**: Supports deep style binding from Markdown/HTML to Word/WPS to ensure layout consistency.
- **Cross-App Compatibility**: Mutual style recognition between Word and WPS, solving common issues like lost table borders and inconsistent spacing.
- **Professional Formula Support**: Built-in LaTeX to MathType/editable Office formula conversion, avoiding blurred images of formulas.
- **Structured Table Processing**: Automatically handles complex nested tables and merged cells, supporting custom table borders and alignment.
- **Style Mapping Configuration**: Customizable style mapping for paragraphs, tables, and images, enabling "Configure once, reuse forever."
- **Reference Template Configuration**: Supports custom and built-in templates for one-click copying of headers/footers and synchronization of styles for easy reuse.

## 🚨 Key User Pain Points & Solutions
### 🔍 Have you encountered these problems?
When pasting AI-generated or online-edited Markdown/HTML content into Office, almost all users face the following pain points:
1. **Compromised Formatting**: Lost heading levels, lists turned into plain text, shifted image positions, and invalid line breaks requiring manual line-by-line adjustment.
2. **Time-consuming Style Adjustments**: Inconsistent Markdown formats across platforms (ChatGPT/Claude/Yuque/Notion) mean resetting fonts, spacing, and colors every time.
3. **Poor Formula/Chart Compatibility**: LaTeX formulas turning into garbled code and Mermaid diagrams only showing text, unable to generate native Office formulas or chart objects.
4. **Collapsed Table Layouts**: Imbalanced column widths and lost alignment after pasting Markdown tables, sometimes requiring a complete redraw.
5. **Difficult Template Reuse**: Custom Word templates cannot link with Markdown conversion, requiring a tedious application process after each conversion.

### ✅ How does AIDOC Station (Lite) solve this?
Deeply customized based on the Pandoc engine, we combine "Style Mapping + Template Customization + Local Computing" to solve typesetting pain points at the root:

#### 1. 🚀 One-Click Precise Conversion, Zero Format Mess
Triggered by a customizable hotkey (e.g., Ctrl+Shift+Q), it automatically reads Markdown/HTML content from the clipboard and instantly translates it into native Office formats. Heading levels, list structures, image positions, and line-break logic are 1:1 fully restored. It also supports pre-binding Markdown syntax to Word custom styles for immediate application of preset templates.
> 📸 One-click Word format conversion:<br><img src="../../docs/images/one-click-conversion.gif" width="600" alt="Comparison">
> *Note: Left side is Markdown content generated by AI including Mermaid and tables; right side is the structured format inserted into Word by AIDOC Station.*

#### 2. 🎨 Smart Style Mapping, One-Click Rule Reuse
Built-in "Style Mapping Configuration" for paragraphs, lists, tables, and images. It supports matching Markdown content directly to Word/WPS built-in styles (including Body, Body Text, Body Indent, Caption, etc.). It automatically recognizes ordered/unordered lists and precisely converts them, allowing zero-cost reuse of typesetting rules.
> 📸 Style Mapping Configuration:<br><img src="../../docs/images/style-mapping.gif" width="600" alt="Configuration UI">
> *Note: Style mapping configuration panel for binding Markdown syntax to corresponding Word styles.*

#### 3. 🔬 Native Rendering for Complex Mathematical Formulas
Deeply adapted for LaTeX/KaTeX formulas, automatically translating them into native Office formula objects. After conversion, formulas can be directly edited, scaled, and fine-tuned, doubling the efficiency of academic and technical document typesetting.
> 📸 Mathematical Formula Rendering:<br><img src="../../docs/images/formula-conversion.gif" width="600" alt="Formula Conversion Effect">
> *Note: LaTeX formulas converted into Word native formula objects, supporting editing, scaling, and format adjustments.*

#### 4. 📋 One-Click Reuse of Reference Documents
Supports specified custom templates to copy headers/footers and full style attributes in one click. Quickly reuse branded typesetting standards without manual replication. Together with editable AIDoc standard reference templates, it significantly reduces repetitive work.
> 📸 Reference Document Reuse:<br><img src="../../docs/images/reference-document.gif" width="600" alt="Reference Document Effect">
> *Note: One-click reference document reuse, supporting headers/footers and full style attribute replication.*

## ✨ Key Features Summary
| Feature               | Details                                                                         |
| --------------------- | ------------------------------------------------------------------------------- |
| 🚀 Direct Conversion   | Custom hotkeys to read clipboard, converting Markdown/HTML to Office in seconds |
| 🎨 Style Mapping       | Bind Markdown syntax to Word styles, supporting built-in/custom templates       |
| 🔬 Formula Parsing     | LaTeX/KaTeX to native Office formulas, MathML mapping for all versions          |
| 📊 Smart Tables        | Preserves alignment, column width; supports one-click Excel/WPS pasting         |
| 📝 Custom Templates    | Export/import style templates for team-wide style consistency                   |
| 🔒 Local Privacy       | 100% local processing, no data upload, compatible with offline use              |
| ⚙️ Highly Configurable | Customizable hotkeys, conversion rules, and Pandoc parameters                   |

## 🎯 Technical Decision Notes
### 1. **Underlying Differences in Word and WPS Automation Rendering**
- Users noticed that when using Word, the template file "flashes" (opens and closes quickly) during insertion, while in WPS, the process is completely silent.
- This transition is due to architectural differences: Word uses Single Document Interface (SDI), requiring each document to initialize an independent window handle, making physical silence difficult. WPS uses Multiple Document Interface (MDI), allowing data stream processing directly in memory.
- Future solutions to achieve a seamless experience:
  - Resource pre-warming pool to hold template references in the background to eliminate loading delay.
  - Ultimate transition to OpenXML binary operation technology, bypassing the COM automation layer for zero-redraw, high-performance synchronization.

### 2. **Word Intelligent Typesetting and Reference Document Usage**
AIDOC Station introduces an innovative reference document management mechanism to balance professional typesetting with a smooth user experience:

1. **Three-State Style Control (Toggle via icon in Settings)**:
   - **[Disabled]**: Original Content. Inserts content without changing existing document styles.
   - **[Built-in]**: Official Paradigm. Automatically applies professional system preset Word templates.
   - **[Custom]**: Brand Customization. Allows uploading personal/corporate .docx templates for branded inheritance.
2. **Core Technology: Smart Fingerprint Sync**:
   The system uses an "On-demand Initialization" algorithm. Continuous operations in the same document record a "Style Fingerprint." If recognized, subsequent additions skip redundant style injections, increasing response speed by over 50% and eliminating screen flickering.
3. **Compatibility Guarantee**:
   Whether using .doc or .docx, AIDOC precisely controls cursor positioning (cursor follows to the end after insertion) and fixes common Chinese font deviations for pixel-perfect alignment.

### 3. Excel Smart Fill Trigger and Format Requirements
To ensure AI-generated data fills Excel accurately, follow these guidelines:

1. **Trigger Mechanism**:
   - **Hotkey**: Press Ctrl+Alt+Q (Windows) or Cmd+Alt+Q (macOS) in an active Excel window.
   - **Context Awareness**: Automatically detects the foreground window. If it detects "excel.exe" or a title containing "Excel", it executes the filling logic.
   - **Switch State**: Ensure "Enable Excel Smart Fill" is ON in settings.
2. **Required Format (Core)**:
   Strict Markdown table parsing is used. Content must follow:
   - **Separators**: Use vertical bars `|` between columns.
   - **Alignment Row**: Include a header separator row (e.g., `|---|---|`).

### 4. Technical Decisions on Full-Bundled Installer & Zero-Configuration Deployment
To achieve a "seamless, out-of-the-box" user experience and eliminate the complexity of cross-platform deployment, AIDOC Station adopts a **Full-Bundled & Zero-Configuration** technical architecture. Below are the key decisions:

**1. Full-Bundled Core Dependencies**
- **Pandoc Engine**: As the core engine for cross-platform document conversion, Pandoc is fully bundled within the installer. Users don't need to install it separately; simply download the installer and it's ready to use.
- **Python Runtime**: Integrated with a lightweight Python runtime environment to ensure steady operation on Windows systems without pre-installed Python.
- **Full Resource Encapsulation (Eliminating User-Environment Dependency)**: Mandatory bundling in the package includes:
    - **Portable Node.js Runtime**: No dependency on system-installed Node.exe.
    - **Full Filter Plugins (Lua/Node_modules)**: No need for users to run `npm install`.

**2. Zero-Configuration Deployment Strategy**
- **Automatic Environment Detection**: The program automatically detects system environment settings upon startup, intelligently configuring paths and dependencies without manual user input.
- **One-Click Installation**: Provides a standard Windows installation wizard with support for custom paths, automatically registering as a system service upon completion.

**3. Cross-Platform Compatibility**
- **Windows Priority**: The current version focuses on the Windows platform, providing best-in-class system integration (e.g., context menus, global hotkeys).
- **Future Roadmap**: Linux and macOS versions are planned, following the same full-bundled and zero-configuration principles to ensure a consistent, seamless experience for all users.

## 🚀 Quick Start
### 1. Prerequisites
- **OS**: Windows 10 / 11 (x64)
- **Core Dependency**: The installation package includes the Pandoc engine (v3.8.3); no additional installation is needed.

### 2. Download and Installation
1. Go to the <a href="https://github.com/AIDriveLab/AIDOCStation/releases" style="color: #375dfb; text-decoration: none;">Releases</a> page and download the latest `AiDoc_Station_Setup_v*.exe`.
2. Run the installer and follow the instructions (supports custom installation paths).
3. After installation, the AIDOC Station tray icon will appear.

### 3. Basic Operations
1. **Copy Content**: Copy Markdown/HTML text from ChatGPT/Claude/Yuque/Notion, etc.
2. **Position Cursor**: Open Word/WPS/Excel and place the cursor at the target position.
3. **One-Click Convert**: Press the default hotkey `Ctrl + Shift + B` to convert and paste content.

## 📚 Technical Guides
Detailed documentation for developers and advanced users:
- ⚙️ **<a href="01-general-settings.md" style="color: #375dfb; text-decoration: none;">General Settings Guide</a>**: Configure appearance, environment paths, behavior, and services.
- 📝 **<a href="02-formatting-rules.md" style="color: #375dfb; text-decoration: none;">Format Processing Engine</a>**: Deep dive into Markdown/HTML to Office conversion rules and Excel adaptation.
- 🎨 **<a href="03-style-mapping.md" style="color: #375dfb; text-decoration: none;">Style Mapping Standards</a>**: Configure Word styles for paragraphs, tables, and images.
- ➗ **<a href="04-troubleshooting.md" style="color: #375dfb; text-decoration: none;">Formula Conversion Standards</a>**: LaTeX fixes, MathML mapping, and formula styling.

## 🤝 Contribution & Feedback
- **Contribution**: We welcome Pull Requests! Please see **<a href="../../CONTRIBUTING.md" style="color: #375dfb; text-decoration: none;">CONTRIBUTING.md</a>** for details.
- **Bug Reports**: Submit an <a href="https://github.com/AIDriveLab/AIDOCStation/issues" style="color: #375dfb; text-decoration: none;">Issue</a>.
- **Security & Privacy**: For vulnerability reporting and privacy, see **<a href="../../SECURITY.md" style="color: #375dfb; text-decoration: none;">SECURITY.md</a>**.

## 📄 License
Licensed under the <a href="../../LICENSE" style="color: #375dfb; text-decoration: none;">LICENSE</a>. See the file for details.

---

<p align="center">
  Built by <b><a href="https://www.pcfox.cn" style="color: #375dfb; text-decoration: none;">AIDriveLab</a></b> · Bringing AI Content Seamlessly to Office Scenarios
</p>

<p align="center">
  <img src="../../docs/images/AIDoc/aidrivelogo.png" alt="AIDriveLab Logo" height="60">
  <img src="../../docs/images/year_horse_2026_logo.png" alt="Year of Horse 2026" height="60" style="margin-left: 10px;">
  <img src="../../docs/images/year_horse_2026_logo_text.png" alt="Year of Horse 2026" height="40" style="margin-left: 5px;">
</p>

<p align="center">
  <img src="../../docs/images/AIDoc/AIDriveQR.jpg" alt="AIDriveLab QR" width="150" style="margin-right: 20px;">
  <img src="../../docs/images/AIDoc/AIDriveVQR.jpg" alt="AIDriveLab Video QR" width="140">
</p>
