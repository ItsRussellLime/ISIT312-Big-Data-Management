# Topic 19: HBase Data Model

## 1. Background

### What is HBase?

**HBase**: Open-source distributed database based on **Google's BigTable** data model

**Key Characteristics**:
- Provides **BigTable view** of data stored in HDFS
- Also called **Hadoop Database**
- Runs on top of HDFS

---

### HBase vs Traditional RDBMS

**Similarities**:
- ✅ Provides **tabular view** of data

**Differences**:
- ❌ Very different from traditional relational data model
- ❌ No fixed schema
- ❌ No SQL (uses different query model)

---

### HBase Data Model Definition

**HBase Data Model**: 
> Sparse, distributed, persistent **multidimensional sorted map**

**Indexed by**:
1. **Row key**
2. **Column key** (family + qualifier)
3. **Timestamp**

**Formula**:
```
(Row Key, Column Family, Column Qualifier, Timestamp) → Cell Value
```

---

## 2. Logical View of Data

### Table Structure

**HBase organizes data into tables**

**Hierarchy**:
```
Table
└── Rows
    └── Column Families
        └── Column Qualifiers (Columns)
            └── Cells
                └── Versions (Timestamped Values)
```

---

### Row Key

**Definition**: **Unique identifier** for each row

**Characteristics**:
- ✅ Every row has exactly one row key
- ✅ Rows **sorted by row key**
- ✅ **Only indexed** component (very important!)

**Example**:
```
Row Key: "007"
Row Key: "employee-007"
Row Key: "Sales"
```

---

### Column Families

**Definition**: Group of columns stored together

**Key Properties**:
1. **Defined at table creation time** (cannot add later without schema change)
2. **Every row has same column families** (though families can be empty)
3. **Important impact on physical implementation**
4. Stored together on disk

**Example**:
```
Table: PERSON
Column Families: HOME, OFFICE
```

**Why Important**: 
- Affects storage and retrieval performance
- Different families stored in separate files

---

### Column Qualifiers (Column Names)

**Definition**: Specific column within a column family

**Notation**: `family:qualifier`

**Key Properties**:
1. **Dynamic**: Can be defined at **write time** (not schema creation)
2. **Flexible**: Different rows can have different qualifiers
3. Stored as **byte sequences**
4. Can **represent data** themselves

**Examples**:
- `Home:Name`
- `Home:Phones`
- `Office:Phone`
- `Office:Address`

---

### Cells

**Definition**: Intersection of row, column family, and column qualifier

**Unique Identification**:
```
(Row Key, Column Family, Column Qualifier, Timestamp) → Cell
```

**Cell Value Characteristics**:
- **No data type**: Always treated as **sequences of bytes**
- **Type-agnostic**: Application interprets meaning
- **Flexible**: Can store any binary data

---

### Versions and Timestamps

**Multiple Versions**: Each cell can store **multiple values**

**Version Identification**: By **timestamp**

**Timestamp Rules**:
1. **Write time**: If not specified, use **current timestamp**
2. **Read time**: If not specified, return **latest version**

**Version Limit**:
- **Configurable** per column family
- **Default**: 3 versions
- Older versions automatically discarded

**Example**:
```
Home:Phones
  timestamp-1: "2 42 214339"
  timestamp-2: "2 42 213456"
  timestamp-3: "+61 2 4567890"  ← Latest (returned by default)
```

---

### Nested Structure View

