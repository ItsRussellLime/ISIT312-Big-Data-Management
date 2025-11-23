# Topic 17: Hive Programming

## 1. Data Selection and Scope

### Basic SELECT Statement

**Standard Components**:
- **SELECT**: Columns to return
- **FROM**: Source table
- **WHERE**: Filter conditions
- **DISTINCT**: Remove duplicates
- **LIMIT**: Restrict number of rows

**Example**:
```sql
SELECT C_NAME, C_PHONE
FROM customer
WHERE C_ACCTBAL > 0
LIMIT 2;
```

---

### Subqueries and Common Table Expressions (CTE)

#### WITH Clause (CTE)

**Purpose**: Define temporary named result sets

**Syntax**:
```sql
WITH alias AS (
    SELECT ...
)
SELECT ...
FROM alias;
```

**Example**:
```sql
WITH cord AS (
    SELECT *
    FROM customer JOIN orders
    ON c_custkey = o_custkey
)
SELECT c_name, c_phone, o_orderkey, o_orderstatus
FROM cord;
```

**Benefits**:
- ✅ Improves readability
- ✅ Can reference multiple times
- ✅ Cleaner than nested subqueries

---

#### Nested Queries (Subqueries)

**Rules**:
- Use SELECT wherever table or scalar value expected
- **Must provide alias** for subquery result

**Example**:
```sql
SELECT c_name, c_phone, o_orderkey, o_orderstatus
FROM (
    SELECT *
    FROM customer JOIN orders
    ON c_custkey = o_custkey
) cord;  -- 'cord' is required alias
```

---

### JOIN Operations

#### Inner Join

**Execution**: Creates MapReduce jobs to process data in HDFS

**Performance Tip**: **Put large table last**
- Last table **streamed through reducers**
- Other tables **buffered in reducer**

**Example with Hint**:
```sql
SELECT /*+ STREAMTABLE(lineitem) */ c_name, o_orderkey, l_linenumber
FROM customer JOIN orders ON c_custkey = o_custkey
              JOIN lineitem ON l_orderkey = o_orderkey;
```
- `STREAMTABLE(lineitem)`: Marks lineitem as streaming table

---

#### Map Join

**Definition**: Join computed **only by map job** (no reduce phase)

**How It Works**:
1. **Small table** read into memory
2. Data **broadcasted** to all maps
3. Each row in **big table** compared with small table rows
4. **No reduce phase needed**

**Benefits**:
- ✅ Improved performance (no shuffle/reduce)
- ✅ Best for small-large table joins

**Manual Map Join**:
```sql
SELECT /*+ MAPJOIN(orders) */ c_name, c_phone, o_orderkey, o_orderstatus
FROM customer JOIN orders ON c_custkey = o_custkey;
```

**Auto Map Join**:
- Set `hive.auto.convert.join = true`
- Hive automatically converts suitable JOINs to MAPJOIN

---

#### Bucket Map Join

**Definition**: Special MAPJOIN using **bucket columns** in join condition

**Advantage**: Only fetches **required bucket data** (not whole table)

**Configuration**:
```sql
SET hive.optimize.bucketmapjoin = true;
```

**Requirement**: Both tables must be **bucketed on join key**

---

#### Left Semi Join

**Definition**: Returns left table rows that **have matches** in right table

**Restriction**: Right table **only in JOIN condition**
- Cannot use in WHERE or SELECT clauses

**Example**:
```sql
SELECT c_name, c_phone
FROM customer LEFT SEMI JOIN orders
ON c_custkey = o_custkey;
```

**Equivalent to**:
```sql
SELECT c_name, c_phone
FROM customer
WHERE c_custkey IN (SELECT o_custkey FROM orders);
```

**Use Case**: Efficiently check existence without returning right table data

---

#### Outer Joins

**Types**: LEFT, RIGHT, FULL OUTER JOIN

**Semantics**: Preserve HQL standard semantics
- Include non-matching rows with NULLs

**Example**:
```sql
SELECT c_name, o_orderkey
FROM customer LEFT OUTER JOIN orders
ON c_custkey = o_custkey;
```

---

### Set Operations

#### UNION ALL

**Supported**: Combines result sets from multiple queries

**Example**:
```sql
SELECT p_name FROM part
UNION ALL
SELECT c_name FROM customer;
```

**Note**: **UNION ALL** only (not UNION)
- No automatic duplicate removal
- All rows from both queries included

