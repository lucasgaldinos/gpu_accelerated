Follow instructions in [thinking_protocol.prompt.md](file:///home/lucas_galdino/TCC-name_to_define/gpu_accelerated/.github/prompts/thinking_protocol.prompt.md).
It's extremely important you keep doing the thinking protocols. The processes are more important than the speed.

**The way you complete this process is more important than doing it fast. Focus on quality and protocol adherence.**

# Task: Refactor Notebook, Document API Failures, and Update Status

**Goal:**
The notebook [task-2-checkpoint](./task2-cheeckpoint.ipynb) is non-functional, inelegant (as too cluttered, many if statements, no use of recurrent functions), and fails to demonstrate the API's strengths and limitations. Your primary goal is to **refactor this notebook** to be robust and elegant.

A critical part of this task is to **document where the API fails**. The provided context shows the underlying database is corrupt. You MUST assume the notebook *will fail* when it tries to load data (like 'gil262') and your refactor must handle this gracefully.

Finally, you will update [project status](../../project_status.md) to reflect these findings.

**Context Sources:**

1. **Target Notebook:** [task-2-checkpoint](./task2-cheeckpoint.ipynb) (This is the file to be refactored).
2. **Project Documentation:** #file:project_status.md (For reading the TOC and updating Gaps/Tasks).
3. **Database Bug Context:** The following summary from our `Routing_data` conversation explains *why* the notebook will fail. The database has a `UNIQUE(name)` constraint instead of `UNIQUE(name, type)`, meaning CVRP instances like `gil262.vrp` were lost, and loading them will fail or return corrupt TSP data.

    <details>
    <summary>Click to expand Database Bug Context</summary>

    ```md
    I understand now! The issue is that VRP and TSP files can have duplicate names across different problem types, but my database schema only has a UNIQUE constraint on `problems.name` without considering the `type` field. This means `gil262.vrp` (CVRP) and `gil262.tsp` (TSP) are both valid files, but the database only keeps one.
    ...
    This explains the "corrupted" medium CVRP instances!
    ...
    BUG 1: Schema Constraint [Routing data repo](../../../Routing_data/src/converter/database/operations.py#L55)
    ...
    BUG 2: Batch Deduplication Logic (operations.py:571-588)
    ...
    BUG 3: Database-Level Deduplication (operations.py:685-706)
    ```
    </details>

**Output Constraints (Notebook Refactor):**
You MUST rewrite [task-2-checkpoint](./task2-cheeckpoint.ipynb). The new notebook must adhere to the following:

1. **Graceful API Failure (MANDATORY):**
    * The notebook MUST attempt to load a known-corrupt problem (e.g., 'gil262' as CVRP).
    * This attempt MUST be wrapped in a `try...except` block.
    * In the `except` block, you must print a clear Markdown message explaining *why* it failed, explicitly referencing the **database bug** (duplicate `name` constraint).
    * After catching the error, you MUST use #get_user_input to ask how to proceed (e.g., "Database is corrupt. Should I stop, or continue with valid TSP data like 'berlin52'?").
2. **Elegance & Readability:**
    * **Refactor Helpers:** Move helper functions (like plotting logic) to the *top* of the notebook in a dedicated "Setup" or "Helper Functions" section.
    * **Fix `print()` Abuse:** Replace excessive `print()` statements with elegant formatting (e.g., Markdown, f-strings in triple-quotes, or `rich.print`).
    * **Fix Timing:** Remove clunky, in-line timing logic. Implement a single, reusable `@timing_decorator` in the setup section and apply it to the functions you want to measure.
3. **Remove Redundancy:**
    * Analyze `Cell 11` and `Cell 17`. If they are redundant, consolidate them into a single, clear cell with a Markdown explanation.
4. **Data Visualization:**
    * Add at least one plot (e.g., using `matplotlib`) to visualize a valid tour (e.g., for 'berlin52', which should load correctly).
5. **Clarity:**
    * `Cell 13` (and others) must have clear Markdown explanations for what is happening and why.

**Documentation Constraints (project_status.md Update):**
After refactoring the notebook, you MUST update #file:project_status.md:

1. **Read the TOC:** You MUST first read the `#sym:## TOC` to find the correct sections for updates.
2. **Document Gaps:** Add a new entry to the "Known Gaps" section detailing the **critical database corruption bug** (`UNIQUE(name)` constraint) and note that it blocks all CVRP benchmark validation.
3. **Register New Task:** Add a *new* high-priority task to "Immediate Next Steps" (e.g., "Fix database schema bug in `Routing_data` and regenerate `routing.duckdb`").
4. **Register Task Done:** Add this notebook refactor to the "Completed Features" section.

**Process Constraints:**

1. You **MUST** use #sequentialthinking for your implementation plan (for both notebook refactor and doc updates).
2. You **MUST** follow `thinking_protocol.prompt.md` throughout.
W3. **No Workarounds:** Do not try to "fix" the database bug. Your task is to *demonstrate the failure* and *document it*.

**Verification (Mandatory):**

1. After implementation and documentation, you **MUST** use #actor-critic-thinking.
2. The Critic **MUST** score 3 points (1-10 scale), with 8.5+ required to pass:
    * **Task Completion (Notebook):** Is it elegant (decorator, plots, no redundancy, `print()` fixed)?
    * **Code Quality (API Focus):** Does the notebook clearly demonstrate *using the API* and *where it fails*?
    * **Documentation Update Quality:** Is `project_status.md` updated correctly? Is the DB corruption bug documented as a GAP? Is the new task registered?
3. Your final response **MUST** include this self-critique, following the honest analysis example (checking for cognitive biases).
4. After the self-critique, use #get_user_input to ask for feedback.
