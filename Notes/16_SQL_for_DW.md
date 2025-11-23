# Topic 16: SQL for Data Warehousing

## 1. SQL/OLAP Operations

### The Cube Problem

**Scenario**: Computing all possible aggregations along dimensions

**Example**: SALES fact table with Product and Customer dimensions

**Traditional Approach Problem**:
- Must **scan entire table** several times
- One scan for each combination of dimensions
- Inefficient and time-consuming

---

### Traditional SQL Approach (Using UNION)

**Basic Cube Creation**:

```sql
-- Detail level (no aggregation)
SELECT ProductKey, CustomerKey, SalesAmount
FROM Sales

UNION

-- Aggregate by Product only
SELECT ProductKey, NULL, SUM(SalesAmount)
FROM Sales
GROUP BY ProductKey

UNION

-- Aggregate by Customer only
SELECT NULL, CustomerKey, SUM(SalesAmount)
FROM Sales
GROUP BY CustomerKey

UNION

-- Grand total
SELECT NULL, NULL, SUM(SalesAmount)
FROM Sales;
```

**Result Structure**:
```
ProductKey | CustomerKey | SalesAmount
-----------|-------------|------------
P1         | C1          | 100        ← Detail
P1         | C2          | 150        ← Detail
P1         | NULL        | 250        ← Product aggregate
NULL       | C1          | 200        ← Customer aggregate
NULL       | NULL        | 450        ← Grand total
```

**NULL Values**: Indicate aggregation level
- Both NULL → Grand total
- One NULL → Aggregated on other dimension

---

### Cube Complexity

**Formula for n dimensions**: 2ⁿ SELECT statements needed

**Examples**:
- **2 dimensions**: 2² = 4 queries (as shown above)
- **3 dimensions**: 2³ = 8 queries
- **4 dimensions**: 2⁴ = 16 queries

**Problem**: Exponential growth with more dimensions!

---

## 2. SQL/OLAP Extensions

### Three Key Operators

SQL/OLAP extends **GROUP BY** clause with:
1. **ROLLUP**
2. **CUBE**
3. **GROUPING SETS** (most powerful)

**Note**: ROLLUP and CUBE are **shorthands** for GROUPING SETS

---

### ROLLUP Operator

**Definition**: Computes **group subtotals** in the order given by attribute list

**Syntax**:
```sql
GROUP BY ROLLUP(attr1, attr2, ..., attrN)
```

**Behavior**: Creates **hierarchical aggregations**
- Groups by (attr1, attr2, ..., attrN)
- Groups by (attr1, attr2, ..., attrN-1)
- Groups by (attr1, attr2, ..., attrN-2)
- ...
- Groups by (attr1)
- Grand total ()

**Example**:
```sql
SELECT ProductKey, CustomerKey, SUM(SalesAmount)
FROM Sales
GROUP BY ROLLUP(ProductKey, CustomerKey);
```

**Equivalent GROUPING SETS**:
```sql
SELECT ProductKey, CustomerKey, SUM(SalesAmount)
FROM Sales
GROUP BY GROUPING SETS(
    (ProductKey, CustomerKey),  -- Detail level
    (ProductKey),               -- Product subtotal
    ()                          -- Grand total
);
```

**Result**:
```
ProductKey | CustomerKey | SUM(SalesAmount)
-----------|-------------|------------------
P1         | C1          | 100              ← (P1, C1)
P1         | C2          | 150              ← (P1, C2)
P1         | NULL        | 250              ← P1 subtotal
P2         | C1          | 100              ← (P2, C1)
P2         | NULL        | 100              ← P2 subtotal
NULL       | NULL        | 350              ← Grand total
```

**Key Characteristic**: **Hierarchical** - follows the order of attributes
- **Does NOT** compute CustomerKey-only aggregates

---

### CUBE Operator

**Definition**: Computes **all possible combinations** of attributes

**Syntax**:
```sql
GROUP BY CUBE(attr1, attr2, ..., attrN)
```

**Behavior**: Creates **complete multidimensional cube**
- All 2ⁿ combinations of attributes

**Example**:
```sql
SELECT ProductKey, CustomerKey, SUM(SalesAmount)
FROM Sales
GROUP BY CUBE(ProductKey, CustomerKey);
```

**Equivalent GROUPING SETS**:
```sql
SELECT ProductKey, CustomerKey, SUM(SalesAmount)
FROM Sales
GROUP BY GROUPING SETS(
    (ProductKey, CustomerKey),  -- Detail level
    (ProductKey),               -- Product-only aggregate
    (CustomerKey),              -- Customer-only aggregate
    ()                          -- Grand total
);
```

**Result**:
```
ProductKey | CustomerKey | SUM(SalesAmount)
-----------|-------------|------------------
P1         | C1          | 100              ← (P1, C1)
P1         | C2          | 150              ← (P1, C2)
P2         | C1          | 100              ← (P2, C1)
P1         | NULL        | 250              ← P1 subtotal
P2         | NULL        | 100              ← P2 subtotal
NULL       | C1          | 200              ← C1 subtotal
NULL       | C2          | 150              ← C2 subtotal
NULL       | NULL        | 350              ← Grand total
```