---

#### INTERSECT and MINUS

**Not Directly Supported**: Must use workarounds

**INTERSECT Workaround**: Use INNER JOIN
```sql
-- INTERSECT: Common customers and suppliers by name
SELECT c_name
FROM customer
INNER JOIN supplier ON c_name = s_name;
```

**MINUS Workaround**: Use LEFT OUTER JOIN with IS NULL
```sql
-- MINUS: Customers with no orders
SELECT c_name
FROM customer
LEFT OUTER JOIN orders ON c_custkey = o_custkey
WHERE o_orderkey IS NULL;
```

---

## 2. Data Manipulation

### LOAD Statement

**Purpose**: Load data from file system into Hive tables

---

#### Load from Local File System

**Syntax**:
```sql
LOAD DATA LOCAL INPATH '/path/to/file'
[OVERWRITE] INTO TABLE tablename
[PARTITION (partcol1=val1, ...)];
```

**Example**:
```sql
LOAD DATA LOCAL INPATH '/local/home/janusz/HIVE-EXAMPLES/TPCHR/part.txt'
OVERWRITE INTO TABLE part;
```

**Load into Partitioned Table**:
```sql
LOAD DATA LOCAL INPATH '/local/home/janusz/HIVE-EXAMPLES/TPCHR/part.txt'
OVERWRITE INTO TABLE part 
PARTITION (P_BRAND='GoldenBolts');
```

**LOCAL Keyword**: Indicates source is local file system (not HDFS)

---

#### Load from HDFS

**Default System Path**:
```sql
LOAD DATA INPATH '/user/janusz/part.txt'
OVERWRITE INTO TABLE part;
```

**Full URI**:
```sql
LOAD DATA INPATH 'hdfs://10.9.28.14:8020/user/janusz/part.txt'
OVERWRITE INTO TABLE part;
```

**Behavior**:
- If **LOCAL** not specified → Load from HDFS
- Uses full URI or `fs.default` configuration

**OVERWRITE Keyword**:
- **With OVERWRITE**: Replace existing data
- **Without OVERWRITE**: Append to existing data

---

### EXPORT and IMPORT

#### EXPORT Statement

**Purpose**: Export data and metadata for migration/backup

**Syntax**:
```sql
EXPORT TABLE tablename TO 'hdfs_path';
```

**Example**:
```sql
EXPORT TABLE part TO '/user/tpchr/part';
```

**Result in HDFS**:
```
/user/tpchr/part/_metadata           ← Metadata file
/user/tpchr/part/p_brand=GoldenBolts ← Data folder
```

**Exported Contents**:
- **Data**: All table/partition data
- **Metadata**: Schema, structure in `_metadata` file

**Use Cases**:
- Data migration between Hive instances
- Backup/restore operations
- Moving to different HDFS clusters

---

#### IMPORT Statement

**Import to Internal Table**:
```sql
IMPORT TABLE new_part FROM '/user/tpchr/part';
```
- Creates **internal table**
- Located in **default Hive warehouse** (`/user/hive/warehouse/new_part`)

**Import to External Table**:
```sql
IMPORT EXTERNAL TABLE new_extpart FROM '/user/tpchr/part';
```
- Creates **external table**
- Located in **default Hive warehouse** (`/user/hive/warehouse/new_extpart`)

---

### Sorting and Distribution

#### ORDER BY

**Purpose**: **Global sort** across all reducers

**Characteristic**:
- Uses **only ONE reducer**
- Maintains order across entire result set
- **Slower** but fully sorted

**Example**:
```sql
SELECT p_partkey, p_name
FROM part
ORDER BY p_name ASC;
```

**Use Case**: When complete ordering required

---

#### SORT BY

**Purpose**: **Local sort** within each reducer

**Characteristics**:
- Sorts data **before sending to reducer**
- Each reducer sorts its input **independently**
- **NO global sort** guarantee
- **Faster** than ORDER BY

**Example**:
```sql
SET mapred.reduce.tasks = 2;  -- Use 2 reducers

SELECT p_partkey, p_name
FROM part
SORT BY p_name ASC;
```

**Result**: Data sorted within each reducer, but not across reducers

---

#### DISTRIBUTE BY

**Purpose**: Control which reducer handles which rows

**Function**: Rows with matching values sent to **same reducer**

