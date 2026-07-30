# AI 产品经理作品集

一个可持续扩展的 AI 产品经理作品集，首个案例是可直接使用的 **OctoAvatar GitHub 头像转换器**。

## 目录结构

```text
/
├── index.html               # 作品集主页
├── styles.css               # 作品集主页样式
└── projects/
    └── octoavatar/
        ├── index.html       # 头像转换器独立页面
        ├── styles.css       # 头像转换器样式
        └── app.js           # 头像转换逻辑
```

## 当前内容

- AI 产品经理定位、工作方式与联系入口
- OctoAvatar 产品案例说明
- 图片上传、拖拽裁剪、缩放、旋转与圆形预览
- 自动导出 PNG，并尽量压缩至 1 MB 以下
- HEIC / HEIF 在线解码支持
- 响应式布局、键盘焦点与减少动态效果支持

## 本地运行

```powershell
python -m http.server 8080
```

访问 `http://localhost:8080`。

## 作品集信息

- 姓名：朱邦国
- 联系邮箱：`231300057@smail.nju.edu.cn`
- 后续可继续补充个人经历和下一批项目。

## 添加新作品

1. 在 `projects/` 下新建独立项目文件夹，例如 `projects/ai-research-assistant/`。
2. 将该项目的 HTML、CSS、JavaScript 和资源都放在自己的文件夹中。
3. 在作品集主页 `index.html` 中增加项目介绍，并通过链接或 `iframe` 指向该目录。
