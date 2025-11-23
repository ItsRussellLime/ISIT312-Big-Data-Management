# Topic 14: Conceptual Data Warehouse Design

## 1. MultiDim Conceptual Model

### Need for Conceptual Models

**Purpose of Conceptual Models**:
- **Better communication** between designers and users
- Understand **application requirements** clearly
- **More stable** than logical schemas (implementation-oriented)
- Independent of platform changes
- **Visual support** for user interfaces

---

### Problems with Current Approaches

**Existing Models**:
- Based on UML, ER model, or specific notations
- **No well-established standard** for multidimensional data

**Common Issues**:
1. Cannot express **complex hierarchies**
2. Lack of **mapping to implementation** platforms
3. Currently, data warehouses designed mostly using **logical models** (star/snowflake)

**Limitations of Logical Models**:
- Require **technical knowledge** to express requirements
- Users limited to defining what **implementation systems can manage**
- Not ideal for requirement gathering phase

---

### MultiDim Model Characteristics

**Foundation**: Based on **Entity-Relationship (ER) model**

**Key Concepts Included**:
1. **Dimensions**
2. **Hierarchies**
3. **Facts**
4. **Measures**

**Advantages**:
- Supports **various kinds of hierarchies** in real-world applications
- Can be **mapped to star or snowflake** relational structures
- Bridge between conceptual design and implementation

---

## 2. MultiDim Model Notation

### Core Components

#### Dimension
- **Definition**: Level or one or more hierarchies
- Represents perspective for analysis

#### Hierarchy
- **Definition**: Several related levels
- Shows parent-child relationships between levels

#### Level
- **Definition**: Entity type in hierarchy
- Represents a granularity of analysis

#### Member
- **Definition**: Every instance of a level
- Example: "Paris" is a member of City level

#### Child and Parent Levels
- **Child**: Lower level in hierarchy (finer granularity)
- **Parent**: Higher level in hierarchy (coarser granularity)

#### Leaf and Root Levels
- **Leaf level**: First level (finest granularity)
- **Root level**: Last level (coarsest granularity, often "All")

---

### Attributes in Levels

#### Key Attribute
- **Purpose**: Indicates how **child members are grouped**
- Used to roll up from child to parent
- Example: City grouped by Country

#### Descriptive Attributes
- **Purpose**: Describe **characteristics of members**
- Provide additional information
- Not used for aggregation
- Example: Population, Area for City level

---

### Cardinality

**Definition**: Minimum/maximum numbers of members in a level related to members in another level

**Notation**: (min, max) on relationship lines

**Common Cardinalities**:
- **(1,1)**: One-to-one
- **(0,n)**: Zero to many
- **(1,n)**: One to many
- **(n,m)**: Many to many

**Example**: 
- City to Country: (1,1) - each city in exactly one country
- Country to City: (1,n) - each country has one or more cities

---

### Criterion

**Definition**: Expresses **different hierarchical structures** used for analysis

**Purpose**: 
- Shows alternative ways to aggregate data
- Enables multiple analysis paths

**Example**: 
- Products can be grouped by Category OR by Supplier
- Two different criteria for Product dimension

---

### Facts

**Definition**: Central concept that relates **measures** to **leaf levels** in dimensions

**Characteristics**:
- Contains **measures** (numeric values)
- Related to **multiple dimensions**
- Represents business process or event

**Dimension-Fact Relationships**:
1. **One-to-one**: Each fact relates to exactly one dimension member
2. **One-to-many**: One dimension member relates to many facts
3. **Many-to-many**: Complex relationship (less common)

**Role-Playing Dimensions**:
- Same dimension can relate to fact **multiple times** with **different roles**
- Example: Time dimension with roles "Order Date" and "Ship Date"

---

### Graphical Notation Summary

**Visual Elements**:
1. **Rectangle**: Level (entity type)
2. **Lines with arrows**: Parent-child relationships
3. **Diamond**: Fact
4. **Lines connecting fact to dimensions**: Fact-dimension relationships
5. **Cardinality notations**: (min, max) on relationships
6. **Criterion indicators**: Show alternative hierarchies

---

## 3. Dimension Hierarchies - Types

### 1. Balanced Hierarchies

**Definition**: The simplest and most common type

**Schema Level Characteristics**:
- **Only one path** from leaf to root
- All parent-child relationships are **many-to-one** (n:1)
- All relationships are **mandatory** (minimum cardinality = 1)