**Key Characteristic**: **Complete** - all possible aggregations
- Includes both ProductKey-only AND CustomerKey-only aggregates

---

### GROUPING SETS Operator

**Definition**: Most **flexible** operator - explicitly specify grouping combinations

**Syntax**:
```sql
GROUP BY GROUPING SETS(
    (attr1, attr2),
    (attr1),
    (attr2),
    ()
)
```

**Advantage**: 
- **Full control** over which aggregations to compute
- Can create **custom aggregation patterns**
- More efficient when you don't need all combinations

**Example - Custom Groupings**:
```sql
SELECT ProductKey, CustomerKey, Year, SUM(SalesAmount)
FROM Sales
GROUP BY GROUPING SETS(
    (ProductKey, Year),     -- Product by Year
    (CustomerKey, Year),    -- Customer by Year
    (Year)                  -- Year totals only
);
```

**Benefit**: Only computes **needed aggregations**, not all 2ⁿ combinations

---

### ROLLUP vs CUBE vs GROUPING SETS

| Operator | Aggregations | Use Case | Example (2 attributes) |
|----------|--------------|----------|------------------------|
| **ROLLUP** | Hierarchical (n+1 levels) | Subtotals in order | (A,B), (A), () |
| **CUBE** | All combinations (2ⁿ) | Complete cube | (A,B), (A), (B), () |
| **GROUPING SETS** | Custom combinations | Specific aggregations | Any explicit list |

**For 2 dimensions**:
- ROLLUP: 3 groupings
- CUBE: 4 groupings
- GROUPING SETS: Any you specify

---

## 3. Window Functions

### Overview

**Window Functions**: Perform calculations across **sets of rows** related to current row

**Three Key Concepts**:
1. **Window Partitioning**
2. **Window Ordering**
3. **Window Framing**

---

## 4. Window Partitioning

### Definition

**Purpose**: Compare **detailed data** with **aggregate values**

**Concept**: Create "windows" (partitions) and compute aggregates over them

---

### Basic Syntax

```sql
aggregate_function() OVER (PARTITION BY column)
```

**PARTITION BY**: Defines how to divide rows into windows

---

### Example: Maximum Sales per Product

**Scenario**: Find each customer's relevance relative to product's max sales

```sql
SELECT ProductKey, 
       CustomerKey, 
       SalesAmount,
       MAX(SalesAmount) OVER (PARTITION BY ProductKey) AS MaxAmount
FROM Sales;
```

**Result**:
```
ProductKey | CustomerKey | SalesAmount | MaxAmount
-----------|-------------|-------------|----------
P1         | C1          | 100         | 150
P1         | C2          | 150         | 150        ← Max for P1
P1         | C3          | 120         | 150
P2         | C1          | 200         | 200        ← Max for P2
P2         | C4          | 180         | 200
```

**How It Works**:
1. **Create partition** for each ProductKey
2. **Compute MAX** within each partition
3. **Repeat MAX value** for all rows in partition

**Key Point**: Each row keeps its **detail data** while showing **aggregate**

---

### Benefits

- ✅ **No GROUP BY** needed - preserves detail rows
- ✅ **Compare individual to aggregate** in same result
- ✅ **Multiple aggregates** possible in one query

**Common Aggregate Functions**:
- MAX(), MIN(), AVG(), SUM(), COUNT()

---

## 5. Window Ordering

### Definition

**Purpose**: Order rows **within each partition** for ranking and running calculations

**Syntax**:
```sql
function() OVER (PARTITION BY column ORDER BY column [ASC|DESC])
```

---

### Example: Ranking Products by Customer

**Scenario**: How does each product rank in sales for each customer?

```sql
SELECT ProductKey, 
       CustomerKey, 
       SalesAmount,
       RANK() OVER (
           PARTITION BY CustomerKey 
           ORDER BY SalesAmount DESC
       ) AS Rank
FROM Sales;
```

**Result**:
```
ProductKey | CustomerKey | SalesAmount | Rank
-----------|-------------|-------------|-----
P2         | C1          | 300         | 1    ← Best for C1
P1         | C1          | 100         | 2
P3         | C1          | 80          | 3
P1         | C2          | 250         | 1    ← Best for C2
P2         | C2          | 200         | 2
```

**How It Works**:
1. **Partition** by CustomerKey (separate ranking per customer)
2. **Order** by SalesAmount DESC within each partition
3. **Assign RANK** (1 = highest sales)

---

### Ranking Functions

**RANK()**: 
- Gaps in ranking for ties
- Example: 1, 2, 2, 4 (skips 3)

**DENSE_RANK()**:
- No gaps in ranking
- Example: 1, 2, 2, 3

**ROW_NUMBER()**:
- Unique number for each row
- Example: 1, 2, 3, 4 (even if ties)

---

## 6. Window Framing

### Definition

**Purpose**: Define **subset of partition** for calculations

