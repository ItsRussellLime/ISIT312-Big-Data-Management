# Topic 15: Logical Data Warehouse Design

## 1. OLAP Technologies

### Three Main OLAP Implementations

#### 1. ROLAP (Relational OLAP)

**Definition**: Stores data in **relational databases**

**Characteristics**:
- Uses **SQL extensions** for OLAP operations
- **Special access methods** for efficient implementation
- Data stored in traditional **tables** (rows and columns)
- Leverages **relational database technology**

**Advantages**:
- ✅ Scales well with large data volumes
- ✅ Leverages mature RDBMS technology
- ✅ Better **storage capacity** than MOLAP
- ✅ Can use existing relational infrastructure

**Disadvantages**:
- ❌ Slower **query and aggregation performance** than MOLAP
- ❌ Complex queries require multiple joins

---

#### 2. MOLAP (Multidimensional OLAP)

**Definition**: Stores data in **special data structures** (e.g., arrays, cubes)

**Characteristics**:
- **Native multidimensional** storage
- OLAP operations implemented **directly in specialized structures**
- Pre-computed **aggregations**
- Array-based or proprietary formats

**Advantages**:
- ✅ **Better performance** for query and aggregation
- ✅ Optimized for **OLAP operations** (slice, dice, roll-up)
- ✅ Faster response times for complex analytical queries

**Disadvantages**:
- ❌ **Less storage capacity** than ROLAP
- ❌ Scalability limitations with very large datasets
- ❌ Data duplication (pre-aggregated values)

---

#### 3. HOLAP (Hybrid OLAP)

**Definition**: **Combines ROLAP and MOLAP** technologies

**Strategy**:
- **Detailed data** stored in **relational databases** (ROLAP)
- **Aggregations** kept in **separate MOLAP store**
- Best of both worlds approach

**Advantages**:
- ✅ Balance between **performance** and **storage**
- ✅ Detailed data uses efficient relational storage
- ✅ Fast aggregation queries using MOLAP
- ✅ Flexible architecture

**Example Architecture**:
```
Detailed Sales Data → ROLAP (Relational DB)
    ↓
Monthly/Yearly Aggregates → MOLAP (Cube Storage)
```

---

### OLAP Technology Comparison

| Aspect | ROLAP | MOLAP | HOLAP |
|--------|-------|-------|-------|
| **Storage** | Relational tables | Multidimensional arrays | Hybrid |
| **Query Performance** | Slower | Faster | Medium-Fast |
| **Storage Capacity** | Higher | Lower | Medium |
| **Scalability** | Better | Limited | Good |
| **Implementation** | SQL + Extensions | Proprietary structures | Combined |
| **Use Case** | Large detailed data | Fast analytics | Balanced approach |

---

## 2. Relational Data Warehouse Design

### Schema Types

In **ROLAP systems**, tables are organized in specialized structures:

#### 1. Star Schema

**Definition**: One **fact table** surrounded by **dimension tables**

**Structure**:
- **Fact table** (center): Contains measures and foreign keys
- **Dimension tables** (points): Denormalized, contain hierarchies

**Characteristics**:
- **Simple structure**: Easy to understand
- **Denormalized dimensions**: May contain **redundancy**
- **Fast queries**: Fewer joins needed
- **Referential integrity** between fact and dimensions

**Visual Analogy**: Like a star with fact table at center

**Example**:
```
        Time
         |
Product - SALES - Customer
         |
      Location
```

**Advantages**:
- ✅ Simple queries with fewer joins
- ✅ Better query performance
- ✅ Easy for users to understand

**Disadvantages**:
- ❌ Redundancy in dimension tables
- ❌ Larger storage requirements
- ❌ Update anomalies possible

---

#### 2. Snowflake Schema

**Definition**: **Normalizes dimension tables** to avoid redundancy

**Structure**:
- **Fact table** (center): Same as star schema
- **Normalized dimension tables**: Hierarchies split into separate tables

**Characteristics**:
- **Removes redundancy** from star schema
- **Dimension tables normalized** into multiple related tables
- More complex structure with **more tables**

