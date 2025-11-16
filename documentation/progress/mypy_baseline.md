# Mypy Baseline (Before M14 Refactor)

**Date:** 2025-01-28  
**Command:** `mypy code/src/ --config-file mypy.ini`  
**Total Output Lines:** 472  
**Configuration:** Strict mode enabled

---

## Goal

After M14-M15 refactor, mypy errors should be ≤ baseline (ideally 0 for new code).

**Target:** New protocol and strategy code should be 100% type-safe.

---

## Common Error Types (from baseline)

### 1. Missing Type Hints

- Function signatures without return type annotations
- Example: `error: Function is missing a return type annotation [no-untyped-def]`
- **Action:** Add `-> ReturnType` to all functions in new code

### 2. Generic Type Parameters

- Missing type parameters for NDArray, ndarray
- Example: `error: Missing type parameters for generic type "NDArray" [type-arg]`
- **Action:** Use `NDArray[np.float64]` instead of `NDArray`

### 3. BackendModule Protocol Compatibility

- numpy Module doesn't perfectly match BackendModule protocol
- Example: `Incompatible default for argument "xp" (default has type Module, argument has type "BackendModule")`
- **Root Cause:** Numpy's type stubs are overly specific (many @overload variants)
- **Action:** May need to relax BackendModule protocol or use `# type: ignore` in specific cases

### 4. Name Not Defined Errors

- Forward references without quotes
- Example: `error: Name "BenchmarkConfig" is not defined [name-defined]`
- **Action:** Use `from __future__ import annotations` or quote forward refs

---

## Acceptable Errors (won't fix in M14)

### Third-Party Library Stubs

- cupy, numpy, scipy stubs incompleteness
- Already ignored in mypy.ini via `ignore_missing_imports = True`

### Legacy Code Not Touched by Refactor

- benchmarking/collectors.py
- benchmarking/config.py
- distances/pairwise.py
- distances/matrix.py

**Note:** These files are NOT part of M14-M15 scope (metaheuristics refactor).

---

## M14-M15 Type Safety Requirements

All NEW code (protocols, strategies, operators) must:

1. **Have explicit type hints:**
   ```python
   def generate_neighbor(
       self,
       tour: List[int],
       problem: Problem,
       xp: BackendModule
   ) -> List[int]:
       ...
   ```

2. **Use proper Protocol typing:**
   ```python
   from typing import Protocol
   
   class NeighborStrategy(Protocol):
       def generate_neighbor(...) -> List[int]: ...
   ```

3. **Pass mypy --strict on new files:**
   ```bash
   mypy code/src/protocols/strategy_protocols.py --strict
   mypy code/src/algorithms/tour_operators/ --strict
   mypy code/src/algorithms/strategies/ --strict
   ```

---

## Baseline File Location

**Full Output:** `mypy_baseline.txt` (472 lines)

**Sample Errors (first 30 lines):**

```
code/src/distances/pairwise.py:545: error: Incompatible return value type
code/src/benchmarking/config.py:217: error: Function is missing a return type annotation
code/src/benchmarking/collectors.py:101: error: Name "BenchmarkConfig" is not defined
code/src/protocols/bin_packing_protocol.py:196: error: Missing type parameters for generic type "NDArray"
code/src/distances/matrix.py:25: error: Missing type parameters for generic type "ndarray"
code/src/distances/matrix.py:25: error: Incompatible default for argument "xp"
```

---

## Validation Commands

### Check Baseline Error Count

```bash
wc -l mypy_baseline.txt
# Expected: 472
```

### Check New Code Only (after implementation)

```bash
# Protocols
mypy code/src/protocols/strategy_protocols.py --strict

# Tour Operators
mypy code/src/algorithms/tour_operators/ --strict

# Strategies
mypy code/src/algorithms/strategies/neighbor_strategies.py --strict
mypy code/src/algorithms/strategies/mutation_strategies.py --strict

# Target: 0 errors for all new files
```

### Compare Against Baseline

```bash
# Run current mypy check
mypy code/src/ --config-file mypy.ini > mypy_current.txt 2>&1

# Compare line counts
echo "Baseline: $(wc -l < mypy_baseline.txt) errors"
echo "Current: $(wc -l < mypy_current.txt) errors"

# Diff (should only show NEW errors if any)
diff mypy_baseline.txt mypy_current.txt
```

---

## Notes

- Baseline captured BEFORE any M14-M15 changes
- 472 lines of output (mix of errors and note lines)
- Most errors in legacy code (distances/, benchmarking/)
- M14-M15 will ADD code, not modify legacy files
- Goal: No regression (total errors should not increase)
- Stretch goal: Fix some legacy errors opportunistically

**Next Review:** After M14.1 (protocol implementation)
