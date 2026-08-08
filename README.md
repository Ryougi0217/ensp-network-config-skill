# eNSP Network Config Skill

一个面向华为eNSP实验与项目实施的Codex Skill。它从拓扑截图、需求和已有配置中建立确认过的网络规划，并按照工程依赖顺序生成阶段TXT脚本、验证门禁和最终完整配置。

## 主要能力

- 识别设备、链路、端口、地址、VLAN和路由区域
- 对不确定端口和扩展模块请求用户确认
- 区分简单模式与大型拓扑阶段模式
- 按接入层、汇聚层、核心层、路由分支、出口和安全策略实施
- 每阶段生成一个包含多台设备的版本化TXT
- 在交付前进行结构和配置一致性检查
- 支持用户口头放行或运行截图/输出验证
- 记录失败、强制放行、返工和项目风险
- 按需将阶段脚本拼接为全网最终配置
- 在配置完成后由用户决定是否保存为案例

## 仓库结构

```text
ensp-network-config/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

## 安装

把`ensp-network-config`目录复制到Codex Skills目录，例如：

```text
%USERPROFILE%\.codex\skills\ensp-network-config
```

重新启动或刷新Codex后，通过`$ensp-network-config`调用。

## 项目工作流

大型拓扑默认采用：

```text
规划基线
→ 接入层
→ 汇聚层
→ 核心层与骨干路由
→ 独立路由区域或业务分支
→ 网络服务与出口
→ 安全策略
→ 全网验收
```

每个阶段只设置一次门禁。阶段内部可以包含多台设备，但配置与验证必须保持在当前故障域内。

## 创建项目

```powershell
python ensp-network-config/scripts/project_workflow.py init projects/hotel `
  --name "酒店网络" `
  --mode staged

python ensp-network-config/scripts/project_workflow.py confirm-baseline projects/hotel --by user
python ensp-network-config/scripts/project_workflow.py status projects/hotel
```

简单拓扑使用`--mode simple`，仍然保留项目状态，但只有一个配置阶段。

## 阶段TXT格式

```text
===== STAGE: 01-access | 接入层 =====
===== CONFIG DEVICE: LSW1 =====
system-view
...
return

===== VERIFY DEVICE: LSW1 =====
display vlan
display interface brief
```

阶段文件规则：

- 每阶段一个TXT文件
- 一个文件中按执行顺序包含所有相关设备
- 使用完整VRP命令
- 不包含`save`
- 验证命令位于文件末尾
- 修改后创建新版本，不覆盖已经交付的版本

## 工具

检查阶段TXT：

```powershell
python ensp-network-config/scripts/validate_stage_script.py scripts/01-接入层-v1.txt
```

判断明确的用户放行：

```powershell
python ensp-network-config/scripts/evaluate_gate.py attestation "本阶段验证通过"
```

根据结构化断言判断运行证据：

```powershell
python ensp-network-config/scripts/evaluate_gate.py evidence validation/evidence.json
```

拼接最终配置：

```powershell
python ensp-network-config/scripts/assemble_stage_scripts.py `
  --project projects/hotel
```

## 安全边界

- 不自动执行设备重置或配置清除
- 不生成命令级回退脚本
- 不静默修改已经确认的网络设计
- 不把静态检查等同于运行成功
- 不经用户明确授权导入案例或更新能力矩阵

详细规则见[项目工作流](ensp-network-config/references/project-workflow.md)。