**Visual Analogy**: Like a snowflake with branching structure

**Example**:
```
Time → Month → Quarter → Year
  |
SALES
  |
Product → Category
  |
Customer → City → Country
```

**Advantages**:
- ✅ **Optimizes storage space** (no redundancy)
- ✅ Easier to maintain dimensional data
- ✅ Better for slowly changing dimensions

**Disadvantages**:
- ❌ **Decreased query performance** (more joins)
- ❌ More complex queries
- ❌ Harder for users to understand

---

#### 3. Starflake Schema (Galaxy Schema)

**Definition**: **Hybrid** of star and snowflake schemas

**Characteristics**:
- **Some dimensions normalized**, others not
- Mix of denormalized and normalized dimensions
- Flexibility to optimize based on dimension characteristics

**Design Decision**:
- Normalize dimensions with **high cardinality** or **many attributes**
- Keep dimensions denormalized for **simplicity** and **performance**

**Example**:
```
Time (normalized) → Month → Quarter
  |
SALES
  |
Product (denormalized - Category embedded)
```

---

#### 4. Constellation Schema (Fact Constellation)

**Definition**: **Multiple fact tables** that **share dimension tables**

**Characteristics**:
- More than one fact table
- **Shared dimensions** across facts
- Represents multiple business processes

**Also Known As**:
- Galaxy schema
- Multi-fact schema

**Example**:
```
          Time
           |
    +------+------+
    |             |
  SALES      INVENTORY
    |             |
    +------+------+
           |
        Product
```
- Sales and Inventory facts **share** Time and Product dimensions

**Use Cases**:
- Enterprise-wide data warehouses
- Multiple related business processes
- Consistent dimensional analysis across facts

**Advantages**:
- ✅ Supports **multiple business processes**
- ✅ **Reuses dimensions** (no duplication)
- ✅ Integrated enterprise view

---

### Schema Characteristics Summary

**Referential Integrity**:
- Constraints between **fact and dimension tables**
- Ensures data consistency
- Foreign keys in fact table → Primary keys in dimensions

**Normalization Trade-off**:
- **Dimension tables**: Often **denormalized** (may contain redundancy)
- **Fact tables**: Always **normalized** (no redundancy)
- Normalized tables optimize **storage**, denormalized optimize **performance**

**Key Principle**:
> "Dimension tables denormalized, fact tables normalized"

---

## 3. Relational Implementation of Conceptual Model

### Mapping Rules: MultiDim → Relational

A set of rules to translate **MultiDim conceptual model** to **relational model**

---

### Rule 1: Level Mapping

**Statement**: A level L (not related to fact with 1:1) → Table TL

**Process**:
1. Create table **TL** for level L
2. Include **all attributes** of the level
3. Add **surrogate key** (optional but recommended)
4. If no surrogate key, **level identifier** becomes table key

**Example**:
```
MultiDim Level: Customer (CustomerID, Name, Phone, Email)
    ↓
Relational Table: 
Customer (CustomerKey, CustomerID, Name, Phone, Email)
```
- **CustomerKey**: Surrogate key (new)
- **CustomerID**: Natural/business key (from level)

---

### Rule 2: Fact Mapping

**Statement**: A fact F → Table TF with all measures

**Process**:
1. Create table **TF** for fact F
2. Include **all measures** as attributes
3. Add **surrogate key** (optional)
4. Additional attributes added via **Rule 3** (foreign keys)

**Example**:
```
MultiDim Fact: Sales (Quantity, Amount, Discount)
    ↓
Relational Table:
Sales (SalesKey, Quantity, Amount, Discount, [FKs added by Rule 3])
```

**Note**: Foreign keys to dimensions added through Rule 3

---

### Rule 3: Relationship Mapping

**Statement**: Map relationships based on **cardinality**

Three sub-rules based on relationship type:

---

#### Rule 3a: One-to-One Relationship

**Applies to**:
- Fact F ↔ Dimension Level L (1:1)
- Parent Level LP ↔ Child Level LC (1:1)

