# SQL Agent with Reflection - Query Improvement

This activity demonstrates the reflection design pattern for SQL query generation, where one LLM generates queries and another evaluates and improves them iteratively.

## Overview

The SQL agent follows a reflection-based workflow:
1. **Generate**: Create initial SQL query from natural language question
2. **Execute**: Run the query and capture results
3. **Evaluate**: Have another LLM assess if results answer the question adequately  
4. **Refine**: Improve the SQL query based on evaluation feedback
5. **Final Execute**: Run the refined query for the final result

## Prerequisites

Ensure you have a `.env` file in the root of the repository with API keys for:
- `OPENAI_API_KEY` - OpenAI API access
- `GOOGLE_API_KEY` - Google AI Studio access
- `ANTHROPIC_API_KEY` - Anthropic Claude access
- `TAVILY_API_KEY` - Tavily web search API access

Install dependencies from the root directory:
```bash
pip install -r requirements.txt
```

## Files

- `sql.ipynb` - Main notebook demonstrating SQL reflection workflow
- `utils.py` - Utility functions for database operations
- `products.db` - SQLite database (auto-generated when running notebook)

## Running the Activity

1. **Open and run the notebook**:
   - Open `sql.ipynb` in Jupyter
   - Run all cells sequentially

2. **The notebook will**:
   - Create a sample products database with 100 items
   - Show database schema and sample data
   - Execute the reflection workflow with example queries
   - Display the improvement process step-by-step

3. **Example workflow**:
   ```python
   results = run_sql_workflow("products.db", 
                              "Which color of product has the highest total sales?",
                              model_generation="openai:gpt-4o-mini",
                              model_evaluation="openai:gpt-4o")
   ```

## Database Schema

Auto-generated `products.db` contains:
- **Table**: products
- **Columns**: id, name, brand, category, color, price, stock, total_sales
- **Data**: 100 random products with brands (Nike, Adidas, Puma, etc.), categories (shoes, hoodie, t-shirt, etc.), and colors

## Key Learning Points

- **Reflection Pattern**: How one LLM can evaluate and improve another's SQL generation
- **Error Recovery**: Fixing syntax errors and logical issues through reflection
- **Query Optimization**: Improving query structure based on evaluation feedback
- **Multi-Model Cooperation**: Using different models for generation vs evaluation
- **Iterative Improvement**: Systematic refinement of database queries

## Expected Outputs

The workflow shows progression through reflection:

1. **Initial Query**: May contain formatting issues or logical errors
2. **Evaluation Feedback**: LLM assessment of query quality and result adequacy
3. **Refined Query**: Improved version based on feedback
4. **Comparison**: Side-by-side view of original vs improved results

## Example Improvements

Common issues fixed by reflection:
- Removing SQL markdown formatting (````sql`)
- Fixing column name errors
- Improving query logic and structure
- Ensuring proper aggregation functions



---

## Assignment: Personal Finance Tracker with SQL Reflection Agent

### Context

You have a database of personal transactions (expenses and income). Build an agentic workflow where an LLM converts natural language questions about your finances into SQL, executes them, reflects on the results, and self-corrects — exactly like the lab but on a domain you actually care about.

---

### The Database

Create a SQLite DB with a single event-sourced `transactions` table:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment PK |
| `date` | DATE | Transaction date |
| `category` | TEXT | `food`, `rent`, `salary`, `entertainment`, `transport`, `utilities` |
| `type` | TEXT | `income` or `expense` |
| `amount` | REAL | Always positive |
| `description` | TEXT | Short note |
| `payment_method` | TEXT | `cash`, `card`, `upi` |

Seed it with at least 6 months of random data (mix of income and expenses).

---

### Tasks

**Task 1 — SQL Generator**

Write `generate_sql(question, schema, model)` that takes a plain-English question and returns a SQL query. Test it with:

- `"What is my total spending on food this month?"`
- `"Which category did I spend the most on?"`
- `"What is my savings rate (income minus expenses) for each month?"`

**Task 2 — Reflection without execution feedback**

Write `refine_sql(question, sql, schema, model)` that reviews the SQL text only and returns `(feedback, refined_sql)`. Find a question where V1 is wrong but V2 fixes it just from reading the query.

**Task 3 — Reflection with execution feedback**

Write `refine_sql_with_output(question, sql, df_result, schema, model)` that also sees the actual query result. The key challenge: make it catch the case where `type = 'expense'` rows need to be filtered (not summed with income). Force this bug by asking:

- `"What is my net spending per category?"` — V1 will likely mix income and expense rows.

**Task 4 — End-to-end workflow**

Wire it all into `run_finance_workflow(db_path, question)` that runs all 5 steps:

```
schema → V1 → execute → reflect → V2 → execute
```

Print each step's output using `utils.print_html`.

**Task 5 — Experiment**

Run the same question with two different models for generation vs reflection (e.g., `gpt-4o-mini` for generation, `gpt-4.1` for reflection). Compare whether the reflection quality differs.

---

### What You'll Learn

| Lab Concept | How This Assignment Uses It |
|---|---|
| Event-sourced schema | Derive totals from raw events, not stored aggregates |
| `generate_sql` | Practice writing a clean prompt with schema injection |
| `refine_sql` without feedback | Understand where text-only reflection fails |
| `refine_sql` with execution output | See why grounding reflection in real data matters (the sign/filter bug) |
| `run_workflow` end-to-end | Understand how the full agentic loop chains together |
| Multi-model setup | Learn when to use a cheap model vs a strong one |

---

### Bonus Challenge

Add a **third reflection pass**: if V2 still has an `error` column in the result (from `utils.execute_sql`), automatically retry once more with the error message as feedback. This is the real-world pattern for self-healing agents.