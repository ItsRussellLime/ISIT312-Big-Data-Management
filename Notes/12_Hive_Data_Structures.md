# Topic 12: Hive Data Structures

## 1. Primitive Data Types

### Numeric Types
| Type | Size | Example | Description |
|------|------|---------|-------------|
| **TINYINT** | 1 byte | `10Y` | Smallest integer |
| **SMALLINT** | 2 bytes | `10S` | Small integer |
| **INT** | 4 bytes | `10` | Standard integer |
| **BIGINT** | 8 bytes | `10L` | Large integer |
| **FLOAT** | 4 bytes | `0.1234567` | Single precision |
| **DOUBLE** | 8 bytes | `0.1234567891234` | Double precision |
| **DECIMAL** | (m,n) | `3.14` | Fixed precision decimal |

### Other Primitive Types
| Type | Size/Format | Example | Description |
|------|-------------|---------|-------------|
| **BINARY** | n bytes | `1011001` | Binary data |
| **BOOLEAN** | 1 byte | `TRUE` | Boolean value |
| **STRING** | Up to 2GB | `'Abcdef'` | Variable-length string |
| **CHAR** | 255 bytes | `'Hello'` | Fixed-length string |
| **VARCHAR** | 1 byte | `'Hive'` | Variable-length string |
| **DATE** | YYYY-MM-DD | `'2017-05-03'` | Date only |
| **TIMESTAMP** | YYYY-MM-DD HH:MM:SS[.f...] | `'2017-05-03 15:10:00.345'` | Date and time |

### Key Points
- Use **suffix notation** for numeric types (Y, S, L)
- **STRING** can hold up to 2GB of data
- **DATE** and **TIMESTAMP** use specific formats

---

## 2. Complex Data Types

### ARRAY Type
**Definition**: List of values of the same type

```sql
-- Declaration
array_col ARRAY<string>

-- Example
['Hadoop', 'Pig', 'Hive']

-- Access
bigdata[1]  -- Returns 'Pig' (0-indexed)
```

### MAP Type
**Definition**: Set of key-value pairs

```sql
-- Declaration
map_col MAP<int, string>

-- Example
{'k1':'Hadoop', 'k2':'Pig'}

-- Access
bigdata['k2']  -- Returns 'Pig'
```

### STRUCT Type
**Definition**: User-defined structure with named fields of any type

```sql
-- Declaration
struct_col STRUCT<a:string, b:int, c:double>

-- Example
{name:'Hadoop', age:24, salary:50000.06}

-- Access
bigdata.name  -- Returns 'Hadoop'
```

### Creating Tables with Complex Types

```sql
-- Create table with complex data types
CREATE TABLE types(
   array_col ARRAY<string>,
   map_col MAP<int, string>,
   struct_col STRUCT<a:string, b:int, c:double>
);

-- Insert data into complex types
INSERT INTO types
   SELECT array('bolt', 'nut', 'screw'),
          map(1, 'bolt', 2, 'nut', 3, 'screw'),
          named_struct('a', 'bolt', 'b', 5, 'c', 0.5)
   FROM DUAL;
```

### Key Concepts
- **ARRAY**: Indexed access with `[index]` (0-based)
- **MAP**: Key-based access with `['key']`
- **STRUCT**: Dot notation access with `.fieldname`
- Use **named_struct()** function to create STRUCT values

---

## 3. Databases

### Definition
- **Database**: Collection of conceptually related tables
- Implements a **conceptual schema**
- Stored as a **folder/directory in HDFS**

### Storage Location
- **Default database**: `/user/hive/warehouse`
- **Custom databases**: `/user/hive/warehouse/<dbname>.db`
- **Example**: Database `tpchr` → `/user/hive/warehouse/tpchr.db`

### Database Operations

```sql
-- Create database
CREATE DATABASE tpchr;

-- Describe database (metadata)
DESCRIBE DATABASE tpchr;

-- Make database current (no need to prefix table names)
USE tpchr;

-- Drop database
DROP DATABASE tpchr;
```

### Key Points
- Databases organize related tables
- Each database has its own folder in HDFS
- **USE** command sets the current database context
- Tables in current database don't need database prefix

---

## 4. Tables

### Types of Tables

#### Internal Tables (Managed Tables)
- **Created and managed by Hive** in HDFS
- Hive **fully manages lifecycle** (add/delete data, create/drop table)
- When table is **dropped**, both **metadata and data** are deleted
- Data stored in **default warehouse directory**

