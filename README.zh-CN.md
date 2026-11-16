# Android 虚拟屏幕实测指南

[Tiếng Việt](README.md) · [English](README.en.md) · **简体中文** · [한국어](README.ko.md) · [日本語](README.ja.md)

本指南记录了在真实 Android 设备上，通过独立虚拟显示屏控制应用、同时保持物理屏幕关闭的实验。
这是**文档与复现指南**，不是完整 Android agent，也不分发 APK，不承诺所有应用或锁屏状态均可用。

**观察日期：2026-11-16。** 下文版本是实测版本，并不代表最新版本。
公开内容是作者报告并脱敏后的实验摘要。私人截图和原始日志未公开，因此不构成可独立审计的原始证据。
请按文档自行复现，并明确区分源码解释、后端诊断、应用调用和完整 AI 任务。

## 核心结论

- **Root 既非必要条件，也非充分条件。** 已 root 的 Samsung A32 在 Virtual Screen 的 Root 后端遇到 package/UID 错误；改用 ADB 启动、以 shell UID `2000` 运行的 Shizuku 后，限定测试通过。
- **非 root 设备也有可行路径。** Xiaomi Pad Mini 的 Mika 解锁状态自检为 12/12；安全锁屏状态另有原生后端诊断成功。
- **熄屏不等于安全锁屏。** A32 的 `keyguard showing=false`，不能据此推断 PIN/图案锁下也能工作。
- **后端成功不等于完整 agent 成功。** Pad Mini 锁屏实验没有调用正在服务的 helper RPC，也没有运行 Mika 应用或 AI 端到端任务。未配置模型或 API key。
- **恢复能力必须单独验证。** Wireless ADB 曾消失；用户重新启用后 helper 不在运行，必须手动重启。自动恢复和重启设备后的恢复均未验证。

## 已验证的范围

| 设备与路径 | 观察结果 | 证据边界 |
|---|---|---|
| Samsung A32，Android 13 / One UI 5.1，已 root；Virtual Screen 0.2.1 Root 后端 | `ROOT_OPERATION_FAILED`；`SecurityException: packageName must match the calling uid` | 仅代表本次 ROM/后端组合，不代表所有 root 实现 |
| 同一 A32；ADB 启动 Shizuku 13.6.0；Virtual Screen MCP | 列出 19 个工具；Settings 启动、节点读取、点击和输入通过；物理显示为 `DOZE_SUSPEND` | `keyguard showing=false`；未重新逐个测试全部 19 个工具 |
| 同一 A32；应用首次自检 | 18/19，Tap 失败 | 后续限定点击与输入成功不覆盖首次失败 |
| Xiaomi Pad Mini，Android 16，非 root；Mika 0.1.44，build `2b26f3f` | 自检 12 pass、0 partial、0 fail、0 skipped，41 秒 | 在设备已解锁时执行 |
| 同一 Pad Mini；安全锁屏且熄屏 | 已安装 APK 的 `ShellService` 在独立临时 shell 进程中创建显示、读取节点、点击计数和输入回读成功 | `Asleep`、物理 `OFF`、`showing=true`；不是服务中 helper 的 RPC 或应用/AI E2E |
| 同一 Pad Mini；安全锁屏；TikTok Studio 44.6.3 | 实际应用启动并捕获 1880×3008 图像；物理屏幕保持关闭 | 仅启动与截图，未发布内容或操作账号 |

完整历史见 [实验结果与边界](docs/observed-results.md)。[脱敏摘要](examples/observations.json)不是原始 trace。

## 如何选择方案

| 条件 | 建议起点 | 需要保留的限制 |
|---|---|---|
| 已 root，现有 `su` 正常 | 使用应用支持的 Root 后端，并只授予对应应用权限 | Root 不保证绕过 package attribution、显示策略或 ROM 差异 |
| Root 后端失败，但授权 ADB 可用 | 用 **ADB 启动 Shizuku**，再授权目标应用 | 核实服务为 UID `2000`；root 启动是不同身份 |
| 非 root，设备满足 Mika 要求 | 安装 Mika，通过选定设备的 ADB 运行官方 helper 启动流程 | Mac 的 ADB 配对不等于 Mika 自身已配对 |
| 无 root，也无 ADB/helper | 考虑常规应用 API 或经用户同意的 MediaProjection | 不会自动获得跨应用输入权或独立后台应用显示屏 |
| 涉及受保护内容 | 按具体应用正常的认证与截图规则测试 | 普通截图成功不能证明可捕获 `FLAG_SECURE` 或 DRM 内容 |

详细步骤见 [Root / 非 root 方案](docs/solutions.md)和[故障排查](docs/troubleshooting.md)。