**Instance Level Characteristics**:
- Members form a **balanced tree**
- All branches have the **same length**
- All parent members have **at least one child**
- Each child belongs to **exactly one parent**

**Example**: Time dimension
```
Day → Month → Quarter → Year
```
- Every day belongs to exactly one month
- Every month belongs to exactly one quarter
- Every quarter belongs to exactly one year
- All paths have same depth (4 levels)

**Properties**:
- ✅ Easy to understand and implement
- ✅ Predictable aggregation behavior
- ✅ No null values or missing levels
- Most **common in practice**

---

### 2. Unbalanced Hierarchies

**Definition**: Hierarchies where branches have different lengths

**Schema Level Characteristics**:
- **One path** from leaf to root
- All parent-child relationships are **many-to-one** (n:1)
- Some relationships are **optional** (minimum cardinality = 0)

**Instance Level Characteristics**:
- Members form an **unbalanced tree**
- Different branches have **different lengths**
- Some members may **skip levels**

**Example**: Employee organizational hierarchy
```
Employee → Manager → Director → VP → CEO
```
- Some employees report directly to CEO (skip intermediate levels)
- Path lengths vary

**Visual Indicator**: 
- **(0,n)** cardinality on some relationships
- Shows optional participation

**Challenges**:
- More complex aggregation logic
- Need to handle null/missing levels
- Queries must account for variable depth

---

### 3. Recursive Hierarchies

**Definition**: Special case of unbalanced hierarchies where a level relates to itself

**Key Characteristic**:
- **Same level** is linked by two roles of parent-child relationship
- Level acts as both parent and child

**When to Use**:
- All hierarchy levels express the **same semantics**
- Characteristics of parent and child are **similar or identical**

**Schema Level**:
- Self-referencing relationship
- One level, but with parent-child roles

**Instance Level**:
- Tree structure with varying depth
- Same entity type at all levels

**Example 1**: Employee hierarchy
```
Employee ← supervises ← Employee
```
- Employee table references itself
- John supervises Mary, Mary supervises Tom

**Example 2**: Location hierarchy
```
Location ← contains ← Location
```
- World → Continent → Country → State → City
- All are "Location" entities

**Implementation Note**:
- Often uses **self-join** in relational databases
- Requires parent_id foreign key pointing to same table

**Advantages**:
- Flexible depth
- Can represent complex organizational structures
- Single table/level definition

**Disadvantages**:
- More complex queries (recursive SQL needed)
- Aggregation more complicated

---

### 4. Generalized Hierarchies

**Definition**: Multiple alternative paths for aggregation

**Schema Level Characteristics**:
- **Multiple exclusive paths** share at least the **leaf level**
- May also share **other intermediate levels**
- Each path represents different aggregation logic

**Instance Level Characteristics**:
- Each member belongs to **only one path**
- Members follow one aggregation route only

**Example**: Customer dimension
```
Customer → Individual Customer → Customer Type → All Customers
Customer → Corporate Customer → Industry → All Customers
```
- Two separate aggregation paths
- One for individual customers (by type)
- One for corporate customers (by industry)
- Both paths start at Customer and end at All Customers

**Use Cases**:
- Different types of entities need different classification schemes
- Business requires multiple analysis perspectives
- Heterogeneous data with different categorization needs

**Key Point**: 
- **Exclusive paths**: A customer is either Individual OR Corporate, not both
- Indicated by **criterion** in notation

**Benefits**:
- Supports multiple business views
- Flexible analysis options
- Reflects real-world complexity

**Challenges**:
- More complex schema
- Users must understand which path to use
- Aggregation logic must handle multiple paths

---

### 5. Noncovering Hierarchies (Ragged / Level-Skipping)

**Definition**: Special case of generalized hierarchies where some members skip intermediate levels

**Also Known As**:
- **Ragged hierarchies**
- **Level-skipping hierarchies**

**Schema Level Characteristics**:
- Alternative paths obtained by **skipping intermediate levels**
- Multiple paths to same root
- Some paths shorter than others

**Instance Level Characteristics**:
- **Path length varies** from leaves to same parent
- Different members have **different depths**
- Some levels may be null/empty for some members

**Example 1**: Geographic hierarchy
```
City → State → Country
City → -----→ Country  (skip State)
```
- US cities: City → State → USA
- Singapore: City → Singapore (no state level)

**Example 2**: Product categorization
```
Product → Subcategory → Category → Department
Product → -----------→ Category → Department  (skip Subcategory)
Product → ----------------------→ Department  (skip Subcategory and Category)
```

