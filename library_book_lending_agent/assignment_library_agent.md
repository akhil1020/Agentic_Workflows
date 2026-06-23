# Assignment: Library Book Lending Agent

## Overview

Build an agentic workflow for a **public library system** that handles book checkouts, returns, reservations, and inventory queries. The agent should implement both the **Tools-Only Planning** pattern and the **Code-as-Plan** pattern — mirroring the two approaches in the customer_service_agent reference project.

---

## Domain

A small public library with a catalog of books. Members can:
- Check out available books
- Return books they have borrowed
- Reserve books that are currently checked out
- Query availability, overdue status, and member borrowing history

---

## Expected Output (What the Agent Should Handle)

### Read-only queries
- "Is *The Great Gatsby* available?"
- "What books does member M003 currently have checked out?"
- "Show me all science fiction books in the catalog."
- "Are there any overdue books today (2026-06-23)?"

### Mutation queries
- "Member M001 wants to check out *Dune* (2 copies)."
  - Expected: stock decremented, transaction logged, due date set 14 days out
- "Member M002 is returning *1984*."
  - Expected: stock incremented, transaction closed, overdue fine computed if applicable
- "Member M003 wants to reserve *Atomic Habits* — it's currently out of stock."
  - Expected: reservation record created, member notified when available
- "Member M001 checks out *Sapiens* and *The Pragmatic Programmer* in one request."
  - Expected: one transaction record per book (no aggregation), each with its own due date

### Failure / validation cases
- "Member M002 tries to check out *Dune* but already has 3 books (the limit)."
  - Expected: validation fails, human-readable error returned, no mutation applied
- "Member M004 tries to return a book they never checked out."
  - Expected: assertion fails, execution halts, error explained in plain English

---

## Data Model

### `catalog` table
| field | type | notes |
|-------|------|-------|
| book_id | str | e.g. BK001 |
| title | str | |
| author | str | |
| genre | str | fiction / non-fiction / sci-fi / self-help / tech |
| total_copies | int | total owned by library |
| available_copies | int | copies currently on shelf |
| price_value | float | replacement cost (used for fines calculation) |

**Seed data (minimum 6 books):**

| book_id | title | author | genre | total_copies | available_copies | price_value |
|---------|-------|--------|-------|-------------|-----------------|-------------|
| BK001 | Dune | Frank Herbert | sci-fi | 3 | 2 | 18.99 |
| BK002 | 1984 | George Orwell | fiction | 4 | 3 | 12.99 |
| BK003 | Sapiens | Yuval Noah Harari | non-fiction | 2 | 2 | 22.00 |
| BK004 | Atomic Habits | James Clear | self-help | 2 | 0 | 19.99 |
| BK005 | The Pragmatic Programmer | Hunt & Thomas | tech | 3 | 3 | 34.99 |
| BK006 | The Great Gatsby | F. Scott Fitzgerald | fiction | 5 | 5 | 10.99 |

### `transactions` table
| field | type | notes |
|-------|------|-------|
| txn_id | str | e.g. TXN001 |
| member_id | str | e.g. M001 |
| book_id | str | |
| txn_type | str | checkout / return / reservation |
| date | str | ISO date string |
| due_date | str | ISO date (checkout only, else null) |
| fine | float | computed on return if overdue (else 0.0) |
| status | str | open / closed / reserved |

**Seed data:** Opening record (TXN001) as system initialization + 2–3 sample checkouts already in flight.

### `members` table
| field | type | notes |
|-------|------|-------|
| member_id | str | e.g. M001 |
| name | str | |
| email | str | |
| active_checkouts | int | maintained by agent (max = 3) |

**Seed data (minimum 4 members):** M001 Alice, M002 Bob, M003 Carol, M004 Dave.

---

## Tools to Implement

### Read tools
| tool | description |
|------|-------------|
| `get_catalog_data()` | Returns full catalog as DataFrame |
| `get_transactions_data()` | Returns all transactions as DataFrame |
| `get_member_data()` | Returns all members as DataFrame |
| `lookup_book(title_or_id)` | Finds a single book record |
| `lookup_member(member_id)` | Finds a single member record |
| `get_member_checkouts(member_id)` | Returns open transactions for a member |
| `compute_fine(due_date, return_date, price_value)` | Calculates overdue fine (1% of price per day overdue) |

### Write tools
| tool | description |
|------|-------------|
| `checkout_book(member_id, book_id, due_date)` | Decrements available_copies, logs TXN, increments active_checkouts |
| `return_book(member_id, book_id, return_date)` | Increments available_copies, closes TXN, applies fine, decrements active_checkouts |
| `reserve_book(member_id, book_id)` | Creates reservation TXN (no stock change) |
| `append_transaction(...)` | Low-level transaction insert (called by above tools) |

