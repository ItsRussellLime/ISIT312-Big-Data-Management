# Topic 10: HBase Data Model and Operations

## 1. HBase Overview

### What is HBase?
- **Open-source distributed database** based on Google's BigTable
- Provides **BigTable view** of data stored in HDFS
- Also called **Hadoop Database**
- **NoSQL database** - very different from relational model

### Data Model Characteristics
- **Sparse**: Not all columns need values
- **Distributed**: Across cluster nodes
- **Persistent**: Stored in HDFS
- **Multidimensional**: Multiple dimensions per cell
- **Sorted map**: Indexed by row key, column key, timestamp

### Key Features
- **Column-oriented** storage
- **Versioned** data (timestamps)
- **Horizontally scalable**
- **Strong consistency** (not eventual)
- **Random read/write** access (unlike HDFS)

## 2. Logical View of HBase Table

### Core Components

#### 1. Row Key
- **Uniquely identifies** each row
- **Always sorted** lexicographically
- Stored as **byte array** (no data type)
- **Primary index** - only indexed field
- **Design critical** for performance

#### 2. Column Family
- **Groups related columns** together
- Defined at **table creation time**
- **Important impact** on physical implementation
- All rows have **same column families** (can be empty)
- Stored together on disk

#### 3. Column Qualifier (Column Name)
- **Specific column** within column family
- Syntax: `family:qualifier`
- **Dynamic**: Can be added at write time
- No need to define in advance
- Can represent data itself

#### 4. Cell
- **Intersection** of row, column family, and column qualifier
- Identified by: `(row key, column family, qualifier, timestamp)`
- Contains **value** (byte array)

#### 5. Value
- **Data stored** in cell
- **No data type** - always byte array
- Application interprets type

#### 6. Timestamp
- **Version number** for cell value
- Default: **timestamp when written**
- **Multiple versions** can exist
- Configurable max versions per column family

### Example HBase Table

```
Row Key: "Row-0001"
└─ Column Family: "Home"
   ├─ Qualifier: "Name"
   │  └─ Timestamp-1: "James"
   └─ Qualifier: "Phones"
      ├─ Timestamp-1: "2 42 214339"
      ├─ Timestamp-2: "2 42 213456"
      └─ Timestamp-3: "+61 2 4567890"
└─ Column Family: "Office"
   ├─ Qualifier: "Phone"
   │  └─ Timestamp-4: "+64 345678"
   └─ Qualifier: "Address"
      └─ Timestamp-5: "10 Ellenborough Pl"
```

### Nested Structure View

```json
{
  "Row-0001": {
    "Home": {
      "Name": {
        "timestamp-1": "James"
      },
      "Phones": {
        "timestamp-1": "2 42 214339",
        "timestamp-2": "2 42 213456",
        "timestamp-3": "+61 2 4567890"
      }
    },
    "Office": {
      "Phone": {
        "timestamp-4": "+64 345678"
      },
      "Address": {
        "timestamp-5": "10 Ellenborough Pl"
      }
    }
  }
}
```

## 3. Design Fundamentals

### Critical Design Questions
1. What should be the **row key**?
2. How many **column families**?
3. What **columns** (qualifiers) in each family?
4. What **information** in cells?
5. How many **versions** per cell?

### Important Facts to Remember

1. **Indexing**: Only on **row key**
   - No secondary indexes by default
   - Row key design critical for queries

2. **Sorting**: Tables sorted by **row key**
   - Lexicographic order
   - Range scans efficient

3. **Data Type**: Everything stored as **byte array**
   - Application handles conversion
   - Flexibility in data representation

4. **Atomicity**: Guaranteed at **row level only**
   - No multi-row transactions
   - Operations on single row are atomic

5. **Column Families**: Defined at **table creation**
   - Cannot add/remove easily
   - Physical storage implications

6. **Column Qualifiers**: **Dynamic**
   - Add at write time
   - Can represent data (timestamps, IDs)

