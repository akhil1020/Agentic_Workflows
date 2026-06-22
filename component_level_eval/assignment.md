# Assignment: Component-Level Evaluation — Hiring Assistant Search Step

## Scenario

A hiring assistant agent has already been built. It searches the web for job market data and returns results as plain text with URLs. Your job is **not to build the agent** — it's to evaluate one component of it: **the web search step**.

The search step sometimes returns URLs from unreliable sources (random blogs, low-credibility job boards). You need to catch this before it corrupts downstream reports.

You are given a **mock search result** (below). Your task is to write the evaluation function and run it.

---

## Mock Search Result (Pre-built — do not change)

Paste this string into your notebook as `mock_search_output`:

```python
mock_search_output = """
Here are recent findings on software engineer hiring trends in 2024:

1. The US Bureau of Labor Statistics projects strong demand:
   https://bls.gov/ooh/computer-and-information-technology/software-developers.htm

2. Stack Overflow's annual developer survey covers compensation:
   https://stackoverflow.com/insights/survey/2024

3. A detailed salary breakdown by role:
   https://randomblog.io/tech-salaries-2024

4. McKinsey report on the future of tech work:
   https://mckinsey.com/capabilities/people-and-organizational-performance/our-insights

5. An informal Reddit thread with anecdotal data:
   https://reddit.com/r/cscareerquestions/comments/abc123

6. World Economic Forum on tech skills gap:
   https://weforum.org/agenda/2024/01/tech-skills-gap
"""
```

---

## Part 1 — Define Preferred Domains

Define a set `HIRING_TOP_DOMAINS` with trusted sources for hiring and labor market data. Start with the base list and **add at least 3 more domains** with a comment explaining why each is trustworthy:

```python
HIRING_TOP_DOMAINS = {
    "bls.gov",
    "oecd.org",
    "ilo.org",
    "levels.fyi",
    "stackoverflow.com",
    "hbr.org",
    "mckinsey.com",
    "weforum.org",
    "arxiv.org",
    # Add at least 3 more below, with a comment for each:
}
```

---

## Part 2 — Write the Evaluation Function

Implement `evaluate_hiring_sources(top_domains, raw, min_ratio=0.4)` that:

1. Extracts all URLs from `raw` using regex.
2. Checks each URL against `top_domains` — mark it `PREFERRED` or `NOT PREFERRED`.
3. Computes `ratio = preferred_count / total_urls`.
4. Returns `(flag: bool, report: str)` where `flag=True` means PASS.
5. Handles the edge case where no URLs are found.

Expected report format:

```
### Evaluation — Hiring Source Quality
- Total results: 6
- Preferred results: 4
- Ratio: 66.67%
- Threshold: 40%
- Status: ✅ PASS

**Details:**
- https://bls.gov/... → ✅ PREFERRED
- https://randomblog.io/... → ❌ NOT PREFERRED
...
```

---

## Part 3 — Run It on the Mock Data

```python
flag, report = evaluate_hiring_sources(HIRING_TOP_DOMAINS, mock_search_output)
print(report)
```

Verify your output matches the expected counts: 4 preferred out of 6 total.

---

## Part 4 — Experiment

Change one variable at a time and note the result:

| # | Change | Expected effect |
|---|---|---|
| A | Set `min_ratio=0.8` | Should it PASS or FAIL now? Why? |
| B | Remove `"mckinsey.com"` from `HIRING_TOP_DOMAINS` | How does the ratio change? |
| C | Add `"reddit.com"` to `HIRING_TOP_DOMAINS` | Does this make sense? Justify your answer. |

Write a one-line observation for each experiment as a comment.

---

## Part 5 — Short Answer

Answer in a markdown cell:

1. Why evaluate the search step alone instead of running the full pipeline every time?
2. What makes this evaluation "objective"? What is the ground truth?
3. The eval fails. Name two fixes you could apply to the **search step only** — without touching the reflection or report steps.
4. A teammate says: *"Just set `min_ratio=0.0` so it always passes."* What is wrong with this?

---

## Grading Rubric

| Criteria | Points |
|---|---|
| `HIRING_TOP_DOMAINS` has 3 added domains with justification | 15 |
| `evaluate_hiring_sources` extracts URLs, checks domains, computes ratio, returns `(bool, str)` | 30 |
| Edge case (no URLs) handled | 10 |
| Output matches expected counts on mock data | 20 |
| Experiments A–C with observations | 15 |
| Short answer questions | 10 |
| **Total** | **100** |

---

## Hints

- Extract URLs: `re.compile(r'https?://[^\s\]\)>\}]+')`
- Check domain: `any(d in url.split("/")[2] for d in top_domains)`
- `min_ratio=0.4` means at least 40% of links must be preferred to PASS.