**Action**: 
- **Extend** fact table (TF) or child table (TC)
- Add **all attributes** from dimension/parent level

**Result**: No separate dimension/parent table needed

**Example**:
```
Fact: Sales (1:1) Order
    ↓
Sales table includes: OrderNumber, OrderDate (Order attributes)
```

**Special Case**: **Degenerate Dimension**
- Dimension exists only in fact table
- No separate dimension table
- Example: Order number, Invoice number

---

#### Rule 3b: One-to-Many Relationship

**Applies to**:
- Fact F → Dimension Level L (1:N)
- Child Level LC → Parent Level LP (1:N)

**Action**:
- **Extend** fact table (TF) or child table (TC)
- Add **surrogate key** (foreign key) from dimension/parent table

**Result**: Foreign key establishes relationship

**Example**:
```
Sales →(many) Customer
    ↓
Sales table includes: CustomerKey (FK to Customer table)
```

**Typical Case**: Most fact-dimension relationships are 1:N

---

#### Rule 3c: Many-to-Many Relationship

**Applies to**:
- Fact F ↔ Dimension Level L (M:N)
- Parent Level LP ↔ Child Level LC (M:N)

**Action**:
1. Create **new bridge table** (TB)
2. Include **two foreign keys**:
   - FK to fact/parent table
   - FK to dimension/child table
3. If relationship has **distributing attribute**, add it to bridge table

**Result**: Bridge table resolves M:N relationship

**Example**:
```
Employee ←(M:N)→ Territory
    ↓
Bridge Table: EmployeeTerritory
- EmployeeKey (FK)
- TerritoryKey (FK)
- AllocationPercentage (distributing attribute)
```

**Distributing Attribute**: 
- Represents share/weight of relationship
- Example: Employee allocated 60% to Territory A, 40% to Territory B

---

### Rule 3 Summary Table

| Cardinality | Action | Result | Example |
|-------------|--------|--------|---------|
| **1:1** | Embed attributes | No separate table | Order → Sales (degenerate) |
| **1:N** | Add foreign key | FK in many side | Customer → Sales |
| **M:N** | Create bridge table | Intermediary table | Employee ↔ Territory |

---

## 4. Northwind Data Warehouse Example

### Relational Implementation Details

**Sales Fact Table**:
- Includes **one FK for each level** related with 1:N relationship
- **Five measure attributes**:
  1. UnitPrice
  2. Quantity
  3. Discount
  4. SalesAmount
  5. Freight

**Time Dimension (Role-Playing)**:
- **Multiple roles**: OrderDate, DueDate, ShippedDate
- Same Time dimension table used three times
- Three different foreign keys in Sales table

**Degenerate Dimension**:
- **Order**: Related to fact with **1:1 relationship**
- OrderNumber stored directly in Sales table
- No separate Order dimension table
- Also called **fact dimension**

**Bridge Table**:
- **Territories** table: Maps M:N relationship
- Between Employee and Territory
- Contains **two foreign keys**:
  - EmployeeKey
  - TerritoryKey

**Surrogate vs Natural Keys**:
- **Customer**: 
  - Surrogate key: **CustomerKey**
  - Natural key: **CustomerAltKey**
- **Supplier**:
  - **SupplierKey**: Database key (natural key)

---

## 5. The Time Dimension

### Importance

**Why Special Treatment**:
- Data warehouse is a **historical database**
- Time dimension present in **almost all data warehouses**
- Critical for trend analysis and historical comparisons

**Inclusion in Schemas**:
- **Foreign key(s)** in fact table
- **Time dimension table** with aggregation levels

---

### OLTP vs Data Warehouse Time Handling

#### OLTP Databases
- Temporal information **derived from DATE data type**
- Use **on-the-fly functions** for computations
- Example: Compute "weekend" using date functions

#### Data Warehouses
- Time information stored as **explicit attributes**
- Pre-computed values for faster queries
- Example: WeekendFlag attribute

---

### Time Dimension Benefits

**Explicit Storage Advantages**:

**Example**: Calculate total sales during weekends

