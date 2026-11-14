# 小入口，可复现的结果

2026-11-14 的首版选择：输入场馆与舞台假设，输出三个可比较的观演视角。研究和判断由代理完成；几何和相机由脚本稳定生成。

## 路线取舍

| 路线 | 优点 | 首次使用的成本 | 选择 |
| --- | --- | --- | --- |
| 每次让 AI 从零写 Blender 脚本 | 自由度高，仓库小 | 安装 Blender、调试生成代码；结果不稳定 | 不作为默认路径 |
| 参数化预览 + 可选 Blender | 示例离线可运行；数据可追溯；两端共享网格 | 不能自动复刻特殊屋顶和每一个票务分区 | v0.1 |
| 完整产品场馆与舞美系统 | 场景丰富 | 模型许可、服务依赖和维护成本高 | 后续按模块评估 |

## 公开 Skill 的规模

以下为 2026-11-14 读取 GitHub 默认分支的原始文件所得快照，含 frontmatter。是有目的的样本，不是完整排名；行数不等于 token、实现成本或质量。

| 公开 Skill | 入口行数 | 额外内容 |
| --- | ---: | --- |
| [web-design-guidelines](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | 39 | 运行时读取远程指南 |
| [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 71 | 许可文件；9,390 字节的入口 |
| [find-skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) | 141 | 调用现成 CLI |
| [remotion-best-practices](https://github.com/remotion-dev/skills/tree/main/skills/remotion-best-practices) | 116 | Skill 子树共 148 个文件 |
| [react-best-practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) | 149 | 72 个 rules Markdown 文件 |
| [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) | 314 | 8 个脚本和两份能力参考 |

[Agent Skills 规范](https://agentskills.io/specification)定义了最小入口和按需加载结构。Seat View 使用同样的结构，不把 README、宣传素材或第三方完整手册塞进模型的必读上下文。

## 精度如何表达

每份输入都有来源、假设和字段证据。`verified` 只用于来源直接支撑的字段；从照片推算用 `estimated`，缺资料用 `unknown`。脚本验证数据结构、数值范围和几何约束，无法验证网页是否真的支持某个事实——这是 Skill 的研究职责。

v0.1 的椭圆看台适合解释位置、距离和方向关系，不承诺建筑复刻。相机使用同一个目标与 50° 垂直视场角，不通过改变焦段让某个位置显得更好。模型排号不是票面排号。

## 维护边界

不抓取受限票务数据，不把实时舞美识别、手机长焦、遮挡分析、排行榜或完整账号系统加入首版。真正值得扩展的能力是有来源的场馆轮廓、有依据的分区映射，以及在更多客户端上完成真实安装验证。