7. **Qualifiers as Data**: Can store data in qualifier names
   - Example: `user:2024-01-15` (date as qualifier)

### Design Patterns

#### 1. Entity Type Implementation
```
Row Key: "007"
Column Family: "CUSTOMER"
  - first-name: "James"
  - last-name: "Bond"
  - phone: "007-007"
  - email: "jb@mi6.com"
```

#### 2. One-to-One Relationship
```
Row Key: "Sales"
Column Family: "DEPARTMENT"
  - dname: "Sales"
  - budget: "1000"
Column Family: "MANAGER"
  - enumber: "007"
  - first-name: "James"
  - last-name: "Bond"
```

#### 3. One-to-Many Relationship (Approach 1)
```
Row Key: "007"
Column Family: "EMPLOYEE"
  - enumber: "007"
  - first-name: "James"
  - last-name: "Bond"
  - department: "Sales"
```

#### 4. One-to-Many Relationship (Approach 2)
```
Row Key: "Sales"
Column Family: "DEPARTMENT"
  - dname: "Sales"
  - budget: "1234567"
Column Family: "EMPLOYEE"
  - 007: "James Bond"
  - 008: "Harry Potter"
  - 009: "Robin Hood"
```

#### 5. One-to-Many Relationship (Approach 3)
```
Row Key: "Sales"
Column Family: "DEPARTMENT"
  - dname: "Sales"
  - budget: "1000"
Column Family: "HAS-EMPLOYEES"
  - employees (version-1): "007 James Bond"
  - employees (version-2): "008 Harry Potter"
  - employees (version-3): "009 Robin Hood"
```

#### 6. Many-to-Many Relationship (Approach 1)
```
Row Key: "participation-1"
Column Family: "EMPLOYEE"
  - enumber: "007"
  - first-name: "James"
  - last-name: "Bond"
  - pnumber (version-1): "project-1"
  - pnumber (version-2): "project-2"
```

#### 7. Many-to-Many Relationship (Approach 2)
```
Row Key: "participation-1"
Column Family: "PROJECT"
  - pnumber: "project-1"
  - budget: "12345.25"
  - employee (version-1): "007"
  - employee (version-2): "008"
  - employee (version-3): "009"
```

#### 8. Many-to-Many Relationship (Approach 3)
```
Row Key: "participation-1"
Column Family: "PARTICIPATION"
  - pnumber: "project-1"
  - employee: "employee-007"

Row Key: "participation-2"
Column Family: "PARTICIPATION"
  - pnumber: "project-1"
  - employee: "employee-008"
```

#### 9. Mixed Entity Types in One Table
```
Row Key: "employee-007"
Column Family: "EMPLOYEE"
  - enumber: "007"
  - first-name: "James"
  - last-name: "Bond"

Row Key: "project-1"
Column Family: "PROJECT"
  - pnumber: "1"
  - budget: "12345.25"

Row Key: "participation-2"
Column Family: "PARTICIPATION"
  - pnumber: "project-1"
  - employee: "employee-007"
```

#### 10. Fact with Dimensions (Data Warehouse)
```
Row Key: "1234567"
Column Family: "MEASURE"
  - amount: "1000000"
Column Family: "BUYER"
  - phone: "242214339"
  - first-name: "James"
  - last-name: "Bond"
Column Family: "SELLER"
  - phone: "242215612"
  - first-name: "Harry"
  - last-name: "Potter"
```

#### 11. Graph Structure
```
Row Key: "A"
Column Family: "R"
  - 1: "B"
  - 2: "D"
Column Family: "S"
  - 1: "C"

Row Key: "B"
Column Family: "R"
  - 1: "D"

Row Key: "C"
Column Family: "S"
  - 1: "D"

Row Key: "D"
(empty - leaf node)
```

## 4. Physical Implementation

### Storage Architecture

#### Region
- **Horizontal partition** of HBase table
- Contiguous range of row keys
- **Unit of distribution** and load balancing
- Stored on **Region Server**