**Use Cases**:
- **Moving averages**
- **Running totals**
- **Year-to-date** calculations

**Syntax**:
```sql
function() OVER (
    PARTITION BY column 
    ORDER BY column
    ROWS frame_specification
)
```

---

### Frame Specifications

**Common Frame Types**:
1. **ROWS N PRECEDING**: Current row + N previous rows
2. **ROWS UNBOUNDED PRECEDING**: All rows before current (inclusive)
3. **ROWS BETWEEN ... AND ...**: Custom range

---

### Example 1: Moving Average (3-Month)

**Scenario**: Calculate 3-month moving average of sales by product

```sql
SELECT ProductKey, 
       Year, 
       Month, 
       SalesAmount,
       AVG(SalesAmount) OVER (
           PARTITION BY ProductKey
           ORDER BY Year, Month
           ROWS 2 PRECEDING
       ) AS MovAvg
FROM Sales;
```

**Result**:
```
ProductKey | Year | Month | SalesAmount | MovAvg
-----------|------|-------|-------------|-------
P1         | 2024 | 1     | 100         | 100.00  ← Only 1 row
P1         | 2024 | 2     | 150         | 125.00  ← Avg(100,150)
P1         | 2024 | 3     | 120         | 123.33  ← Avg(100,150,120)
P1         | 2024 | 4     | 130         | 133.33  ← Avg(150,120,130)
```

**Frame**: Current row + 2 preceding rows (3 total)

**How It Works**:
1. **Partition** by ProductKey
2. **Order** by Year, Month (chronological)
3. **Average** over sliding 3-row window

---

### Example 2: Year-to-Date Sum

**Scenario**: Calculate year-to-date (YTD) sum of sales by product

```sql
SELECT ProductKey, 
       Year, 
       Month, 
       SalesAmount,
       SUM(SalesAmount) OVER (
           PARTITION BY ProductKey, Year
           ORDER BY Month
           ROWS UNBOUNDED PRECEDING
       ) AS YTD
FROM Sales;
```

**Result**:
```
ProductKey | Year | Month | SalesAmount | YTD
-----------|------|-------|-------------|-----
P1         | 2024 | 1     | 100         | 100   ← Jan only
P1         | 2024 | 2     | 150         | 250   ← Jan + Feb
P1         | 2024 | 3     | 120         | 370   ← Jan + Feb + Mar
P1         | 2024 | 4     | 130         | 500   ← Jan-Apr
P1         | 2025 | 1     | 110         | 110   ← New year resets
```

**Frame**: All rows from start of partition to current row

**How It Works**:
1. **Partition** by ProductKey AND Year (resets each year)
2. **Order** by Month
3. **Sum** all rows from start to current (cumulative)

---

### Frame Specification Options

| Specification | Description | Use Case |
|---------------|-------------|----------|
| **N PRECEDING** | Current + N before | Moving average |
| **UNBOUNDED PRECEDING** | Start to current | Running total, YTD |
| **CURRENT ROW** | Only current row | Default |
| **N FOLLOWING** | Current + N after | Forward-looking |
| **UNBOUNDED FOLLOWING** | Current to end | Reverse cumulative |

---

## Summary: SQL for Data Warehousing

### OLAP Operations
1. **ROLLUP**: Hierarchical subtotals (n+1 groupings)
2. **CUBE**: All combinations (2ⁿ groupings)
3. **GROUPING SETS**: Custom groupings (explicit control)

### Window Functions
1. **Partitioning**: Group rows, compute aggregates
2. **Ordering**: Rank and sequence within partitions
3. **Framing**: Define calculation window (moving/running)

### Key Benefits
- **No multiple scans**: Single query for multiple aggregations
- **Detail + Aggregates**: Compare individual to group in same result
- **Efficient**: Database optimizes execution

---

## Exam Tips

1. **ROLLUP vs CUBE**:
   - ROLLUP: Hierarchical (follows order)
   - CUBE: All combinations
2. **GROUPING SETS**: Most flexible, explicitly list groupings
3. **Window Partitioning**: 
   - PARTITION BY creates groups
   - Aggregate repeats for all rows in partition
4. **Window Ordering**: 
   - ORDER BY for ranking
   - RANK(), DENSE_RANK(), ROW_NUMBER()
5. **Window Framing**:
   - ROWS N PRECEDING: Moving calculations
   - ROWS UNBOUNDED PRECEDING: Running totals
6. **NULL values** in ROLLUP/CUBE indicate aggregation level
7. **Remember**: Window functions don't reduce rows (unlike GROUP BY)
8. **Frame specifications**: Know PRECEDING, FOLLOWING, UNBOUNDED
9. **YTD pattern**: PARTITION BY item, Year; ORDER BY Month; UNBOUNDED PRECEDING
10. **Moving average pattern**: ORDER BY time; ROWS N PRECEDING

### Common Exam Questions
- Write ROLLUP/CUBE queries for given scenarios
- Explain difference between ROLLUP and CUBE results
- Create window functions for ranking
- Calculate moving averages or running totals
- Identify frame specifications needed for specific calculations