**Visual Characteristics**:
- Paths of different lengths to same parent
- Some intermediate nodes empty/null
- "Holes" in hierarchy tree

**Handling Strategies**:
1. **Placeholder values**: Use "N/A" or "None" for missing levels
2. **Null values**: Allow nulls in parent references
3. **Direct linking**: Skip directly to next available level

**Challenges**:
- Aggregation must handle variable depths
- Queries need to account for missing levels
- Display/reporting must handle gaps gracefully

**Real-World Examples**:
- Geographic: Countries without states (Singapore, Monaco)
- Corporate: Employees reporting to CEO directly
- Product: Items without subcategory classification

---

## 4. Hierarchy Comparison Table

| Hierarchy Type | Paths | Relationship | Path Length | Use Case |
|----------------|-------|--------------|-------------|----------|
| **Balanced** | One | Many-to-one, mandatory | Same for all | Time, standard taxonomies |
| **Unbalanced** | One | Many-to-one, some optional | Variable | Organizations with optional levels |
| **Recursive** | One (self) | Self-referencing | Variable | Employee supervision, Bill-of-materials |
| **Generalized** | Multiple exclusive | Many-to-one per path | Can vary per path | Heterogeneous entities needing different classifications |
| **Noncovering (Ragged)** | Multiple (level-skipping) | Many-to-one, skips allowed | Variable within same path | Geography, products with inconsistent categorization |

---

## 5. MultiDim Conceptual Schema Example

### Northwind Data Warehouse Schema Components

A complete MultiDim schema includes:

1. **Multiple Dimensions** with hierarchies:
   - Time (Date → Month → Quarter → Year)
   - Customer (Customer → City → Country → Region)
   - Product (Product → Category)
   - Employee (Employee → Title)
   - Shipper

2. **Fact** (Sales):
   - Links to leaf levels of all dimensions
   - Contains measures: Quantity, Discount, Extended Price

3. **Cardinalities** on all relationships

4. **Descriptive attributes** in levels

5. **Key attributes** for aggregation

---

## 6. Design Process Implications

### Benefits of Conceptual Modeling

1. **Communication**: Bridge between business users and technical team
2. **Stability**: Less affected by implementation technology changes
3. **Clarity**: Visual representation easier to understand
4. **Validation**: Easier to verify requirements with stakeholders
5. **Documentation**: Better long-term maintenance

### Mapping to Implementation

**From Conceptual to Logical**:
- MultiDim → Star Schema
- MultiDim → Snowflake Schema
- Different hierarchies require different physical designs

**Design Decisions Based on Hierarchy Type**:
- **Balanced**: Simple star schema works well
- **Unbalanced/Recursive**: May need special handling (bridge tables, recursive queries)
- **Generalized**: Might need separate dimension tables per path
- **Noncovering**: May need placeholder values or nullable columns

---

## Summary: Key Takeaways

### Essential Concepts
1. **MultiDim** is conceptual model based on ER
2. **Five hierarchy types**: Balanced, Unbalanced, Recursive, Generalized, Noncovering
3. **Hierarchies** enable drill-down and roll-up operations
4. **Levels** have key (for grouping) and descriptive (for context) attributes
5. **Facts** connect dimensions and contain measures

### Hierarchy Selection Guidelines
- **Simple, regular data** → Balanced
- **Variable depth, same semantics** → Recursive
- **Optional levels** → Unbalanced
- **Multiple classification schemes** → Generalized
- **Inconsistent depth** → Noncovering (Ragged)

---

## Exam Tips

1. **Know all five hierarchy types** and their characteristics
2. **Distinguish schema vs instance level** properties
3. **Understand cardinality notation**: (min, max)
4. **Balanced hierarchies**: All paths same length, mandatory relationships
5. **Recursive hierarchies**: Self-referencing, same semantics
6. **Generalized vs Noncovering**:
   - Generalized: Multiple exclusive paths
   - Noncovering: Skips intermediate levels
7. **Key vs descriptive attributes**: Key for grouping, descriptive for information
8. **Criterion**: Shows alternative analysis paths
9. **Fact**: Central concept linking dimensions, contains measures
10. **Remember real-world examples** for each hierarchy type

### Common Exam Questions
- Identify hierarchy type from diagram
- Explain when to use each type
- Design conceptual schema for given scenario
- Map between conceptual and logical models