#### External Tables
- **Data already exists** in HDFS
- Hive provides **tabular view** of existing data
- **LOCATION** property specifies data location in HDFS
- When table is **dropped**, only **metadata** is removed; **data remains** in HDFS
- **Use case**: Share data between multiple tools/applications

### Creating Internal Tables

```sql
-- Create internal table
CREATE TABLE IF NOT EXISTS intregion(
   R_REGIONKEY DECIMAL(12),
   R_NAME VARCHAR(25),
   R_COMMENT VARCHAR(152)
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;

-- Load data into internal table
LOAD DATA LOCAL INPATH 'region.tbl' INTO TABLE intregion;
```

### Creating External Tables

```sql
-- Create external table
CREATE EXTERNAL TABLE IF NOT EXISTS extregion(
   R_REGIONKEY DECIMAL(12),
   R_NAME VARCHAR(25),
   R_COMMENT VARCHAR(152)
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE 
LOCATION '/user/tpchr/region';

-- Load data into external table
LOAD DATA LOCAL INPATH 'region.tbl' INTO TABLE extregion;
```

### Creating External Table Over Existing HDFS File

```bash
# First, put file in HDFS
hadoop fs -mkdir /user/tpchr/nation
hadoop fs -put nation.tbl /user/tpchr/nation
hadoop fs -ls /user/tpchr/nation
```

```sql
-- Create external table over existing file
CREATE EXTERNAL TABLE IF NOT EXISTS extnation(
   N_NATIONKEY DECIMAL(12),
   N_NAME VARCHAR(25),
   N_COMMENT VARCHAR(152)
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE 
LOCATION '/user/tpchr/nation';
```

### Table Creation Components
- **ROW FORMAT DELIMITED**: Specifies row formatting
- **FIELDS TERMINATED BY**: Column delimiter (e.g., '|', ',', '\t')
- **STORED AS TEXTFILE**: File format (TEXTFILE, SEQUENCEFILE, ORC, PARQUET)
- **LOCATION**: HDFS path for external tables

### Key Differences: Internal vs External

| Aspect | Internal Table | External Table |
|--------|----------------|----------------|
| **Data Management** | Hive manages | User manages |
| **Location** | Default warehouse | User-specified LOCATION |
| **DROP Behavior** | Deletes metadata + data | Deletes metadata only |
| **Use Case** | Hive-only data | Shared data across tools |

---

## 5. Partitions

### Purpose
- **Eliminate unnecessary scans** of entire table
- Access only **required fragments** of data
- Improve **query performance**

### How Partitions Work
- Partition corresponds to **predefined columns**
- Stored as **subfolder in HDFS**
- Only **required partitions** are accessed during queries

### Creating Partitioned Table

```sql
-- Create partitioned table
CREATE TABLE IF NOT EXISTS part(
   P_PARTKEY DECIMAL(12),
   P_NAME VARCHAR(55),
   P_TYPE VARCHAR(25),
   P_SIZE DECIMAL(12),
   P_COMMENT VARCHAR(23)
)
PARTITIONED BY (P_BRAND VARCHAR(20))
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;
```

### Managing Partitions

```sql
-- Add partition (must be done before loading data)
ALTER TABLE part ADD PARTITION (P_BRAND='GoldenBolts');

-- List partitions
SHOW PARTITIONS part;
-- Output: p_brand=GoldenBolts

-- Load data into partition
LOAD DATA LOCAL INPATH '/local/home/janusz/HIVE-EXAMPLES/TPCHR/part.txt'
OVERWRITE INTO TABLE part 
PARTITION (P_BRAND='GoldenBolts');

-- Check partition in HDFS
hadoop fs -ls /user/hive/warehouse/part
-- Shows: drwxrwxr-x - janusz supergroup 0 2017-07-01
```

### Partition Storage Structure
```
/user/hive/warehouse/part/
    ├── p_brand=GoldenBolts/
    │   └── data_file
    ├── p_brand=SilverBolts/
    │   └── data_file
```

### Key Partition Concepts
- **PARTITIONED BY** clause defines partition columns
- Partitions must be **added before loading data**
- Each partition stored as **separate subfolder**
- Partition columns **not stored in data files** themselves
- **Significant performance benefit** for queries filtering on partition columns

---

## 6. Buckets

### Purpose
- **Speed up processing** of large tables
- Distribute data across **fixed number of files**
- Enable **efficient sampling and joins**

### How Buckets Work
- Bucket corresponds to **segment of file in HDFS**
- Values in bucket column are **hashed** into buckets
- Number of buckets is **user-defined**

### Creating Bucketed Table