**Example HBase Table as JSON**:

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
  },
  "Row-0002": {
    "Home": {
      "Name": {
        "timestamp-6": "Harry"
      },
      "Phones": {
        "timestamp-7": "2 42 214234"
      }
    },
    "Office": {
      "Phone": {
        "timestamp-8": "+64 345678"
      },
      "Address": {
        "timestamp-9": "10 Bong Bong Rd",
        "timestamp-10": "23 Victoria Rd"
      }
    }
  }
}
```

---

### Keys in HBase

**Key Composition**: Depends on what needs to be retrieved

**Options**:
1. **Row key only**: Retrieve all cells in a row
2. **Row key + Column family**: Retrieve all columns in family
3. **Row key + Column family + Qualifier**: Retrieve specific column
4. **Row key + Column family + Qualifier + Timestamp**: Retrieve specific version

---

## 3. Design Fundamentals

### HBase as Hierarchical Structure

**Four Levels**:
1. **Table** → Contains rows
2. **Rows** → Contain column families
3. **Column Families** → Contain columns
4. **Columns** → Contain versions

**Can Become Network/Graph**: If cells contain keys/references to other rows

---

### Key Design Questions

When designing HBase table, consider:

1. **What should be the row key?**
   - Most critical decision
   - Affects query performance
   - Only indexed field

2. **How many column families?**
   - Affects physical storage
   - Usually keep small (1-3)

3. **What columns (qualifiers) in each family?**
   - Dynamic, but plan common ones
   - Think about access patterns

4. **What information in cells?**
   - Simple values vs. complex structures
   - References to other rows?

5. **How many versions to store?**
   - Based on temporal query needs
   - Storage vs. functionality trade-off

---

### Important Design Facts

**Critical Constraints**:

1. **Indexing only on row key**
   - No secondary indexes by default
   - Row key design crucial for performance

2. **Tables sorted by row key**
   - Lexicographic order
   - Affects range scan performance

3. **Everything stored as untyped bytes**
   - Application responsible for serialization/deserialization

4. **Atomicity only at row level**
   - No multi-row transactions
   - No ACID across rows

5. **Column families defined at creation**
   - Must plan ahead
   - Changes require schema modification

6. **Column qualifiers are dynamic**
   - Can be added at write time
   - Great flexibility

7. **Qualifiers stored as byte sequences**
   - Can represent data themselves
   - Example: timestamp as qualifier

---

## 4. Design Patterns

### Entity Type Implementation

**Example: Customer Entity**

```json
{
  "007": {
    "CUSTOMER": {
      "first-name": {"timestamp-1": "James"},
      "last-name": {"timestamp-2": "Bond"},
      "phone": {"timestamp-1": "007-007"},
      "email": {"timestamp-1": "jb@mi6.com"}
    }
  }
}
```

**Pattern**:
- Row key: Unique identifier (e.g., customer ID)
- Column family: Entity type name
- Qualifiers: Entity attributes

---

### One-to-One Relationship

**Example: Department and Manager**

```json
{
  "Sales": {
    "DEPARTMENT": {
      "dname": {"timestamp-1": "Sales"},
      "budget": {"timestamp-1": "1000"}
    },
    "MANAGER": {
      "enumber": {"timestamp-2": "007"},
      "first-name": {"timestamp-3": "James"},
      "last-name": {"timestamp-4": "Bond"}
    }
  }
}
```

**Pattern**:
- Row key: Shared identifier (department name)
- Two column families: One per entity
- Each family contains respective attributes

---

### One-to-Many Relationship

#### Pattern 1: Foreign Key in "Many" Side

```json
{
  "007": {
    "EMPLOYEE": {
      "enumber": {"timestamp-1": "007"},
      "first-name": {"timestamp-2": "James"},
      "last-name": {"timestamp-3": "Bond"},
      "department": {"timestamp-4": "Sales"}
    }
  }
}
```

**Pattern**: Store reference to "one" side (like RDBMS foreign key)

---

#### Pattern 2: Embed "Many" in "One"

```json
{
  "Sales": {
    "DEPARTMENT": {
      "dname": {"timestamp-1": "Sales"},
      "budget": {"timestamp-1": "1234567"}
    },
    "EMPLOYEE": {
      "007": {"timestamp-2": "James Bond"},
      "008": {"timestamp-3": "Harry Potter"},
      "009": {"timestamp-4": "Robin Hood"}
    }
  }
}
```

**Pattern**: 
- Row key: Department (one side)
- Column family: EMPLOYEE
- Qualifiers: Employee IDs
- Values: Employee names

**Advantage**: Single row read gets department + all employees

---

#### Pattern 3: Versions for Multiple Values

```json
{
  "Sales": {
    "DEPARTMENT": {
      "dname": {"timestamp-1": "Sales"},
      "budget": {"timestamp-1": "1000"}
    },
    "HAS-EMPLOYEES": {
      "employees": {
        "timestamp-2": "007 James Bond",
        "timestamp-3": "008 Harry Potter",
        "timestamp-4": "009 Robin Hood"
      }
    }
  }
}
```

**Pattern**: Use versions to store multiple related values

---

### Many-to-Many Relationship

#### Pattern 1: Store Array of Keys

**Employee Side**:
```json
{
  "participation-1": {
    "EMPLOYEE": {
      "enumber": {"timestamp-1": "007"},
      "first-name": {"timestamp-2": "James"},
      "last-name": {"timestamp-3": "Bond"},
      "pnumber": {
        "timestamp-4": "project-1",
        "timestamp-5": "project-2"
      }
    }
  }
}
```

---

#### Pattern 2: Project Side

**Project Side**:
```json
{
  "participation-1": {
    "PROJECT": {
      "pnumber": {"timestamp-1": "project-1"},
      "budget": {"timestamp-2": "12345.25"},
      "employee": {
        "timestamp-3": "007",
        "timestamp-4": "008",
        "timestamp-5": "009"
      }
    }
  }
}
```

---

#### Pattern 3: Junction Table (Link Table)

**Participation Row 1**:
```json
{
  "participation-1": {
    "PARTICIPATION": {
      "pnumber": {"timestamp-1": "project-1"},
      "employee": {"timestamp-2": "employee-007"}
    }
  }
}
```

**Participation Row 2**:
```json
{
  "participation-2": {
    "PARTICIPATION": {
      "pnumber": {"timestamp-1": "project-1"},
      "employee": {"timestamp-2": "employee-008"}
    }
  }
}
```

**Pattern**: Separate row for each relationship instance (like junction table)

---

### Mixed Entity Types in One Table

**Possible**: Group different entity types in same table

```json
{
  "employee-007": {
    "EMPLOYEE": {
      "enumber": {"timestamp-1": "007"},
      "first-name": {"timestamp-2": "James"},
      "last-name": {"timestamp-3": "Bond"}
    }
  },
  "project-1": {
    "PROJECT": {
      "pnumber": {"timestamp-4": "1"},
      "budget": {"timestamp-5": "12345.25"}
    }
  },
  "participation-2": {
    "PARTICIPATION": {
      "pnumber": {"timestamp-1": "project-1"},
      "employee": {"timestamp-2": "employee-007"}
    }
  }
}
```

**Use row key prefix** to distinguish entity types (e.g., "employee-", "project-")

---

### Fact with Dimensions (Data Warehouse Pattern)

```json
{
  "1234567": {
    "MEASURE": {
      "amount": {"timestamp-1": "1000000"}
    },
    "BUYER": {
      "phone": {"timestamp-1": "242214339"},
      "first-name": {"timestamp-1": "James"},
      "last-name": {"timestamp-1": "Bond"}
    },
    "SELLER": {
      "phone": {"timestamp-1": "242215612"},
      "first-name": {"timestamp-1": "Harry"},
      "last-name": {"timestamp-1": "Potter"}
    }
  }
}
```

**Pattern**:
- Row key: Transaction/fact ID
- Column families: Measure + each dimension
- Denormalized: Dimension attributes embedded

---

### Graph Structure Implementation

**Node A**:
```json
{
  "A": {
    "R": {
      "1": {"timestamp-1": "B"},
      "2": {"timestamp-1": "D"}
    },
    "S": {
      "1": {"timestamp-1": "C"}
    }
  }
}
```

**Node B**:
```json
{
  "B": {
    "R": {
      "1": {"timestamp-1": "D"}
    }
  }
}
```

**Pattern**:
- Row key: Node ID
- Column families: Edge types (R, S)
- Qualifiers: Edge numbers
- Values: Target node IDs

**Use Case**: Social networks, knowledge graphs, recommendation systems

---

## 5. Physical Implementation

### HBase on HDFS

**Foundation**: HBase is database **built on top of HDFS**

**Scalability**:
- **Billions of rows**
- **Millions of columns**
- **Terabytes to petabytes** of data

---

### Regions and Region Servers

**Challenge**: Tables too large for single server

**Solution**: **Horizontal splits** into **regions**

**Region**: Chunk of data (contiguous row key range)

**Region Server**: Server hosting one or more regions

**Collocation**: Region servers usually **collocated with HDFS data nodes**

**Example**:
```
Table: CUSTOMER
├── Region 1: Row keys A-G (Server 1)
├── Region 2: Row keys H-N (Server 2)
├── Region 3: Row keys O-T (Server 3)
└── Region 4: Row keys U-Z (Server 4)
```

---

### Region Splits

**Horizontal Splits (Usual)**:
- Divide by **row key ranges**
- Each region contains subset of rows
- Sorted by row key

**Vertical Splits (Also Possible)**:
- Separate **column families**
- Different families on different servers
- Benefits when families accessed independently

---

### Region Assignment

**When does region assignment happen?**

1. **Table grows**: Region becomes too large → split into two
2. **Region server malfunction**: Regions reassigned to healthy servers
3. **New region server added**: Rebalance load

**Goal**: **Load balancing** across cluster

---

## Summary: HBase Data Model Key Points

### Structure
- **Sparse, distributed, persistent multidimensional sorted map**
- **Indexed by**: Row key, column family, column qualifier, timestamp
- **Hierarchy**: Table → Row → Column Family → Column → Versions

### Critical Design Facts
1. **Only row key is indexed** (most important!)
2. Tables **sorted by row key**
3. **Everything stored as bytes**
4. **Atomicity only at row level**
5. **Column families fixed at creation**
6. **Column qualifiers dynamic**

### Physical Implementation
- **Regions**: Horizontal splits of table
- **Region servers**: Host regions
- **Collocation**: Region servers + HDFS data nodes
- **Splits**: Automatic based on size or manual

---

## Exam Tips

1. **Row key is only indexed field** - Design carefully!
2. **Four-level hierarchy**: Table → Row → Family → Column → Versions
3. **Sparse model**: Not all rows have all columns
4. **No data types**: Everything is bytes
5. **Versions**: Default 3, configurable per family
6. **Column families**: Fixed at creation, impacts storage
7. **Column qualifiers**: Dynamic, can be data
8. **Atomicity**: Row-level only, no multi-row transactions
9. **Regions**: Horizontal splits for scalability
10. **Design patterns**: Know how to model 1:1, 1:M, M:M relationships

### Common Exam Questions
- Design HBase schema for given requirements
- Explain difference from relational model
- Describe version handling
- Explain region splits and assignment
- Model relationships in HBase
- Why is row key design critical?