## 三条控制路径不能混为一谈

1. **Virtual Screen + MCP**：应用授权、session、控制 lease、最新 observation、操作、回读及清理。
2. **Mika 正常应用流程**：自身 helper、Accessibility 服务、应用编排，以及可选的模型配置。
3. **独立原生诊断**：临时 shell 进程加载已安装 Mika APK 中的 `ShellService`，验证设备与后端能力。

第三条路径没有验证 Mika 的应用编排或正在服务的 helper RPC，也没有提供生产远程控制端点。
实验 harness 依赖具体版本，本仓库不将其作为通用 SDK 分发。
虚拟屏幕、物理屏幕与 keyguard 的状态必须分别记录。
设备级 `Awake` 可以与物理面板 `DOZE_SUSPEND` 同时出现，不能只看一个总状态。

## A32 的经验：身份比“有无 root”更具体

本实验开始前设备已 root；本指南不包含刷机、解锁 bootloader 或安装 root 的步骤。
`su` 可用，但 Root 后端创建显示时被 package/UID 校验拒绝，具体上游缺陷未被定位。
可行路径是官方 Shizuku 的 ADB 启动方式，核实 shell 身份后，在 Virtual Screen 中选择该后端。
无需为 Shizuku 追加 root 授权，也不应为其他应用扩大权限。
MCP 应保留认证并仅监听 loopback，通过选定设备的 ADB forward 连接。
工具参数以已安装服务器返回的 schema 为准，不要猜测；读取最新 observation 后再输入，并回读验证。

## Pad Mini 的经验：成功与生命周期分开报告

Mika 0.1.44 的 helper 可通过现有授权 ADB 通道运行官方 `usb-start.sh`。
脚本名称不意味着必须使用 USB，也不证明 Mika 已完成自己的无线配对或保存了可重连身份。
首次自检为 11 pass、1 partial，原因是通知关闭；开启通知后重新自检才达到 12/12。
Accessibility、通知、电池不受限、自启动和最近任务锁定等准备不能保证 helper 永久存活。
锁屏诊断未输入 PIN/图案，也未解除物理 keyguard；它仅验证独立显示的原生能力。
Wireless ADB 消失后，即使用户恢复连接，helper 仍需手动启动。不要将此描述为自动恢复。

## 权限、输入与清理规则

- 先核实实时设备型号与 serial；每条 ADB 命令都显式使用 `adb -s "$SERIAL"`。公开报告只保留占位符。
- 分清 ADB shell、应用 `su`、Shizuku 与 Accessibility 授权，保留其他服务和授权。
- 只通过应用支持的 UI/配置读取认证信息；不要写入历史、日志、截图或仓库。
- 不将带 bearer 认证的控制器暴露到公共 tunnel；loopback 转发只服务本次测试。
- 输入前核对 display、task、focus 和新 observation；不确定是否送达时先回读，避免重复点击。
- 不因应用已有其他显示屏上的 task 就强制停止或重启，避免丢失草稿；遵循工具确认流程。
- 若测试经同意移动 task，先记录原位置与 focus，完成后恢复并验证；不要把 ROM 专属命令当作通用方案。
- 结束时关闭本次显示、释放 lease/session、清理本次 forward，并复查物理屏幕与应用状态。

## 建议复现顺序

1. 核实设备、官方 APK 的来源、版本和 hash。
2. 建立后端身份，只授予目标应用必需权限。
3. 解锁状态先跑自检，修正失败前提后重跑受影响项目，保留最初失败。
4. 在 Settings 或无害测试页上测试启动、观察、一次限定输入与回读。
5. 由用户明确控制锁定状态，再分别记录熄屏与安全 keyguard 状态，重复限定测试。
6. 单独测试传输断开、helper 死亡、空闲与设备重启；未测项目标注未验证。
7. 发布脱敏的版本、身份、状态与结果，不发布账号、网络标识、原始截图或私有路径。

## 进一步阅读

以下详细文档为英文：

- [完整实验结果](docs/observed-results.md)与[方案说明](docs/solutions.md)
- [复现与清理](docs/reproduce.md)及[故障诊断](docs/troubleshooting.md)
- [公开资料的隐私处理](docs/privacy.md)及[固定版本与官方来源](docs/sources.md)
- [English README](README.en.md)

## 许可与上游归属

本指南及原创示例采用 [MIT 许可](LICENSE)。上游应用保留各自许可。
本仓库不分发上游 APK、源码树、凭据或私人截图，也不代表上游维护者。
安装和版本变更请查阅 [android-virtual-screen、Shizuku 与 Mika 官方来源](docs/sources.md)。