**Similar to**: GROUP BY (in terms of reducer distribution)

**Must Come Before**: SORT BY (if used together)

**Example**:
```sql
SELECT p_partkey, p_name
FROM part
DISTRIBUTE BY p_partkey
SORT BY p_name;
```

**Result**: 
- All rows with same p_partkey → same reducer
- Within each reducer, sorted by p_name

---

#### CLUSTER BY

**Definition**: Shorthand for **DISTRIBUTE BY + SORT BY** on **same columns**

**Syntax**:
```sql
CLUSTER BY column
```

**Equivalent to**:
```sql
DISTRIBUTE BY column SORT BY column
```

**Example**:
```sql
SELECT p_partkey, p_name
FROM part
CLUSTER BY p_name;
```

**Comparison**:
- **ORDER BY**: Global sort, one reducer
- **CLUSTER BY**: Distributes + sorts locally, multiple reducers

**Advanced Usage**: CLUSTER BY first, then ORDER BY
```sql
SELECT p_partkey, p_name
FROM part
CLUSTER BY p_name  -- Distribute + local sort
ORDER BY p_name;   -- Final global sort
```
- Utilizes all reducers for initial processing
- Final ORDER BY for complete ordering

---

### Sorting/Distribution Summary Table

| Clause | Scope | Reducers | Use Case |
|--------|-------|----------|----------|
| **ORDER BY** | Global | 1 | Complete ordering needed |
| **SORT BY** | Local per reducer | Multiple | Faster, local ordering sufficient |
| **DISTRIBUTE BY** | Controls distribution | Multiple | Ensure related rows same reducer |
| **CLUSTER BY** | Distribute + sort | Multiple | Shorthand for DISTRIBUTE BY + SORT BY on same column |

---

## 3. Data Aggregation and Sampling

### Basic Aggregation

**GROUP BY with Aggregation Functions**:

**Example**:
```sql
SELECT p_type, COUNT(*)
FROM part
GROUP BY p_type;
```

**collect_set Function**: Aggregate into sets
```sql
SELECT p_type, collect_set(p_name), COUNT(*)
FROM part
GROUP BY p_type;
```
- Returns **array of unique values**

---

### Advanced Aggregation

#### GROUPING SETS

**Purpose**: Multiple GROUP BY operations on same data

**Example**:
```sql
SELECT p_type, p_name, COUNT(*)
FROM part
GROUP BY p_type, p_name
GROUPING SETS ((p_type), (p_name));
```

**Result**: Aggregates by p_type AND by p_name separately

---

#### ROLLUP

**Purpose**: Calculate **hierarchical aggregations**

**Syntax**:
```sql
GROUP BY p_type, p_name WITH ROLLUP;
```

**Equivalent to**:
```sql
GROUPING SETS (
    (p_type, p_name),  -- Detail
    (p_type),          -- Subtotal by type
    ()                 -- Grand total
)
```

---

#### CUBE

**Purpose**: **All possible subsets** of attributes

**Syntax**:
```sql
GROUP BY p_type, p_name WITH CUBE;
```

**Equivalent to**:
```sql
GROUPING SETS (
    (p_type, p_name),  -- Both
    (p_type),          -- Type only
    (p_name),          -- Name only
    ()                 -- Grand total
)
```

---

#### GROUPING__ID Function

**Purpose**: Distinguish aggregation levels

**Example**:
```sql
SELECT GROUPING__ID, p_type, p_name, COUNT(*)
FROM part
GROUP BY p_type, p_name WITH CUBE
ORDER BY GROUPING__ID;
```

**Result**: Different GROUPING__ID for each aggregation level

---

#### HAVING Clause

**Purpose**: Filter GROUP BY results

**Example**:
```sql
SELECT GROUPING__ID, p_type, p_name, COUNT(*)
FROM part
GROUP BY p_type, p_name WITH CUBE
HAVING COUNT(*) > 1
ORDER BY GROUPING__ID;
```

---

### Analytic Functions (Window Functions)

**General Syntax**:
```sql
function(arg1, ..., argn)
OVER (
    [PARTITION BY <...>]
    [ORDER BY <...>]
    [window_frame]
)
```

---

#### Standard Aggregations as Analytic Functions

**Example**:
```sql
SELECT p_name,
       COUNT(*) OVER (PARTITION BY p_name)
FROM part;
```

---

#### Ranking Functions

