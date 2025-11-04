# Task: Project State Regeneration & Workflow Reset

## 1. Objective & Context

We are performing a hard reset on our project documentation. Your performance has degraded due to critical context loss and protocol non-compliance.

Your **sole, serialized task** is to create a new, definitive `project_status.md`. This file will be our single source of truth for (A) **What is Done** (the *how* and *why* of its implementation) and (B) **What Needs to Be Done** (the *how* and *why* of its future design).

You will build this by synthesizing information from **all** available project sources. This prompt *replaces* our previous conversational flow.

**Mandatory Protocols:**

* You **MUST** follow the `thinking_protocol.prompt.md` for this entire task.
* You **MUST** use #sequentialthinking for planning and synthesis.
* You **MUST** use #actor-critic-thinking for self-verification.
* You **MUST** use file-reading tools for all file/directory analysis.

## 2. File Operations

1. You **WILL** first **delete** any existing file named `project_status.md` (or similar, like `project_status (1).md`, search for them, read them, only then remove. Use `tree -I ".git" -I ".github" -I "knowledge_base"` to inspect and keep track.) to ensure a clean state.
2. You **WILL** then **create** a new, single file named `project_status.md`.

## 3. Execution Workflow (Mandatory 4-Phase Process)

You **MUST** follow this 4-phase process in sequence. Do not proceed to the next phase until the previous one is complete.

### Phase 1: Analysis & Information Gathering

1. **Initial Plan:** Start with #sequentialthinking to create a high-level plan for how you will read and process all four context sources.
2. **Read Context Source 1 (Documentation):** Read the *entire* contents of the #file:documentation folder.
3. **Read Context Source 2 (Historical Draft):** Read the *entire* contents of the #file:first_draft.md file.
4. **Read Context Source 3 (Source Code):**
    * List the full file tree of the `src/` and `tests/` directories.
    * Read the contents of key implementation files (e.g., `main.py`, key modules in `src/`, `conftest.py`, and key tests in `tests/`) to understand the *actual* implemented code structure, patterns, and state.
5. **Analyze Context Source 4 (Conversation History):**
    * Analyze your available conversation history.
    * Extract key decisions, completed tasks, user-stated goals, and known issues that are *not* yet captured in the static documentation.
6. **Synthesize Plan:** After gathering from **all four sources**, use `#sequentialthinking` again. This plan MUST detail the *final, merged outline* for the `project_status.md` and explicitly state *how* you will resolve any conflicts (e.g., if the code in `src/` contradicts the plans in `first_draft.md`).

### Phase 2: Document Generation

You will now generate the content for the new `project_status.md` file. It **MUST** follow this structure precisely. Populate every section based on your findings from Phase 1.

```markdown
# Project Status & Roadmap

## 1. Project Overview
* (A brief 1-2 sentence summary of the project's main goal, synthesized from all sources.)

## 2. Current Status (What is Done)

### 2.1. Completed Features & Milestones
* (A list of completed work, based on `first_draft.md`, docs, and confirmed in conversation history.)

### 2.2. Current Architecture & Design
* (A detailed explanation of *how* the project is currently built.)

#### 2.2.1. Implemented Codebase State
* (An analysis of the *actual code* from `src/` and `tests/`. What is the structure? What modules exist? What is the test coverage like *in practice*?)

#### 2.2.2. Design Patterns & System Design
* (List patterns currently *in use* (e.g., dataclasses, context managers,
    factories) and *why* they were chosen. Describe data flow.)

#### 2.2.3. Key Decisions & Rationale
* (Document specific technology or algorithm choices (e.g., "We use `DuckDB`
    for..."). Pull this from docs, conversation, and ADRs.)

### 2.3. Known Gaps & Technical Debt
* (A list of what is *missing* or *wrong* with the *already-built* parts. e.g.,
    "The `GEO` distance function is implemented but lacks tests," "The documentation
    for module X is missing," "The `test_parser_basic.py` file is empty.")

## 3. Future Roadmap (What Needs to Be Done)

### 3.1. Immediate Next Steps (Priority Tasks)
* (A list of the next 1-3 tasks to be implemented, based on conversation and
    gaps identified in 2.3.)
* **How & Why:** (Proposed implementation plan, required design patterns, and
    target modules for these tasks.)

### 3.2. Future Goals & Long-Term Features
* (A long-term list of planned features from `first_draft.md` or docs that are
    not yet started.)
* **Proposed Design:** (High-level thoughts on system design, patterns, or
    choices for these *future* features.)
```

### Phase 3: Self-Verification

1. **Internal Critique:** Immediately after generating the document content, you **MUST** use #actor-critic-thinking.
2. **The Critic's Job:** The Critic's role is to verify compliance against three things:
    * **Protocol Compliance:** "Did I correctly use #sequentialthinking *twice* (once for planning, once for synthesis) as required in Phase 1?"
    * **Structural Compliance:** "Does the generated document *exactly* match the 3-part structure defined in Phase 2, including all sub-headings like `2.2.1. Implemented Codebase State`?"
    * **Contextual Completeness:** "Does my analysis in 'Section 2. Current Status' *explicitly* synthesize information from **all four** required sources (docs, draft, source code, and conversation history)? Did I note where the code differs from the docs?"

### Phase 4: User Validation

1. **Get Feedback:** After you have completed and presented your internal critique, you **MUST** use the `#get_user_input` tool.
2. **Prompt:** Example text, add information suggesting how we should proceed. Think about it before.
    > "I have generated the new `project_status.md` and performed a self-critique. Please review the output. Does it meet the required structure and quality?"
