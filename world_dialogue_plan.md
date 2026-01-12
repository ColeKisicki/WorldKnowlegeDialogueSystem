# World Dialogue System — Project Plan

## LONG-TERM VISION (Do NOT implement yet)

### Goal
Create a **world-aware dialogue system** where NPCs respond based on:
- objective world truth
- what they plausibly know
- how they learned it
- their perspective, role, and limitations

NPCs should be able to:
- answer questions
- be wrong or uncertain
- cite where information came from
- explain *how* they know something

---

### Long-Term Architecture (Conceptual)

#### 1. One World Knowledge System (Source of Truth)
- Stores **entities**, **facts**, and **events**
- Represents *what exists* and *what happened*
- Is authoritative and immutable
- Does NOT encode who knows what

Eventually modeled as a graph:
- entities as nodes
- events as nodes
- relationships as edges

---

#### 2. Knowledge as Exposure, Not Permission
NPC knowledge is **derived**, not stored directly.

In the future, an NPC knows something only if:
- a **knowledge transfer event** occurred
- OR a **plausible path of information flow** exists

Information flows via:
- hubs (inns, markets, temples)
- channels (gossip, travel, books, broadcasts)
- routines (who goes where)

---

#### 3. Plausibility & Audit Trails (Future)
When answering:
- system finds relevant world facts
- determines if NPC could plausibly know them
- returns an **audit trail**

This avoids omniscience and supports:
- misinformation
- uncertainty
- investigation gameplay

---

#### 4. LLM Conversations as World Events (Future)
In a simulated world:
- NPC-NPC LLM conversations generate **knowledge transfer events**
- Only structured deltas are recorded (not raw dialogue)
- Claims ≠ truth

---

#### 5. Vector Recall Layer (Future)
A semantic index (like Google search):
- maps user questions to candidate facts/claims
- does NOT verify truth
- references IDs in the world knowledge system

---

## CURRENT PLAN (PHASE 1 — WHAT TO BUILD NOW)

### Phase 1 Goal
Build a **simple, observable world dialogue system** where:
- You can talk to **one NPC**
- The NPC has **absolute knowledge of the world**
- All answers are **true**
- Each answer includes a **clear audit trail**
- World knowledge is **easy to inspect and visualize**

No plausibility.  
No diffusion.  
No secrecy.  
No multiple perspectives.

NPC = omniscient narrator for now.

---

### Phase 1 Responsibilities

#### 1. World Knowledge (Absolute Truth Only)
A simple structured store containing:
- entities (NPCs, locations, objects)
- facts (statements about entities)
- events (things that happened)

This is the only knowledge source the NPC uses.

---

#### 2. Dialogue NPC
- Backed by an LLM
- Always has full access to world knowledge
- Answers user questions using only stored facts
- Cites which facts it used (audit trail)

---

#### 3. Debuggability First
You must be able to:
- print all facts
- inspect facts related to an entity
- see which facts were used in a response

This phase is about **iteration speed**, not realism.

---

## CURRENT FILE STRUCTURE (PHASE 1)

```
world_dialogue/
│
├── main.py
├── config.py
│
├── world/
│   ├── models.py
│   ├── store.py
│   ├── seed_world.py
│   └── visualize.py
│
├── dialogue/
│   ├── npc.py
│   ├── prompt_builder.py
│   └── audit.py
│
└── utils/
    └── ids.py
```

---

## Phase 1 NPC Behavior Rules
- NPC always knows all world facts
- NPC never invents facts
- NPC must cite fact IDs used in every answer
- NPC answers only from provided world context
- If no relevant facts exist, NPC says “I don’t know”

---

## What Comes After Phase 1 (Later)
1. Add relationships/events as graph edges
2. Add visualization of world graph
3. Add multiple NPCs
4. Add per-NPC knowledge filtering
5. Add plausibility search + audit trails
6. Add misinformation and belief modeling

---

## IMPORTANT GUIDELINES
- Do not add premature abstraction
- Do not implement plausibility logic yet
- Prefer clarity and inspectability over cleverness

---

## One-Sentence Summary
**Phase 1 builds an omniscient NPC grounded in an explicit world truth store, with full auditability, so later knowledge-limiting systems can be added safely and incrementally.**
