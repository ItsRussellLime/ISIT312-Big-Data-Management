# Topic 13: Data Warehouse Concepts

## 1. OLAP vs OLTP

### OLTP (Online Transaction Processing)

**Definition**: Traditional database systems designed for day-to-day operations

**Characteristics**:
- **Fast, concurrent access** to data
- **Transaction processing** and concurrency control
- Focus on **online update** and **data consistency**
- Also known as **operational databases**

**Data Properties**:
- **Detailed data** at finest granularity
- **No historical data** (current state only)
- **Highly normalized** schema
- **Poor performance** on complex queries with joins and aggregation

**Example Query**: 
- "What are the pending orders for customer X?"
- Simple, transactional, accessing few records

---

### OLAP (Online Analytical Processing)

**Definition**: New paradigm for **data analysis** requiring different database design

**Key Differences from OLTP**:
- **Focus**: Analytical queries vs. transactions
- **Normalization**: Not good for analytical queries (requires many joins)
- **Query Load**: Heavy query load vs. many small transactions
- **Indexing**: OLTP indexing inefficient for OLAP (OLAP needs aggregation)

**Example Query**:
- "What is the total sales amount by product and by customer?"
- Complex, analytical, aggregating large volumes

---

### Data Warehouse Definition

**Data Warehouse**: Large repositories that:
1. **Consolidate data** from different sources (internal and external)
2. Updated **offline** (not real-time)
3. Follow the **multidimensional data model**
4. **Designed and optimized** for efficient OLAP queries

### OLTP vs OLAP Comparison Table

| Aspect | OLTP | OLAP |
|--------|------|------|
| **Purpose** | Day-to-day operations | Data analysis |
| **Focus** | Transactions | Analytical queries |
| **Data** | Current, detailed | Historical, aggregated |
| **Schema** | Highly normalized | Multidimensional/denormalized |
| **Queries** | Simple, few records | Complex, aggregation |
| **Updates** | Frequent, online | Infrequent, offline (batch) |
| **Performance Goal** | Fast concurrent access | Fast complex queries |
| **Example** | Order processing | Sales analysis |

---

## 2. The Multidimensional Model

### Data Cube Concept

**Definition**: A view of data in **n-dimensional space**

**Components**:
1. **Dimensions**: Perspectives used to analyze data
2. **Facts**: Cells containing numeric values (measures)

**Example**: Three-dimensional cube for sales data
- **Dimensions**: Product, Time, Customer
- **Measure**: Quantity (units sold)

### Dimensions

**Definition**: Perspectives or contexts for analysis

**Properties**:
- Have **attributes** that describe them
- Example: Product dimension has ProductNumber, UnitPrice attributes

**Instances**: Called **members**
- Example: "Seafood" and "Beverages" are **members** of Product dimension at Category granularity

### Facts and Measures

**Facts**: Cells of the data cube

**Measures**: Numeric values associated with facts
- Example: **Quantity** of units sold by category, quarter, and city
- Multiple measures possible: Quantity, Amount, Profit, etc.

**Data Granularity**: Level of detail for measures in each dimension
- Example: Sales at Category (Product), Quarter (Time), City (Customer)

### Cube Characteristics

**Sparse vs Dense**:
- **Sparse**: Not all combinations exist (typical case)
  - Example: Not all customers ordered all products in all quarters
- **Dense**: Most combinations have values

---

### Hierarchies

**Definition**: Allow viewing data at **several granularities**

**Structure**:
- Sequence of mappings from **lower-level (child)** to **higher-level (parent)** concepts
- Lower level = **child**, Higher level = **parent**

**Dimension Schema**: Hierarchical structure of a dimension

**Dimension Instance**: All members at all levels in a dimension

### Example Hierarchies

**Product Hierarchy**:
```
All Products
    └── Category (Seafood, Beverages, etc.)
        └── Product (Salmon, Tuna, etc.)
```

**Time Hierarchy**:
```
All Time
    └── Year
        └── Quarter (Q1, Q2, Q3, Q4)
            └── Month (Jan, Feb, Mar, etc.)
                └── Day
```

**Customer Hierarchy**:
```
All Customers
    └── Country (France, USA, etc.)
        └── Region/State
            └── City (Paris, Lyon, etc.)
                └── Customer
```

### Granularity Examples

- **Finer granularity**: Month (instead of Quarter)
- **Coarser granularity**: Country (instead of City)
- Hierarchies enable moving between granularities

---

## 3. Measures Classification

### By Additivity

#### 1. Additive Measures
**Definition**: Can be meaningfully summarized using addition **along ALL dimensions**

**Examples**:
- Sales quantity
- Sales amount
- Cost

**Most common type** of measures

#### 2. Semi-Additive Measures
**Definition**: Can be meaningfully summarized using addition **along SOME dimensions**

