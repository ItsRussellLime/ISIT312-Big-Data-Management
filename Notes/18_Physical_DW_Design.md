# Topic 18: Physical Data Warehouse Design

## 1. Overview of Physical Design Techniques

### Three Main Techniques

1. **Materialized Views**: Physically stored views
2. **Indexing**: Efficient data access structures
3. **Partitioning**: Dividing tables into smaller files

---

## 2. Materialized Views

### Definition

**Materialized View**: Relational table that contains rows returned by a view definition (SELECT statement)

**Concept**:
- **Regular views**: Stored queries
- **Materialized views**: Stored results

---

### Purpose

**Primary Goal**: Reduce computation time for SELECT statements

**Example Use Case**:
- **Join materialized views**: Eliminate need to join tables repeatedly
- Pre-compute expensive aggregations

---

### Two Access Methods

#### 1. Brute Force Method

**Definition**: SQL explicitly accesses the materialized view

**Example**:
```sql
SELECT * 
FROM MV_ORDERS 
WHERE O_ORDERDATE = TO_DATE('01-JAN-1992','DD-MON-YYYY');
```
- Directly query the materialized view table

---

#### 2. Transparent Query Rewrite

**Definition**: Query optimizer automatically detects when to use materialized view

**How It Works**:
- User writes query against **base tables**
- Optimizer recognizes materialized view can satisfy query
- Automatically **rewrites query** to use materialized view

**Example - User Query**:
```sql
SELECT O_ORDERKEY, O_CUSTKEY, O_TOTALPRICE, O_ORDERDATE 
FROM ORDERS
WHERE O_ORDERDATE > TO_DATE('31-DEC-1986','DD-MON-YYYY');
```

**Optimizer Rewrites To**:
```sql
-- Internally uses MV_ORDERS instead of ORDERS
SELECT * FROM MV_ORDERS WHERE ...
```

**Query Plan Shows**:
```
MAT_VIEW REWRITE ACCESS FULL | MV_ORDERS
```

**Advantage**: 
- ✅ Users don't need to know materialized views exist
- ✅ Optimizer handles optimization automatically

---

### Creating Materialized Views

**Syntax**:
```sql
CREATE MATERIALIZED VIEW view_name
REFRESH [ON COMMIT | ON DEMAND]
ENABLE QUERY REWRITE
AS
SELECT ...
FROM ...
WHERE ...;
```

**Example**:
```sql
CREATE MATERIALIZED VIEW MV_ORDERS
REFRESH ON COMMIT
ENABLE QUERY REWRITE
AS (
    SELECT O_ORDERKEY, O_CUSTKEY, O_TOTALPRICE, O_ORDERDATE 
    FROM ORDERS
    WHERE O_ORDERDATE > TO_DATE('31-DEC-1986','DD-MON-YYYY')
);
```

**Key Clauses**:
- **REFRESH ON COMMIT**: Update when base table commits
- **ENABLE QUERY REWRITE**: Allow optimizer to use this view

---

### View Maintenance

**Definition**: Keeping materialized view synchronized with base tables

**Challenge**: When base tables are updated, materialized view must be updated

**Two Maintenance Strategies**:

#### 1. Full Refresh
- Recompute from entire base tables
- Slower but guaranteed correct

#### 2. Incremental View Maintenance
- Compute from **individual modifications** only
- Update view based on changes (inserts, updates, deletes)
- **More efficient** for large tables

**Example**:
- Base table: 1 million rows, 10 updated
- Incremental: Process only 10 changes
- Full: Reprocess all 1 million rows

---

### Materialized View Benefits

**Performance**:
- ✅ Pre-computed results → Faster queries
- ✅ Reduced CPU and I/O
- ✅ Especially beneficial for complex joins and aggregations

**Use Cases**:
- Frequently accessed summary data
- Complex multi-table joins
- Time-consuming aggregations
- Reports requiring pre-computed metrics

---

## 3. Indexes for Data Warehouses

### Purpose

**Index**: Quick way to locate data of interest

**Without Index**: Full table scan required

**With Index**: Direct access to relevant rows

---

### Example Scenario

