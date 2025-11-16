# Validation Script Usage

**File:** `scripts/validate_refactor.sh`

**Purpose:** Continuous validation during M14-M15 refactor

---

## When to Run

- ✅ After EVERY task completion
- ✅ Before EVERY commit
- ✅ Before EVERY git push
- ✅ When encountering unexpected behavior

**Frequency:** At least 10-15 times during M14-M15 implementation

---

## Expected Behavior

- Reports ALL errors (doesn't stop on first failure)
- Uses `timeout` to prevent hangs (60s for mypy, 30s for tests)
- Returns exit code 0 if critical tests pass, 1 otherwise
- Shows progress with emojis: ✅ (pass), ❌ (fail), ⚠️ (expected)

---

## Interpreting Results

### ✅ Green Checkmark

- Test passed completely
- No action needed

### ❌ Red X

- **CRITICAL FAILURE** - must fix before proceeding
- Indicates regression or broken implementation
- Examples:
  - Type checking failed (new mypy errors introduced)
  - Import safety check failed (circular import)

### ⚠️ Warning Triangle

- **EXPECTED FAILURE** - not yet implemented
- Safe to ignore during early phases
- Examples:
  - Protocol tests not created yet
  - Strategy tests not implemented yet
  - Integration tests directory doesn't exist

---

## 5-Stage Validation Process

### Stage 1: Type Checking (mypy --strict)

**What it checks:**

- All Python files in `code/src/` for type safety
- Enforces strict mode (no `Any`, no missing annotations)

**Expected during M14-M15:**

- ✅ Should pass (baseline errors exist but won't increase)
- ❌ FAIL means new type errors introduced

**How to debug:**

```bash
# See full mypy output
mypy code/src/ --config-file mypy.ini

# Check only new files
mypy code/src/protocols/strategy_protocols.py --strict
mypy code/src/algorithms/tour_operators/ --strict
mypy code/src/algorithms/strategies/ --strict
```

---

### Stage 2: Import Safety Check

**What it checks:**

- Can import protocols without errors
- Can import tour_operators (if implemented)
- No circular import issues

**Expected during M14-M15:**

- ✅ `backend.py` should always import
- ⚠️ `tour_operators` may not be ready initially
- ❌ FAIL means circular dependency or syntax error

**How to debug:**

```bash
# Test specific imports
python -c "from code.src.protocols.strategy_protocols import NeighborStrategy"
python -c "from code.src.algorithms.tour_operators.swap import swap_cities"
python -c "from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy"

# If import fails, check for:
# 1. Syntax errors in the file
# 2. Circular imports (check import_dependencies.md)
# 3. Missing __init__.py files
```

---

### Stage 3: Protocol Tests

**What it checks:**

- Unit tests for protocol definitions (`tests/unit/protocols/`)
- Protocol compliance validation

**Expected during M14-M15:**

- ⚠️ Initially: Directory doesn't exist (M14.1 not complete)
- ✅ After M14.1: All protocol tests pass
- ❌ FAIL means protocol implementation broken

**How to debug:**

```bash
# Run protocol tests with verbose output
pytest tests/unit/protocols/ -v --tb=short

# Run single test file
pytest tests/unit/protocols/test_strategy_protocols.py -v

# Run specific test
pytest tests/unit/protocols/test_strategy_protocols.py::test_neighbor_strategy_protocol -v
```

---

### Stage 4: Strategy Tests

**What it checks:**

- Unit tests for strategy implementations (`tests/unit/strategies/`)
- Correctness of neighbor/mutation/crossover operators

**Expected during M14-M15:**

- ⚠️ M14.0-M14.2: Not implemented yet
- ⚠️ M14.3: Only SA strategies tested
- ✅ M14.4+: All strategy tests pass
- ❌ FAIL means strategy implementation broken

**How to debug:**

```bash
# Run all strategy tests
pytest tests/unit/strategies/ -v

# Run specific strategy tests
pytest tests/unit/strategies/test_neighbor_strategies.py -v
pytest tests/unit/strategies/test_mutation_strategies.py -v

# Run single test
pytest tests/unit/strategies/test_neighbor_strategies.py::test_random_swap_returns_valid_tour -v
```

---

### Stage 5: Integration Smoke Test

**What it checks:**

- Integration tests for SA and GA with strategies
- End-to-end workflow validation

**Expected during M14-M15:**

- ⚠️ M14.0-M14.2: Not implemented yet
- ⚠️ M14.3-M14.4: Partially implemented
- ✅ M14.5+: All integration tests pass
- ❌ FAIL means strategy composition broken

**How to debug:**

```bash
# Run integration tests
pytest tests/integration/ -k "test_sa_strategy or test_ga_strategy" -v

# Run all integration tests
pytest tests/integration/ -v
```

---

## What to Do on Failure

### ❌ Type Checking Failed

1. **Read error message carefully**
   - Identify file and line number
   - Look for specific mypy error code (e.g., `[no-untyped-def]`)

2. **Common fixes:**
   - Add return type annotation: `def foo() -> int:`
   - Add type hints to parameters: `def foo(x: int, y: str) -> None:`
   - Use proper generic types: `List[int]` not `list`
   - Import from `typing`: `from typing import List, Optional`

3. **Check baseline:**
   ```bash
   # Is this a NEW error or existing?
   diff mypy_baseline.txt <(mypy code/src/ --config-file mypy.ini 2>&1)
   ```

---

### ❌ Import Safety Failed

1. **Check for circular imports:**
   - Review `documentation/architecture/import_dependencies.md`
   - Ensure protocols don't import from algorithms
   - Ensure strategies don't import from metaheuristics

2. **Check for syntax errors:**
   ```bash
   python -m py_compile code/src/path/to/file.py
   ```

3. **Check **init**.py files:**
   - All directories must have `__init__.py`
   - Check exports in `__all__`

---

### ❌ Tests Failed

1. **Run with verbose output:**
   ```bash
   pytest path/to/test_file.py -vv --tb=long
   ```

2. **Check test implementation:**
   - Is the test correctly written?
   - Does it match the implementation?
   - Are fixtures set up correctly?

3. **Check implementation:**
   - Does the code match the protocol?
   - Are all edge cases handled?
   - Are type hints correct?

---

### 📝 Stuck >30min?

1. **Document the blocker:**
   - Add to `M14_task_log.md` under "Blockers" section
   - Include: what you tried, error messages, hypothesis

2. **Review related documentation:**
   - `import_dependencies.md` (layer rules)
   - `M14_M15_DETAILED_TASKS.md` (task details)
   - `mypy_baseline.md` (type error patterns)

3. **Try simpler approach:**
   - Can you reduce the problem scope?
   - Can you test in isolation?
   - Can you add debug prints?

---

## Example Session

```bash
# After implementing M14.1 (protocols)
$ bash scripts/validate_refactor.sh

======================================
M14-M15 Validation Suite
======================================

[1/5] Type Checking (mypy --strict)...
✅ Type checking passed

[2/5] Import Safety Check...
✅ Backend protocol imports OK
✅ Protocol imports OK

[3/5] Protocol Tests...
✅ Protocol tests passed

[4/5] Strategy Tests...
⚠️  Strategy test directory not created yet

[5/5] Integration Smoke Test...
⚠️  Integration test directory not created yet

======================================
✅ ALL CRITICAL VALIDATIONS PASSED
```

**Interpretation:**

- Core protocols implemented correctly ✅
- Strategies not yet implemented (expected) ⚠️
- Ready to proceed to next phase ✅

---

## Pro Tips

1. **Run validation BEFORE starting next task**
   - Ensures clean slate
   - Catches regressions early

2. **Run validation AFTER completing task**
   - Confirms implementation works
   - Catches bugs immediately

3. **Keep validation script terminal open**
   - Quick feedback loop
   - Just hit ↑ Enter to re-run

4. **Don't ignore warnings forever**
   - ⚠️ should become ✅ as you implement features
   - Track progress: count warnings decreasing over time

5. **Use focused validation for debugging**
   - Don't re-run all 5 stages if only one changed
   - Run `mypy file.py` or `pytest test_file.py` directly

---

## Validation Checklist

Before committing code:

- [ ] `bash scripts/validate_refactor.sh` exits with code 0
- [ ] No NEW ❌ failures introduced
- [ ] ⚠️ warnings match current implementation phase
- [ ] Type hints on all new functions
- [ ] Tests written for new code
- [ ] Documentation updated

---

## Notes

**Created:** 2025-01-28 (M14.0.4)  
**Last Updated:** 2025-01-28  
**Script Location:** `scripts/validate_refactor.sh`

**Related Documents:**

- `documentation/architecture/import_dependencies.md` (layer rules)
- `documentation/progress/mypy_baseline.md` (type checking baseline)
- `M14_M15_DETAILED_TASKS.md` (task breakdown)
