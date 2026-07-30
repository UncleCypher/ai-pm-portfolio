# OctoAvatar · GitHub 头像转换器

[![在线体验](https://img.shields.io/badge/在线体验-OctoAvatar-4F6DF5?style=for-the-badge)](https://unclecypher.github.io/ai-pm-portfolio/projects/octoavatar/)

OctoAvatar 是一个完全在浏览器本地运行的 GitHub 头像转换工具。它将图片格式、尺寸和文件大小等技术规则收敛为“选择图片、调整、下载”三个用户动作。

## 产品背景

用户上传 GitHub 头像时，可能遇到格式不支持、文件过大、画面比例不合适等问题。对一次性任务来说，要求用户先理解图片格式和压缩参数，会产生不必要的学习成本。

产品选择不引入账号系统或云端上传，通过浏览器原生图像处理能力完成转换，以缩短任务路径并保护图片隐私。

## 主要功能

- 拖放或选择本地图片
- 自动识别常见图片格式
- 拖动调整头像位置
- 滑块或滚轮缩放
- 向左、向右旋转与一键重置
- 正方形和 GitHub 圆形效果预览
- 选择 500、800、1000 或 2000 像素输出尺寸
- 导出 PNG，并自动尝试压缩至 1 MB 以下
- 支持 HEIC / HEIF 转换

## 隐私设计

图片不会上传到服务器。读取、裁剪、缩放、旋转、压缩和导出均在用户浏览器中完成。

HEIC / HEIF 解码组件通过 CDN 加载，但用户选择的图片本身不会发送到该 CDN。

## 支持格式

常见浏览器可直接读取：

- JPG / JPEG
- PNG
- WebP
- GIF
- BMP
- SVG
- AVIF
- JFIF

HEIC / HEIF 使用 `heic2any` 在浏览器端解码。实际格式支持情况可能受到浏览器版本影响。

## 本地运行

在作品集仓库根目录运行：

```powershell
python -m http.server 8080
```

然后访问：

```text
http://localhost:8080/projects/octoavatar/
```

不要直接双击打开 HTML 文件，否则部分浏览器的安全策略可能限制外部组件加载。

## 文件说明

```text
octoavatar/
├── README.md   # 项目介绍
├── index.html  # 项目页面与交互结构
├── styles.css  # 项目独立样式
└── app.js      # 图片处理与导出逻辑
```

## 技术实现

- 原生 HTML、CSS 和 JavaScript
- Canvas 负责预览、裁剪、旋转和输出
- `createImageBitmap` 优先解码浏览器支持的图片
- `heic2any` 处理 HEIC / HEIF
- Canvas PNG 导出与逐级缩小实现文件大小控制

## 当前边界

- PNG 是无损格式，复杂图片在保持较高分辨率时可能超过 1 MB，因此工具会逐步降低输出尺寸。
- 圆形选项用于预览 GitHub 的最终显示效果，下载文件仍保持标准正方形 PNG，避免永久裁掉圆形外区域。
