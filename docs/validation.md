# 验证记录

记录日期：2026-11-14。以下描述实测范围，不代表所有客户端、设备或场馆都已验证。

| 项目 | 方法与结果 |
| --- | --- |
| Python | macOS / Python 3.9.6；标准库运行；13 项单元测试通过 |
| 生成器 | 三种舞台布局、相机落在排位上方、人物 1.75 m、舞台位于内场范围、有限数值与规模边界、确定性输出 |
| 数据与文件 | 非法输入拒绝；已有产物保留；名称不能终止 HTML 内嵌 JSON 脚本；完整许可随包和 HTML 分发 |
| 浏览器 | Playwright 驱动本机 Chrome；1440×1000 与 390×844；虚构样例和研究样例均完成全景、三机位、资料弹窗与 PNG 下载 |
| 离线 | 浏览器测试主动拦截全部 HTTP(S) 请求；生成页面实际发起 0 个请求，控制台无页面异常 |
| Blender | 5.1.2 实际导出 `.blend` 和 GLB；示例 17 网格 / 12,600 三角面；三相机统一 50° 垂直 FOV；检查过落座渲染 |
| 独立使用 | 将整个 Skill 复制到独立目录，仅依据 Skill 文档执行一次真实场馆研究和生成；不依赖坐哪儿产品仓库 |
| 开放格式 | `SKILL.md` 含 `name` / `description` / `license` / 顶层 `compatibility`；资源使用相对路径；未声明专属工具依赖 |

## 真实请求试用

输入：“上海体育场，假想端台，对比侧面低层、正面低层和正面高层；不足的资料明确写估算。”

可复现输入在 [examples/shanghai-estimated.json](examples/shanghai-estimated.json)。官方和专业来源确认了真实场馆的非对称特征，却没有验证本输入的半轴、排距和层高。因此这份示例的相机相关尺寸全部标为估算，不应作为上海体育场的精确选座依据。

研究流程发现了两处文档歧义：证据字段不接受 `name` 或 `bowl.tiers`。现已在参数说明中写明支持的路径。实测对称椭圆与真实场馆西高东低结构存在差异，说明“已做研究”不等于“已经标定”。

## 尚未验证

- CodeArts、Claude Code、Cursor 等客户端的完整自动触发、工具授权和市场安装流程。
- 真机移动浏览器、Safari、Firefox、Windows 和 Linux 的视觉表现。
- 真实票面区排座映射、演出遮挡、建筑精确重建与音响表现。
- 所有 Blender 版本；4.x 的引擎兼容分支存在，但本次只运行了 5.1.2。

浏览器的手机宽度测试不能替代手机真机测试。可选浏览器检查脚本是开发工具，需要单独安装 Playwright；普通使用不需要它。

## 重跑

```bash
python3 -m unittest discover -s tests -v
python3 skills/seat-view/scripts/build.py --demo --output ./preview-check
```

已另行安装 Playwright 与 Chrome 的开发环境可运行：

```bash
node tests/browser_check.mjs ./preview-check/index.html ./preview-check/screenshots
```

检查截图与导出图片，不能只看脚本返回 PASS。