**Example**:
```sql
SELECT l_orderkey, l_partkey, l_quantity,
       RANK() OVER (ORDER BY l_quantity),
       DENSE_RANK() OVER (ORDER BY l_quantity)
FROM lineitem;
```

**With PARTITION**:
```sql
SELECT l_orderkey, l_partkey, l_quantity,
       RANK() OVER (PARTITION BY l_orderkey ORDER BY l_quantity),
       DENSE_RANK() OVER (PARTITION BY l_orderkey ORDER BY l_quantity)
FROM lineitem;
```

---

#### Value Functions

**FIRST_VALUE and LAST_VALUE**:
```sql
SELECT l_orderkey, l_partkey, l_quantity,
       FIRST_VALUE(l_quantity) OVER (PARTITION BY l_orderkey ORDER BY l_quantity),
       LAST_VALUE(l_quantity) OVER (PARTITION BY l_orderkey ORDER BY l_quantity)
FROM lineitem;
```

---

#### Window Frames

**Example - Preceding Rows**:
```sql
SELECT l_orderkey, l_partkey, l_quantity,
       MAX(l_quantity) OVER (
           PARTITION BY l_orderkey 
           ORDER BY l_partkey
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       )
FROM lineitem;
```

**Example - Preceding and Following**:
```sql
SELECT l_orderkey, l_partkey, l_quantity,
       MAX(l_quantity) OVER (
           PARTITION BY l_orderkey 
           ORDER BY l_partkey
           ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
       )
FROM lineitem;
```

---

### Sampling

**Purpose**: Work with subset of data for faster analysis

---

#### Random Sampling

**Using RAND() and LIMIT**:
```sql
SELECT *
FROM lineitem 
DISTRIBUTE BY RAND() 
SORT BY RAND() 
LIMIT 5;
```
- **DISTRIBUTE BY RAND()**: Random distribution to reducers
- **SORT BY RAND()**: Random order
- **LIMIT 5**: Take 5 rows

---

#### Bucket Table Sampling

**Optimized for bucketed tables**:
```sql
SELECT *
FROM customer 
TABLESAMPLE(BUCKET 3 OUT OF 8 ON rand());
```
- Sample bucket 3 out of 8 buckets
- More efficient than full table scan

---

#### Block Sampling

**By Number of Rows**:
```sql
SELECT * FROM lineitem TABLESAMPLE(4 ROWS);
```

**By Percentage**:
```sql
SELECT * FROM lineitem TABLESAMPLE(50 PERCENT);
```

**By Byte Size**:
```sql
SELECT * FROM lineitem TABLESAMPLE(20B);
```

---

## Summary: Key Hive Programming Concepts

### Joins
- **INNER JOIN**: Standard join, put large table last
- **MAP JOIN**: No reduce phase, for small-large joins
- **BUCKET MAP JOIN**: Optimized for bucketed tables
- **LEFT SEMI JOIN**: Existence check, right table in condition only
- **OUTER JOIN**: LEFT, RIGHT, FULL with NULLs

### Sorting/Distribution
- **ORDER BY**: Global sort, 1 reducer
- **SORT BY**: Local sort per reducer
- **DISTRIBUTE BY**: Control reducer distribution
- **CLUSTER BY**: DISTRIBUTE + SORT on same column

### Aggregation
- **GROUPING SETS**: Custom aggregation combinations
- **ROLLUP**: Hierarchical aggregations
- **CUBE**: All possible combinations
- **Analytic Functions**: Window-based calculations

### Data Loading
- **LOAD**: From local or HDFS
- **EXPORT/IMPORT**: Migration and backup
- **LOCAL** keyword: Determines source location

---

## Exam Tips

1. **Map Join**: Know when to use (small-large table joins)
2. **ORDER BY vs SORT BY**: Global vs local sorting
3. **CLUSTER BY** = DISTRIBUTE BY + SORT BY (same column)
4. **LEFT SEMI JOIN**: Right table only in condition
5. **ROLLUP vs CUBE**: Hierarchical vs all combinations
6. **Windowing**: PARTITION BY, ORDER BY, ROWS/RANGE
7. **LOAD**: Understand LOCAL keyword and OVERWRITE
8. **EXPORT/IMPORT**: Know metadata file creation
9. **Sampling methods**: Random, bucket, block
10. **Performance**: Large table last in joins, map joins for efficiency