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
- 从已验证案例中使用可迁移的设计规则，不复制案例参数与脚本
- 通过能力依赖图把规则组合成项目决策链，而不是一次加载全部规则
- 为每个阶段生成有预算限制的规则上下文，减少模型上下文压力
- 对授权导入的案例执行确定性结构与配置校验

## 仓库结构

```text
ensp-network-config/
├── SKILL.md
├── agents/
├── references/
│   ├── design-rules.md
│   ├── design-rules/
│   ├── rule-flow.md
│   ├── rule-capabilities.json
│   ├── rule-index.json
│   └── project-workflow.md
└── scripts/
    ├── project_workflow.py
    └── rule_flow.py
```

## 安装

把`ensp-network-config`目录复制到Codex Skills目录，例如：

```text
%USERPROFILE%\.codex\skills\ensp-network-config
```

安装脚本依赖：

```powershell
python -m pip install -r requirements.txt
```

重新启动或刷新Codex后，通过`$ensp-network-config`调用。

## 设计规则

`references/design-rules.md`是规则目录路由表，`references/rule-index.json`是可查询的规则元数据索引。Skill先根据需求和拓扑查询索引，再只读取当前阶段需要的规则正文，不会一次加载全部规则。已有规则只作为可迁移的设计约束；设备、端口、VLAN、地址、VRID、优先级和成本必须根据当前拓扑重新计算。

当前规则覆盖园区二层、网关与冗余、IPv4/DHCP、静态与动态路由、WAN/IPsec、访问安全与防火墙、PoE与堆叠、WLAN、QoS、SNMP等领域。BGP、IS-IS、组播和MPLS已有候选规则，但在独立验证前只能作为建议，不能进入正式配置链；EVPN/VXLAN和Segment Routing继续保留为空目录。

规则状态分为`validated`、`candidate`和`deprecated`。项目中另行记录规则是否应用以及验证是否通过，避免把“写进规则”“用于项目”和“运行成功”混为一谈。

## 规则流与上下文控制

大型或多协议项目使用`planning/rule-plan-vN.yaml`保存规则实例、能力依赖、需求覆盖和验证引用。常用命令：

```powershell
python ensp-network-config/scripts/rule_flow.py index --check
python ensp-network-config/scripts/rule_flow.py query --tags vlan mstp vrrp
python ensp-network-config/scripts/rule_flow.py validate projects/hotel/planning/rule-plan-v1.yaml
python ensp-network-config/scripts/rule_flow.py context projects/hotel/planning/rule-plan-v1.yaml `
  --stage 01-access `
  --output projects/hotel/planning/context/01-access.md
```

默认每个阶段最多加载12条规则正文、4个规则目录和3条候选建议。超过预算时，应按网络层次或独立业务/故障域拆分阶段。

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

初始化会创建`planning/rule-plan-v0.yaml`、规则选择日志和阶段上下文目录。确认基线前会校验规则计划，并生成与基线一致的`rule-plan-v1.yaml`。简单拓扑使用`--mode simple`，仍然使用同一接口，但只有一个配置阶段。

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

校验经过用户授权导入的案例：

```powershell
python ensp-network-config/scripts/validate_case.py cases/case-01
```

案例必须依次经过`imported -> normalized -> statically_validated -> runtime_validated -> approved`。只有`approved`案例可作为可信证据。

## 安全边界

- 不自动执行设备重置或配置清除
- 不生成命令级回退脚本
- 不静默修改已经确认的网络设计
- 不把静态检查等同于运行成功
- 不经用户明确授权导入案例或更新能力矩阵

详细规则见[规则流](ensp-network-config/references/rule-flow.md)和[项目工作流](ensp-network-config/references/project-workflow.md)。