### Validation tools
| tool | description |
|------|-------------|
| `assert_book_available(book_id)` | Fails if available_copies == 0 |
| `assert_member_under_limit(member_id)` | Fails if active_checkouts >= 3 |
| `assert_open_checkout_exists(member_id, book_id)` | Fails if no open TXN found for return |
| `assert_not_already_reserved(member_id, book_id)` | Fails if duplicate reservation |

---

## Files to Create

```
library_agent/
├── tools.py                  # tool registry + executor (same pattern as customer_service_agent)
├── db_utils.py               # TinyDB helpers: seed_db(), schema builders, balance/id helpers
├── utils.py                  # display helpers (print_html, before/after snapshots)
├── library_db.json           # TinyDB store (auto-generated by seed_db())
├── M1_tools_only.ipynb       # Approach 1: JSON plan → reflect → execute
└── M2_code_as_plan.ipynb     # Approach 2: LLM writes Python → exec in sandbox
```

---

## Approach 1 — Tools-Only Planning (`M1_tools_only.ipynb`)

The LLM produces a **JSON plan** (list of steps). Each step specifies a tool name and its arguments (no raw Python, no SQL). A separate executor runs each step and halts on the first validation failure.

**Required pipeline cells:**

1. **Plan generation** — prompt the LLM to produce a JSON plan for the user query
2. **Reflection** — second LLM call critiques the draft plan and produces a `revised_plan`
3. **Execution** — `execute_plan_tools_only()` runs steps, applies validations, auto-updates DataFrames
4. **Error explanation** — if execution failed, a final LLM call translates the error to plain English for the member

**Example plan shape (checkout):**
```json
[
  { "step": 1, "description": "Look up book", "tools": [{"name": "lookup_book", "args": {"title": "Dune"}, "output_key": "book"}] },
  { "step": 2, "description": "Verify availability", "tools": [{"name": "assert_book_available", "args": {"book_id_from": "context.book.book_id"}}] },
  { "step": 3, "description": "Check member limit", "tools": [{"name": "assert_member_under_limit", "args": {"member_id": "M001"}}] },
  { "step": 4, "description": "Check out book", "tools": [{"name": "checkout_book", "args": {"member_id": "M001", "book_id_from": "context.book.book_id", "due_date": "2026-07-07"}}] }
]
```

---

## Approach 2 — Code-as-Plan (`M2_code_as_plan.ipynb`)

The LLM writes **executable Python** that uses TinyDB tables directly. The notebook extracts the code block and runs it in a sandboxed namespace. The generated code must set `answer_text` (member-facing message) and `STATUS` (`"SUCCESS"` or `"FAILED"`).

**Required pipeline cells:**

1. **Before snapshot** — capture catalog and transaction state
2. **Code generation** — prompt the LLM; extract `<execute_python>...</execute_python>` block
3. **Safe execution** — run in namespace containing `{catalog_tbl, transactions_tbl, members_tbl, get_current_balance, next_txn_id, compute_fine}`
4. **After snapshot** — capture updated state
5. **Display** — show before/after side by side plus `answer_text` to the member

**Sandbox namespace must expose:**
- `catalog_tbl`, `transactions_tbl`, `members_tbl` (TinyDB Table objects)
- `next_txn_id()` — returns next TXN id string
- `compute_fine(due_date_str, return_date_str, price_value)` — returns float
- `TODAY` — string constant `"2026-06-23"`

**Generated code contract:**
- Must set `answer_text: str` — the response shown to the member
- Must set `STATUS: str` — `"SUCCESS"` or `"FAILED"`
- One `transactions_tbl.insert(...)` call per book (no batching)
- Must not import external libraries beyond what's in the namespace

---

## Key Constraints & Business Rules

1. A member may have at most **3 books** checked out simultaneously.
2. Checkout period is **14 days**; overdue fine = **1% of replacement cost per day** overdue.
3. A reservation does **not** decrement stock; it only creates a record and flags the book as reserved.
4. Returns must match an **open checkout** for the same member + book; otherwise validation fails.
5. Multi-book requests must produce **one transaction per book** (never aggregated into a single record).
6. All mutations must be preceded by the relevant assertions; the executor halts on the first failure.

---

## Grading / Completion Criteria

- [ ] `seed_db()` initializes all three tables with the data above
- [ ] All 8 read/write tools implemented and registered in `TOOL_REGISTRY`
- [ ] All 4 validation tools implemented with clear error messages
- [ ] Approach 1 notebook runs end-to-end for at least: one successful checkout, one successful return, one failure (member at limit)
- [ ] Approach 2 notebook runs end-to-end for at least: one read-only query, one multi-book checkout, one failed return
- [ ] Before/after snapshots displayed for all mutation scenarios
- [ ] Error explanation cell produces member-friendly text (not a raw traceback)
- [ ] `library_db.json` readable and matches expected schema after all mutations
