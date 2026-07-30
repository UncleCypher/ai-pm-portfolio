# AI 产品经理作品集

一个可持续扩展的单页作品集，首个案例是可直接使用的 **OctoAvatar GitHub 头像转换器**。

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

复制 `index.html` 中的 `.featured-project` 或 `.next-project` 结构，新建项目标题、背景、决策、验证结果与体验入口即可。视觉变量集中在 `styles.css` 顶部的 `:root` 中。