**OLTP Approach** (slower):
```sql
SELECT SUM(SalesAmount)
FROM Sales S
WHERE DAYOFWEEK(S.OrderDate) IN (6, 7)  -- Compute on-the-fly
```

**Data Warehouse Approach** (faster):
```sql
SELECT SUM(SalesAmount)
FROM Time T, Sales S
WHERE T.TimeKey = S.TimeKey 
  AND T.WeekendFlag = TRUE  -- Pre-computed attribute
```

**Benefits**:
- ✅ **Faster queries**: No computation needed
- ✅ **Simpler SQL**: Direct attribute filtering
- ✅ **Consistent**: Pre-computed logic always same
- ✅ **Richer attributes**: Can store fiscal periods, holidays, etc.

---

### Time Dimension Structure

**Typical Attributes**:
- **Keys**: TimeKey (surrogate), Date (natural)
- **Hierarchy levels**: Day, Month, Quarter, Year
- **Descriptive**: DayOfWeek, WeekendFlag, HolidayFlag
- **Business-specific**: FiscalPeriod, FiscalYear
- **Computed**: WeekNumber, DayOfYear

**Example Time Table**:
```
TimeKey | Date       | Year | Quarter | Month | Day | DayOfWeek | WeekendFlag
--------|------------|------|---------|-------|-----|-----------|------------
1       | 2024-01-01 | 2024 | Q1      | Jan   | 1   | Monday    | FALSE
2       | 2024-01-02 | 2024 | Q1      | Jan   | 2   | Tuesday   | FALSE
...
```

---

### Granularity Considerations

**Definition**: Level of detail for time dimension

**Calculation Example**:
- **Granularity**: Month
- **Span**: 5 years
- **Tuples**: 5 × 12 = **60 records**

**Common Granularities**:
1. **Day**: 365/366 records per year
2. **Month**: 12 records per year
3. **Quarter**: 4 records per year
4. **Year**: 1 record per year

**Design Decision Factors**:
- Business requirements
- Query patterns
- Storage considerations
- Update frequency

**Example Scenarios**:
- **Retail**: Day-level granularity (daily sales analysis)
- **Financial reporting**: Month-level (monthly summaries)
- **Strategic planning**: Quarter/Year-level (trends)

---

## Summary: Logical Design Key Points

### OLAP Technologies
- **ROLAP**: Relational storage, better capacity
- **MOLAP**: Multidimensional storage, better performance
- **HOLAP**: Hybrid approach, balanced

### Schema Types
- **Star**: Simple, denormalized, fast queries
- **Snowflake**: Normalized, less storage, more joins
- **Starflake**: Hybrid approach
- **Constellation**: Multiple facts, shared dimensions

### Mapping Rules
- **Rule 1**: Level → Table
- **Rule 2**: Fact → Table with measures
- **Rule 3**: Relationships by cardinality
  - 1:1 → Embed attributes
  - 1:N → Foreign key
  - M:N → Bridge table

### Time Dimension
- Special importance in data warehouses
- Explicit attributes for performance
- Various granularities based on needs

---

## Exam Tips

1. **Know all three OLAP types** and their trade-offs
2. **Star vs Snowflake**:
   - Star: denormalized, fast, redundant
   - Snowflake: normalized, slow, no redundancy
3. **Understand constellation schema**: Multiple facts, shared dimensions
4. **Master mapping rules**:
   - 1:1 → Embed (degenerate dimension)
   - 1:N → FK (most common)
   - M:N → Bridge table
5. **Degenerate dimension**: Dimension data in fact table (1:1 relationship)
6. **Bridge table**: Resolves M:N relationships, may have distributing attribute
7. **Time dimension**: Explicit attributes for performance, multiple roles possible
8. **Surrogate keys**: Recommended for all dimension tables
9. **Referential integrity**: Fact table FKs → Dimension table PKs
10. **Remember**: "Dimension tables denormalized, fact tables normalized"

### Common Exam Scenarios
- Design star/snowflake schema for given requirements
- Identify when to use bridge tables
- Calculate dimension table sizes based on granularity
- Map conceptual MultiDim model to relational schema