**Query**:
```sql
SELECT *
FROM EMPLOYEE
WHERE EmployeeKey = 007;
```

**With Index on EmployeeKey**:
- **Single disk block access** to find row
- Fast lookup

**Without Index**:
- **Complete table scan** required
- Slow for large tables

---

### Index Trade-offs

**Drawback**: 
- Almost every **update on indexed attribute** requires **index update**
- Too many indexes → **Degraded performance** on writes

**Balance**: 
- Read performance vs. write performance
- Data warehouses: Usually **read-heavy**, so more indexes acceptable

---

### Common Indexing Techniques

1. **B*-tree (B+ tree)**: Standard relational database index
2. **Bitmap Index**: Specialized for data warehouses

---

## 4. B*-Tree Indexes

### Structure

**Tree Structure**:
- **Root node** at top
- **Internal nodes** in middle
- **Leaf nodes** at bottom (contain data pointers)

### Traversal Methods

1. **Vertical**: Root → Leaf level
2. **Horizontal**: Left to right (or reverse) at leaf level
3. **Combined**: Vertical then horizontal

**Use Case**: Good for high-cardinality columns (many distinct values)

---

## 5. Bitmap Indexes

### Concept

**Bitmap Index**: Uses bit vectors to represent data

**Structure**:
- One **bit vector** per distinct value
- Each bit represents one row
- **1** = row has that value
- **0** = row does not have that value

---

### Example: Product Table

**Table**:
```
RowID | PiecesPerUnit | UnitPrice
------|---------------|----------
1     | 50            | 150
2     | 60            | 120
3     | 40            | 180
4     | 50            | 110
```

**Bitmap Index on PiecesPerUnit**:
```
Value 40: [0, 0, 1, 0]  ← Row 3 has value 40
Value 50: [1, 0, 0, 1]  ← Rows 1,4 have value 50
Value 60: [0, 1, 0, 0]  ← Row 2 has value 60
```

---

### Query Using Bitmap Indexes

**Query**: Products with 45-55 pieces per unit AND price 100-200

**Step 1**: Get bitmap for PiecesPerUnit between 45-55
```
Value 50: [1, 0, 0, 1]  ← Matches
```

**Step 2**: Get bitmap for UnitPrice between 100-200
```
Prices 100-200: [1, 1, 0, 1]
```

**Step 3**: AND operation (bitwise)
```
[1, 0, 0, 1] AND [1, 1, 0, 1] = [1, 0, 0, 1]
```

**Result**: Rows 1 and 4 satisfy both conditions

---

### Bitmap Index Advantages

**For Data Warehouses**:
- ✅ Excellent for **low-cardinality** columns (few distinct values)
- ✅ Efficient **bitwise operations** (AND, OR, NOT)
- ✅ **Space-efficient** for low-cardinality
- ✅ Fast for **complex queries** with multiple conditions

**Best For**:
- Gender (M/F)
- Status (Active/Inactive)
- Categories (few types)
- Boolean flags

---

### Bitmap vs B*-Tree

| Aspect | Bitmap Index | B*-Tree Index |
|--------|--------------|---------------|
| **Best for** | Low cardinality | High cardinality |
| **Space** | Efficient (low card.) | More space |
| **Complex queries** | Excellent (bitwise ops) | Good |
| **Updates** | Expensive | Less expensive |
| **Use case** | Data warehouses (read-heavy) | OLTP (write-heavy) |

---

## 6. Index Requirements for Data Warehouses

### Four Key Requirements

#### 1. Symmetric Partial Match Queries

**Definition**: All dimensions should be **symmetrically indexed**

**Reason**: Dimensions can be searched **simultaneously**

**Example**: Search by Product AND Customer AND Time equally efficiently

---

#### 2. Indexing at Multiple Aggregation Levels

**Definition**: **Summary tables** must be indexed same way as base tables

**Reason**: Queries at different granularities need efficient access

**Example**:
- Daily sales table indexed
- Monthly summary table also indexed

---

#### 3. Efficient Batch Update

**Definition**: Consider data warehouse **refreshing time**

**Reason**: DW typically updated in batch (nightly, weekly)

**Strategy**: 
- Balance index benefits vs. update overhead
- May disable indexes during load, rebuild after