**Example**: 
- **Inventory quantities**: Cannot be added along Time dimension
  - Adding inventory from Q1 + Q2 makes no sense
  - But can sum across products or locations

#### 3. Non-Additive Measures
**Definition**: Cannot be meaningfully summarized using addition **across ANY dimension**

**Examples**:
- Item price
- Cost per unit
- Exchange rate
- Ratios and percentages

**Note**: May use other aggregation functions (average, min, max)

---

### By Computation Method

#### 1. Distributive Measures
**Definition**: Aggregation function can be computed in a **distributed way**

**Functions**: count, sum, min, max

**Counter-example**: 
- **distinct count** is NOT distributive
- Example: S = {3, 3, 4, 5, 8, 4, 7, 3, 8}
  - Partitions: {3, 3, 4}, {5, 8, 4}, {7, 3, 8}
  - Distinct counts: 2, 3, 3 → Total: 8
  - But actual distinct count over original set: 5

#### 2. Algebraic Measures
**Definition**: Aggregation function expressed as **scalar function of distributive measures**

**Example**: 
- **Average** = sum / count
- Both sum and count are distributive
- Therefore average is algebraic

---

## 4. OLAP Operations

### Core Operations Overview

1. **Roll-up**: Aggregate to coarser granularity (go up hierarchy)
2. **Drill-down**: Disaggregate to finer granularity (go down hierarchy)
3. **Slice**: Fix one dimension to a single value (reduce dimensions)
4. **Dice**: Fix multiple dimensions to ranges (create sub-cube)
5. **Pivot (Rotate)**: Change axis orientation without changing granularity
6. **Sort**: Order members by some criteria

---

### Operation Examples

**Starting Cube**: Quarterly sales (in thousands) by product category and customer cities for 2012

#### 1. Roll-Up
**Action**: Compute sales by **Country** instead of City
- Aggregates from City → Country along Customer dimension
- **Coarser granularity**

**Result**: See if Seafood sales in France higher in Q1

#### 2. Drill-Down
**Action**: Disaggregate Time from **Quarter** to **Month**
- Go to finer granularity
- Find which specific month caused Q1 spike

#### 3. Slice
**Action**: Fix Customer.City = 'Paris'
- Reduces 3D cube to **2D** (Product × Time)
- Result: Collection of time series for Paris only

#### 4. Dice
**Action**: Select subset:
- Cities: Lyon OR Paris
- Quarters: Q1 OR Q2
- Result: **3D sub-cube** with restricted ranges

#### 5. Pivot (Rotate)
**Action**: Change axis orientation
- Put Time on x-axis instead of Product
- **No granularity change**, just visualization

#### 6. Sort
**Action**: Order products by name
- Alphabetical ordering of Product members

---

## 5. OLAP Algebraic Operators

### Roll-Up Operations

#### Basic Roll-Up
**Syntax**:
```
ROLLUP(CubeName, (Dimension → Level)*, AggFunction(Measure)*)
```

**Example**:
```sql
ROLLUP(Sales, Customer → Country, SUM(Quantity))
```
- Aggregates Sales cube
- Customer dimension to Country level
- Using SUM on Quantity measure

#### Extended Roll-Up (ROLLUP*)
**Syntax**:
```
ROLLUP*(CubeName, [(Dimension → Level)*], AggFunction(Measure)*)
```

**Difference**: Drops all dimensions **not involved** in operation

**Examples**:
```sql
ROLLUP*(Sales, Time → Quarter, SUM(Quantity))
ROLLUP*(Sales, Time → Quarter, COUNT(Product) AS ProdCount)
```

#### Recursive Roll-Up (RECROLLUP)
**Syntax**:
```
RECROLLUP(CubeName, Dimension → Level, AggFunction(Measure)*)
```

**Purpose**: Aggregates over **recursive hierarchy** (level rolls up to itself)

---

### Drill-Down Operation

**Syntax**:
```
DRILLDOWN(CubeName, (Dimension → Level)*)
```

**Purpose**: Move from general to detailed level in hierarchy

**Example**:
```sql
DRILLDOWN(Sales, Time → Month)
```
- Disaggregates Time dimension to Month level

---

### Sort Operation

**Syntax**:
```
SORT(CubeName, Dimension, Expression [ASC | DESC])
```

**Purpose**: Sort members of dimension by expression value

**Example**:
```sql
SORT(Sales, Product, NAME)
```
- Sorts Product dimension members alphabetically
- **NAME**: Predefined keyword representing member name

---

### Pivot Operation

**Syntax**:
```
PIVOT(CubeName, (Dimension → Axis)*)
```

**Purpose**: Change axes without altering granularity