```sql
-- Create table with buckets
CREATE TABLE customer(
   C_CUSTKEY DECIMAL(12),
   C_NAME VARCHAR(25),
   C_PHONE CHAR(15),
   C_ACCTBAL DECIMAL(12,2)
)
CLUSTERED BY (C_CUSTKEY) INTO 2 BUCKETS
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|';

-- Set MapReduce and Hive parameters
SET map.reduce.tasks = 2;
SET hive.enforce.bucketing = true;
```

### Inserting Data into Bucketed Tables

```sql
-- Insert data (each row goes to appropriate bucket)
INSERT INTO customer VALUES(1, 'Customer#000000001', '25-989-741-2988', 711.56);
INSERT INTO customer VALUES(2, 'Customer#000000002', '23-768-687-3665', 121.65);
INSERT INTO customer VALUES(3, 'Customer#000000003', '11-719-748-3364', 7498.12);
INSERT INTO customer VALUES(4, 'Customer#000000004', '14-128-190-5944', 2866.83);
INSERT INTO customer VALUES(5, 'Customer#000000005', '13-750-942-6364', 794.47);
```

### Bucketing Configuration
- **map.reduce.tasks**: Number of reducers (should match buckets)
- **hive.enforce.bucketing**: Ensures proper bucket distribution

### Key Bucketing Concepts
- **CLUSTERED BY** clause defines bucket column
- **INTO n BUCKETS** specifies number of buckets
- Hashing function determines which bucket for each row
- **Benefits**:
  - Faster **map-side joins**
  - Efficient **sampling**
  - Better **query performance** for bucketed columns

### Partitions vs Buckets

| Aspect | Partitions | Buckets |
|--------|-----------|---------|
| **Structure** | Separate subfolders | Separate files in same folder |
| **Basis** | Column values | Hash of column values |
| **Number** | Variable (one per value) | Fixed (user-defined) |
| **Use Case** | Filter queries | Joins and sampling |
| **Storage** | Subfolder per partition | Multiple files per table/partition |

---

## 7. Views

### Definition
- **Logical data structures** that simplify queries
- **Do not store data** or get materialized
- Virtual tables based on SELECT query

### View Characteristics
- **Frozen definition**: Schema fixed at creation time
- **No automatic updates**: Changes in underlying tables not reflected
- **Simplify complex queries**: Reusable query logic
- **No performance benefit**: Views are not materialized

### Creating Views

```sql
-- Create view
CREATE VIEW vcustomer AS
   SELECT C_CUSTKEY, C_NAME, C_PHONE
   FROM CUSTOMER
   WHERE C_CUSTKEY < 5;

-- Use view like a table
SELECT * FROM vcustomer;
```

### Key View Concepts
- Views provide **logical abstraction** over tables
- **Definition frozen** at creation time
- Useful for:
  - **Simplifying complex queries**
  - **Hiding complexity** from users
  - **Security**: Limit access to specific columns/rows
- **No data stored**: View is a saved query definition

### Important Limitation
- If underlying table schema changes, **view schema does NOT update**
- Need to **DROP and RECREATE view** to reflect changes

---

## Summary: Hive Data Structures Hierarchy

```
Database (Folder in HDFS)
└── Tables (Internal or External)
    ├── Partitions (Subfolders)
    │   └── Buckets (Files)
    └── Views (Logical, no storage)
```

### Data Type Categories
1. **Primitive**: TINYINT, INT, BIGINT, FLOAT, DOUBLE, STRING, DATE, TIMESTAMP, etc.
2. **Complex**: ARRAY, MAP, STRUCT

### Storage Optimization Techniques
1. **Partitions**: Divide table by column values → subfolders
2. **Buckets**: Divide table by hash → multiple files
3. **Both**: Partition first, then bucket within partitions

### Table Management Strategy
- Use **Internal Tables** for Hive-managed data
- Use **External Tables** for shared data or when data should persist after DROP
- Use **Partitions** for large tables with time/category filters
- Use **Buckets** for join optimization and sampling
- Use **Views** to simplify complex query logic

---

## Exam Tips
1. Know **all primitive data types** and their sizes
2. Understand **complex types** (ARRAY, MAP, STRUCT) and access patterns
3. **Internal vs External tables**: Memorize key differences
4. **Partitions vs Buckets**: Know when to use each
5. Remember partition **must be added before loading data**
6. Know **ROW FORMAT** and **STORED AS** clauses
7. Views are **logical only** (not materialized)
8. Understand **HDFS storage structure** for databases, tables, partitions