---

#### 4. Sparse Data Handling

**Definition**: Index schema must handle **sparse and non-sparse data** efficiently

**Fact**: Typically only **20% of data cube cells are non-empty**

**Challenge**: Don't waste space on empty cells

**Solution**: Bitmap indexes naturally handle sparsity well

---

## 7. Star Queries

### Definition

**Star Query**: Query over **star schema** joining fact table with dimension tables

---

### Typical Star Query Structure

**Example**: Total sales of discontinued products by customer and product name

```sql
SELECT ProductName, CustomerName, SUM(SalesAmount)
FROM Sales S, Customer C, Product P
WHERE S.CustomerKey = C.CustomerKey 
  AND S.ProductKey = P.ProductKey 
  AND P.Discontinued = 'Yes'
GROUP BY C.CustomerName, P.ProductName;
```

---

### Three Evaluation Steps

1. **Join condition evaluation**: Connect fact to dimensions
2. **Selection condition evaluation**: Filter dimensions (WHERE clause)
3. **Aggregation**: Group and compute measures

---

## 8. Evaluating Star Queries with Bitmap Indexes

### Example Scenario

**Query**: Find sales for discontinued products

**Available Indexes**:
- **B+-tree** on CustomerKey and ProductKey in Sales
- **Bitmap indexes** on foreign keys in Sales
- **Bitmap index** on Discontinued in Product

---

### Evaluation Steps

**Step 1**: Filter Product dimension
```
Discontinued = 'Yes' → ProductKey values: p2, p4, p6
```

**Step 2**: Join Product with Sales
- Access **bitmap vectors** in Sales labeled p2, p4, p6
- Result: p2 and p4 have fact records; p6 doesn't

**Step 3**: Extract CustomerKey values
- From matching fact records
- Result: c2, c3

**Step 4**: Get names using B+-tree
- Use ProductKey and CustomerKey indexes
- Retrieve customer and product names

**Step 5**: Aggregate
```
Result: (cust2, prod2, 200), (cust3, prod4, 100)
```

---

### Benefits of Bitmap Indexes for Star Queries

- ✅ **Fast filtering** on dimension attributes
- ✅ **Efficient joins** using bitmap operations
- ✅ **Reduced I/O**: Only access relevant data
- ✅ **Parallel processing**: Bitwise operations highly parallelizable

---

## 9. Data Warehouse Partitioning

### Definition

**Partitioning (Fragmentation)**: Divides table into **smaller datasets** (partitions)

**Applied to**: Tables and indexes

---

### Types of Partitioning

#### 1. Vertical Partitioning

**Definition**: Splits **attributes** into groups stored independently

**Example**:
```
Original: Employee (ID, Name, Address, Salary, Phone, Email)
    ↓
Partition 1: Employee_Basic (ID, Name, Salary)
Partition 2: Employee_Contact (ID, Address, Phone, Email)
```

**Use Case**: 
- Most frequently used attributes in one partition
- Less frequently used in another

**Benefit**: 
- ✅ More records fit in memory
- ✅ Reduced processing time for common queries

---

#### 2. Horizontal Partitioning

**Definition**: Divides table into **smaller tables** with **same structure**

**Example**:
```
Sales table partitioned by year:
- Sales_2022
- Sales_2023
- Sales_2024
```

**Use Case**:
- Queries needing **recent data** only
- Time-based access patterns

**Benefit**:
- ✅ Query only relevant partition
- ✅ Faster access to subset

---

## 10. Query Optimization with Partitioning

### Partition Pruning

**Definition**: Access only **relevant partitions** for a query

**Example**:
- Sales table **partitioned by month**
- Query requests **single month**
- Only **one partition** accessed (not all 12)

**Performance Gain**: 
- 12× reduction in data scanned
- Proportional speed improvement

---

### Join Optimization

**Two Scenarios for Enhanced Joins**:

#### 1. Co-partitioning
- Both tables **partitioned on join attribute**
- Example: Sales and Orders partitioned by CustomerKey

#### 2. Reference Table Partitioning
- Reference table **partitioned on primary key**
- Large join broken into **smaller joins**