**Example**:
```sql
PIVOT(Sales, Time → X, Customer → Y, Product → Z)
```
- Assigns dimensions to specific axes (X, Y, Z, X₁, Y₁, Z₁, ...)

---

### Slice Operation

**Syntax**:
```
SLICE(CubeName, Dimension, Level = Value)
```

**Purpose**: 
- Fix single value in dimension level
- **Drops that dimension** from result
- Other dimensions unchanged

**Assumptions**:
- Cube granularity must be at specified level

**Example**:
```sql
SLICE(Sales, Customer, City = 'Paris')
```
- Fixes Customer dimension to Paris
- Result: 2D cube (Product × Time)

---

### Dice Operation

**Syntax**:
```
DICE(CubeName, φ)
```

**Purpose**: Create sub-cube by applying Boolean conditions

**Example**:
```sql
DICE(Sales, 
     (Customer.City = 'Paris' OR Customer.City = 'Lyon') 
     AND 
     (Time.Quarter = 'Q1' OR Time.Quarter = 'Q2'))
```
- Results in 3D sub-cube
- Only specified cities and quarters
- φ is Boolean condition over dimension levels, attributes, measures

---

## 6. Data Warehouse Architecture

### Architecture Tiers

Data warehouse follows **multi-tier architecture**:

1. **Back-End Tier**
2. **Data Warehouse Tier**
3. **OLAP Tier**
4. **Front-End Tier**

---

### 1. Back-End Tier

**Components**:

#### ETL Tools (Extract, Transform, Load)
- **Extract**: Data from operational databases and sources
- **Transform**: Clean, integrate, format data
- **Load**: Feed data into data warehouse

#### Data Staging Area
- **Intermediate database**
- All **data integration and transformation** processes run here
- **Before loading** into data warehouse
- Temporary storage during ETL process

**Data Sources**:
- Operational databases (internal)
- External data sources

---

### 2. Data Warehouse Tier

**Components**:

#### Enterprise Data Warehouse
- **Central repository**
- Consolidated data from all sources
- Organization-wide view

#### Data Marts (Optional)
- **Subset** of data warehouse
- **Department/function-specific** (e.g., Sales, Finance)
- Smaller, focused datasets

#### Metadata Repository
- Stores **information about data warehouse**
- Data definitions, schemas
- ETL processes, transformations
- Data lineage and quality metrics

---

### 3. OLAP Tier

**Component**: OLAP Server

**Purpose**:
- Provides **multidimensional view** of data
- **Independent of physical storage** (relational or multidimensional)
- Processes OLAP operations (roll-up, drill-down, slice, dice, pivot)

**Functions**:
- Query processing
- Aggregate pre-computation
- Cache management

---

### 4. Front-End Tier

**Purpose**: Data analysis and visualization

**Client Tools**:
1. **OLAP Tools**: Multidimensional analysis
2. **Reporting Tools**: Standard reports, dashboards
3. **Statistical Tools**: Advanced analytics
4. **Data Mining Tools**: Pattern discovery, predictive models

**Users**: Business analysts, data scientists, managers

---

### Architecture Diagram Flow

```
Data Sources → ETL Tools → Staging Area → Data Warehouse/Data Marts
                                              ↓
                                         Metadata Repository
                                              ↓
                                         OLAP Server
                                              ↓
                                    Front-End Client Tools
```

---

## Summary Table: Key Concepts

| Concept | Key Points |
|---------|-----------|
| **OLTP** | Transactions, detailed, normalized, current data |
| **OLAP** | Analysis, aggregated, multidimensional, historical |
| **Data Cube** | n-dimensional view: dimensions + facts/measures |
| **Hierarchies** | Multiple granularities: child → parent |
| **Roll-Up** | Aggregate to coarser granularity (up hierarchy) |
| **Drill-Down** | Disaggregate to finer granularity (down hierarchy) |
| **Slice** | Fix one dimension value → reduce dimensions |
| **Dice** | Apply Boolean conditions → create sub-cube |
| **Pivot** | Rotate axes → change visualization |
| **ETL** | Extract, Transform, Load → data integration |

---

## Exam Tips

1. **Know OLTP vs OLAP differences** - frequently tested
2. **Understand measure types**:
   - Additive (sum across all dimensions)
   - Semi-additive (sum across some dimensions)
   - Non-additive (cannot sum)
3. **Master OLAP operations**:
   - Roll-up = coarser, Drill-down = finer
   - Slice = fix one dimension
   - Dice = Boolean conditions
4. **Hierarchies**: Understand parent-child relationships
5. **Architecture tiers**: Know what each tier does
6. **Know algebraic notation** for operations
7. **Granularity**: Level of detail in each dimension
8. **Data cube**: Dimensions (perspectives) vs Facts (measures)
9. **ETL process**: Extract → Transform → Load
10. **Distributive vs Algebraic measures** - understand computation differences