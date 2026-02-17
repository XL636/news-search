# Super Team Agent 模板库

## 📦 内容说明

这是一个可复用的 AI Agent 团队配置模板，包含10个基于世界顶级专家思维模型设计的角色。

### 📁 文件结构

```
super-team/
├── agents/              # 10个Agent角色配置文件
│   ├── ceo-bezos.md           # CEO (Jeff Bezos思维模型)
│   ├── cto-vogels.md          # CTO (Werner Vogels思维模型)
│   ├── fullstack-dhh.md       # 全栈开发 (DHH思维模型)
│   ├── interaction-cooper.md  # 交互设计 (Alan Cooper)
│   ├── marketing-godin.md     # 营销专家 (Seth Godin)
│   ├── operations-pg.md       # 运营专家 (Paul Graham)
│   ├── product-norman.md      # 产品设计 (Don Norman)
│   ├── qa-bach.md            # QA测试 (James Bach)
│   ├── sales-ross.md         # 销售专家 (Aaron Ross)
│   └── ui-duarte.md          # UI设计 (Matías Duarte)
├── skills/             # 技能配置（如有）
├── settings.json       # Claude Code 设置
├── CLAUDE.md          # 详细使用说明和理念
└── README.md          # 本文件

```

## 🎯 核心理念

**一个人 + 世界顶级思维模型 = 一支超级团队**

每个 Agent 都基于该领域公认最顶尖专家的思维模型和决策框架。

## 🚀 如何在新项目中使用

### 方法1：复制整个 .claude 文件夹（推荐）

```bash
# 在新项目根目录下
cp -r "D:\claude\agent-templates\super-team" "./.claude"
```

### 方法2：只复制特定角色

```bash
# 创建 .claude/agents 目录
mkdir -p .claude/agents

# 只复制需要的角色
cp "D:\claude\agent-templates\super-team\agents\ceo-bezos.md" "./.claude/agents/"
cp "D:\claude\agent-templates\super-team\agents\fullstack-dhh.md" "./.claude/agents/"
```

### 方法3：创建软链接（高级）

```bash
# 在新项目中创建指向模板的软链接
ln -s "D:\claude\agent-templates\super-team\agents" "./.claude/agents"
```

## 📋 10个角色概览

| 角色 | 专家模型 | 核心能力 | 何时使用 |
|------|---------|---------|---------|
| **CEO** | Jeff Bezos | 战略决策、商业模式、PR/FAQ | 评估新产品、重大决策 |
| **CTO** | Werner Vogels | 技术架构、工程标准 | 技术选型、架构设计 |
| **产品设计** | Don Norman | 用户体验、可供性设计 | 产品定义、需求分析 |
| **UI设计** | Matías Duarte | 视觉系统、Material Design | 界面设计、设计系统 |
| **交互设计** | Alan Cooper | 用户流程、Persona | 交互设计、用户研究 |
| **全栈开发** | DHH | Rails哲学、单体架构 | 代码实现、技术方案 |
| **QA测试** | James Bach | 探索性测试、质量把控 | 测试策略、质量保证 |
| **营销** | Seth Godin | 紫牛理论、许可营销 | 品牌定位、获客策略 |
| **运营** | Paul Graham | YC理念、增长策略 | 用户运营、社区建设 |
| **销售** | Aaron Ross | 可预测收入、销售漏斗 | 销售策略、定价模型 |

## 🔄 标准工作流

项目已预定义4个标准协作流程：

1. **新产品/功能评估**
   ```
   ceo-bezos → product-norman → interaction-cooper
   → cto-vogels → fullstack-dhh → marketing-godin
   ```

2. **功能开发**
   ```
   interaction-cooper → ui-duarte → fullstack-dhh
   → qa-bach → operations-pg
   ```

3. **产品发布**
   ```
   qa-bach → marketing-godin → sales-ross
   → operations-pg → ceo-bezos
   ```

4. **每周复盘**
   ```
   operations-pg → sales-ross → qa-bach → ceo-bezos
   ```

## 💡 使用建议

### ✅ 推荐做法

1. **按需使用**：不需要每次都调用所有10个角色
2. **保留原项目**：不要删除 ctxport 原项目，保留完整参考
3. **自定义修改**：可以根据自己的需求修改角色配置
4. **创建文档目录**：在项目中创建 `docs/<role>/` 存放各角色的产出

### ❌ 避免做法

1. 不要过度依赖流程，保持灵活性
2. 不要让 Agent 替代你的判断，你才是最终决策者
3. 不要一次性调用所有角色，会导致信息过载

## 📚 详细说明

查看 `CLAUDE.md` 了解：
- 完整的决策原则和工作原则
- 详细的协作流程
- 文档管理规范
- 沟通规范

## 🔗 原始来源

本模板来自 [nicepkg/ctxport](https://github.com/nicepkg/ctxport) 项目。

## 📝 自定义指南

如果要创建自己的 Agent：

1. 在 `agents/` 目录创建 `.md` 文件
2. 使用 YAML frontmatter 定义基本信息：
   ```yaml
   ---
   name: my-agent
   description: "角色描述和使用场景"
   model: inherit
   ---
   ```
3. 在正文中定义：
   - Role（角色定位）
   - Persona（人设）
   - Core Principles（核心原则）
   - Decision Framework（决策框架）
   - Communication Style（沟通风格）

## 🎨 使用示例

在 Claude Code 中使用这些角色：

```
用户：我想开发一个新的SaaS产品，帮我分析一下可行性

Claude：让我调用CEO角色来帮您分析...
（调用 ceo-bezos agent）

CEO (Bezos思维模型)：
1. 首先，我们需要明确客户问题...
2. 让我们用PR/FAQ方法来思考...
3. 这个想法是否有飞轮效应？...
```

## 🤝 贡献

如果您创建了新的有价值的 Agent 角色，欢迎分享！

---

**核心价值**：让独立开发者拥有世界级团队的思维能力 🚀