#### Region Server
- Manages multiple regions
- Usually **collocated** with HDFS DataNode
- Handles read/write requests for its regions
- Reports to HMaster

#### HMaster
- Coordinates cluster operations
- Assigns regions to Region Servers
- Handles schema changes
- Load balancing

### Scalability
- Tables can grow to **billions of rows**
- **Millions of columns**
- **Terabytes or petabytes** of data
- **Automatic splitting** when regions grow large
- **Horizontal partitioning** for distribution

### Region Assignment
Happens when:
1. Table **grows in size**
2. Region Server **malfunctioning**
3. **New Region Server** added
4. Manual **load balancing**

### Column Family Storage
- Each column family stored **separately**
- **Vertical partitioning** by column family
- Affects:
  - **I/O performance**
  - **Compression**
  - **Caching**

### Versioning
- **Max versions**: Configurable per column family
- **Default**: 3 versions
- Older versions **automatically deleted**
- Can specify **TTL** (Time To Live)

---

## Key Points for Exam

### Core Concepts
1. **Row Key**: Only indexed field, sorted, byte array
2. **Column Family**: Defined at table creation, physical storage unit
3. **Column Qualifier**: Dynamic, can be added at write time
4. **Cell**: (row key, family, qualifier, timestamp)
5. **Value**: Byte array, no data type
6. **Timestamp**: Version number, multiple versions possible

### Logical Structure
```
Table
└─ Row (sorted by row key)
   └─ Column Family (fixed at creation)
      └─ Column Qualifier (dynamic)
         └─ Cell (with timestamp)
            └─ Value (byte array)
```

### Design Fundamentals
1. **Only row key indexed**: Design carefully
2. **Lexicographic sorting**: Row key order matters
3. **Byte arrays**: Everything stored as bytes
4. **Row-level atomicity**: No multi-row transactions
5. **Column families fixed**: Plan ahead
6. **Qualifiers dynamic**: Add anytime
7. **Qualifiers can be data**: Use creatively

### Physical Implementation
1. **Regions**: Horizontal partitions of table
2. **Region Servers**: Manage regions
3. **HMaster**: Coordinates cluster
4. **Column families**: Stored separately (vertical partition)
5. **Colocation**: Region Server + DataNode (data locality)

### Versioning
- Default: **3 versions** per cell
- Configurable per **column family**
- Identified by **timestamp**
- **Latest version** returned by default
- **TTL** can be set

### Key Design Patterns
1. **Entity**: Row key = entity ID
2. **One-to-One**: Multiple column families
3. **One-to-Many**: Embedded or separate rows
4. **Many-to-Many**: Junction table or embedded
5. **Graph**: Adjacency list in column families
6. **Mixed types**: Different entities in same table

### HBase vs Relational DB
| Aspect | HBase | Relational |
|--------|-------|-----------|
| **Schema** | Flexible | Fixed |
| **Index** | Row key only | Multiple |
| **Columns** | Dynamic | Static |
| **Data Type** | Byte array | Typed |
| **Transactions** | Row-level | Multi-row |
| **Joins** | Application | Database |
| **Scalability** | Horizontal | Vertical/Limited |

### Important Characteristics
- **Sparse**: Not all columns need values
- **Distributed**: Across cluster
- **Column-oriented**: Store by column family
- **Versioned**: Multiple timestamps
- **No joins**: Application handles
- **Strong consistency**: Not eventual
- **Random access**: Read/write any row
- **Built on HDFS**: Inherits reliability

### When to Use HBase
- **Random read/write** access needed
- **Billions of rows**
- **Variable schema**
- **Time-series data**
- **High write throughput**
- **Need strong consistency**

### When NOT to Use HBase
- **Complex queries** with joins
- **Full table scans** frequently
- **Small datasets** (< TB)
- **Relational guarantees** needed
- **Ad-hoc analytics** (use Hive instead)