**Benefit**: Parallel processing of smaller joins

---

## 11. Partitioning Strategies

### 1. Range Partitioning

**Definition**: Map records based on **value ranges**

**Syntax**:
```sql
PARTITION BY RANGE (date_column)
(
    PARTITION p_jan VALUES LESS THAN ('2024-02-01'),
    PARTITION p_feb VALUES LESS THAN ('2024-03-01'),
    ...
)
```

**Natural Candidate**: **Time dimension**

**Example**:
- January-2012 partition: January 1-31, 2012
- February-2012 partition: February 1-29, 2012

**Use Case**: Time-series data, sequential access patterns

---

### 2. Hash Partitioning

**Definition**: Use **hashing algorithm** on partitioning key

**Goal**: Distribute rows **uniformly** across partitions

**Benefit**: Ideally, partitions of **equal size**

**Use Case**:
- Data **not time-based**
- Distribute across **multiple devices**
- Load balancing

**Example**:
```
hash(CustomerKey) mod 4 → Partition 0, 1, 2, or 3
```

---

### 3. List Partitioning

**Definition**: Specify **explicit list of values** for each partition

**Example**:
```sql
PARTITION BY LIST (region)
(
    PARTITION p_north VALUES ('NY', 'MA', 'CT'),
    PARTITION p_south VALUES ('FL', 'TX', 'GA'),
    PARTITION p_west VALUES ('CA', 'OR', 'WA')
)
```

**Use Case**: 
- Categorical data
- Business-defined groupings

---

### 4. Composite Partitioning

**Definition**: Combine multiple partitioning methods

**Example**: Range + Hash
```
First: Range partition by year
Then: Hash partition each year's data
```

**Benefit**: Combine advantages of multiple strategies

**Support**: Some vendors (e.g., Oracle)

---

## 12. Partitioning Strategy Comparison

| Strategy | Basis | Use Case | Example |
|----------|-------|----------|---------|
| **Range** | Value ranges | Time-series, sequential | Sales by month |
| **Hash** | Hash function | Uniform distribution | Load balancing |
| **List** | Explicit values | Categorical | Sales by region |
| **Composite** | Combination | Complex requirements | Range + Hash |

---

## Summary: Physical DW Design Techniques

### Materialized Views
- **Store query results** for fast access
- **Two access methods**: Brute force, transparent rewrite
- **Maintenance**: Incremental preferred for efficiency

### Indexing
- **B*-tree**: High cardinality, standard RDBMS
- **Bitmap**: Low cardinality, data warehouses
- **Requirements**: Symmetric, multi-level, batch-friendly, sparse-aware

### Partitioning
- **Vertical**: Split columns
- **Horizontal**: Split rows
- **Strategies**: Range, Hash, List, Composite
- **Optimization**: Partition pruning, join enhancement

---

## Exam Tips

1. **Materialized Views**:
   - Know two access methods
   - Incremental maintenance more efficient
   - ENABLE QUERY REWRITE for transparency
2. **Bitmap Indexes**:
   - Best for **low-cardinality** columns
   - Efficient **bitwise operations** (AND, OR)
   - Space-efficient for sparse data
3. **B*-tree vs Bitmap**:
   - B*-tree: High cardinality, OLTP
   - Bitmap: Low cardinality, data warehouses
4. **Star Query Evaluation**:
   - Three steps: Join, Filter, Aggregate
   - Bitmap indexes optimize all steps
5. **Partitioning Types**:
   - Vertical: Split columns
   - Horizontal: Split rows (same structure)
6. **Partitioning Strategies**:
   - Range: Time-series
   - Hash: Uniform distribution
   - List: Explicit categorical
7. **Partition Pruning**: Access only relevant partitions
8. **Index Requirements**: Symmetric, multi-level, batch-efficient, sparse-aware
9. **Performance Trade-off**: Indexes speed reads, slow writes
10. **Composite Partitioning**: Combine strategies for complex needs

### Common Exam Scenarios
- When to use bitmap vs B*-tree index
- Design partitioning strategy for given scenario
- Explain star query evaluation with bitmap indexes
- Calculate partition pruning benefits
- Describe materialized view maintenance strategies