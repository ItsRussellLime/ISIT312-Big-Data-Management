# Topic 21-24: Apache Spark Complete Guide

## TOPIC 21: Spark Introduction

### 1. MapReduce Challenges

**Problems with Hadoop MapReduce**:
1. **Low-level Java API**: Difficult to use
2. **Persistent storage I/O**: Very inefficient for interactive/iterative computation
3. **Data sharing slow**: Replication, serialization, disk I/O overhead
4. **90%+ time on HDFS read-write**: Not on actual computation

**Data Sharing Problem**:
- Reuse data between jobs → Write to HDFS
- Substantial overhead from replication and disk I/O

---

### 2. What is Apache Spark?

**Definition**: Cluster computing platform designed to be **fast** and **general-purpose**

**Key Innovations**:
1. **In-memory computing**: Main performance advantage
2. **Extends MapReduce model**: Supports more computation types
3. **Unified environment**: One platform for multiple workloads

**Performance**:
- **100x faster in memory**
- **10x faster on disk** (compared to MapReduce)

---

### 3. Features of Spark

#### Speed
- Reduces read/write to persistent storage
- Stores intermediate data **in memory**

#### Multiple Language Support
- **Java**, **Scala**, **Python**, **R**, **SQL**

#### Advanced Analytics
- **SQL queries**
- **Streaming data**
- **Machine Learning (ML)**
- **Graph algorithms**

#### General Purpose
**Batch**: Traditional data processing
**Interactive**: Ad-hoc queries
**Iterative**: Machine learning algorithms
**Real-time**: Streaming analytics

---

### 4. Spark Architecture

**Three Key Components**:

#### 1. Driver Program
- Main Spark application
- Contains data processing logic
- Coordinates executors

#### 2. Executor
- **JVM process** on each worker node
- Runs tasks submitted by driver
- Processes actual data

#### 3. Task
- Subcomponent of job
- Smallest unit of work

---

### 5. Spark on YARN Modes

#### Client Mode
- Driver runs on **client machine**
- Good for **interactive** applications
- Client must stay connected

#### Cluster Mode
- Driver runs **inside cluster**
- Good for **production** jobs
- Client can disconnect after submission

---

### 6. Spark Components

**Spark Stack**:

```
┌──────────────────────────────────────┐
│  SparkSQL │ MLlib │ GraphX │ Streaming│
├──────────────────────────────────────┤
│         Spark Core (RDD API)         │
├──────────────────────────────────────┤
│    Cluster Manager (YARN/Mesos)      │
└──────────────────────────────────────┘
```

#### Spark Core
- **Foundation** for all functionality
- **In-memory computing**
- References datasets in external storage (HDFS)

#### Spark SQL
- **Structured/semi-structured data** processing
- **SchemaRDD** abstraction (now DataFrame/Dataset)

#### Spark Streaming
- **Streaming analytics**
- Leverages Spark Core's fast scheduling

#### MLlib
- **Machine Learning** framework
- Distributed algorithms

#### GraphX
- **Graph processing** framework
- Graph computation API

#### SparkR
- **R package** for Spark
- Light-weight frontend

---

### 7. Use Cases

**Data Scientists**:
- Analyze and model data
- Make predictions

**Data Engineers**:
- Build data pipelines
- Deploy production applications

---

## TOPIC 22: Spark Data Model

### 1. RDD (Resilient Distributed Dataset)

**Definition**: **Lowest-level** and **oldest** data abstraction

**Characteristics**:
- **Immutable** collection
- **Partitioned** across cluster
- Operated **in parallel**
- Each row is **Java object**
- **No schema** required

**Properties**:
1. List of **partitions**
2. **Function** for computing each split
3. List of **dependencies** on other RDDs
4. Optional: **Partitioner** (for key-value RDDs)
5. Optional: **Preferred locations** for computation

**Advantages**:
- ✅ **Flexible**: No fixed schema
- ✅ **Control**: Over data distribution and operations

**Disadvantages**:
- ❌ **Complex**: Must implement own functions (avg, count, max, etc.)
- ❌ **Less optimized**: Compared to DataFrames

**Creating RDD**:
```scala
// From collection
val strings = "hello hello !".split(" ")
val rdset = spark.sparkContext.parallelize(strings)

// From file
val lines = spark.sparkContext.textFile("sales.txt")
```

---

### 2. DataFrame

**Definition**: **Table** with **rows and columns** (structured data)

**Schema**: List of columns with types

**Key Features**:
- Can span **multiple systems** in cluster
- **Simplest** data model in Spark
- Consists of zero or more **partitions**

**Partitions**:
- Collection of rows on **single system**
- Spark processes all partitions **simultaneously**
- **Shuffle**: Share data among systems

**Creating DataFrame**:
```scala
val dataFrame = spark.read.json("/bigdata/people.json")
dataFrame.show()
dataFrame.printSchema()
```

**Advantages**:
- ✅ **Simple** to use
- ✅ **Optimized** performance
- ✅ **Schema** enforcement

---

### 3. SQL Tables/Views

**SQL on DataFrames**: Can register DataFrame as SQL table/view

**No Performance Overhead**: DataFrame and SQL table processing identical

**Types**:

#### Temporary View
```scala
dataFrame.createOrReplaceTempView("people")
val sqlDF = spark.sql("SELECT * FROM people")
```

#### Global View
```sql
CREATE GLOBAL VIEW just_usa_global AS
SELECT * FROM flights WHERE dest_country_name = 'United States'
```

#### Managed vs Unmanaged Tables

**Managed Table** (Internal):
- Stores **data and metadata**
- Equivalent to Hive internal table

**Unmanaged Table** (External):
- Stores **only metadata**
- Data location specified by user
- Equivalent to Hive external table

```sql
CREATE EXTERNAL TABLE hive_flights(...)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION '/mnt/defg/flight-data-hive/'
```

---

### 4. Dataset

**Definition**: Distributed collection of **typed data**

**Key Points**:
- **DataFrame = Dataset[Row]**
- **Strictly JVM**: Scala and Java only (not Python/R)
- Each row is **typed object**
- Uses **Encoder** for serialization

**Creating Dataset**:
```scala
case class Person(name: String, age: Long)
val caseClassDS = Seq(Person("Andy", 32)).toDS()
```

**Advantages**:
- ✅ **Type-safe**: Compile-time type checking
- ✅ **All DataFrame operations** supported

---

### Data Model Comparison

| Feature | RDD | DataFrame | Dataset |
|---------|-----|-----------|---------|
| **Type** | Untyped objects | Untyped rows | Typed objects |
| **Schema** | No | Yes | Yes |
| **API Level** | Low | High | High |
| **Type Safety** | Runtime | Runtime | Compile-time |
| **Optimization** | Manual | Automatic (Catalyst) | Automatic (Catalyst) |
| **Language** | All | All | Scala/Java only |
| **Use When** | Need control | Structured data, SQL | Type safety needed |

---

## TOPIC 23: Spark Operations

### 1. Scala Basics

**Why Scala**:
- Most supported language in Spark
- Spark implemented in Scala
- Unifies object-oriented and functional programming

**Hello World**:
```scala
object Hello {
    def main(args: Array[String]) = {
        println("Hello, world")
    }
}
```

**Variable Types**:
```scala
var x = 7           // Variable (mutable)
val x = 7           // Value (immutable)
lazy val x = {...}  // Computed when needed
def hello(name: String) = "Hello : " + name  // Function
```

---

### 2. Quick Start

**Start Spark Shell**:
```bash
bin/spark-shell --master local[*]    # Standalone
bin/spark-shell --master yarn        # YARN
```

**SparkSession**: Entry point to Spark
```scala
spark  // Already created in shell
val myRange = spark.range(1000).toDF("number")
myRange.show(2)
```

**Basic Operations**:
```scala
val textFile = spark.read.textFile("README.md")
textFile.count()                                    // 104
textFile.first()                                    // First line
textFile.filter(line => line.contains("Spark")).count()  // 20
```

---

### 3. Self-Contained Application

**SimpleApp.scala**:
```scala
import org.apache.spark.sql.SparkSession

object SimpleApp {
  def main(args: Array[String]) {
    val spark = SparkSession.builder
      .appName("Simple Application")
      .config("spark.master", "local[*]")
      .getOrCreate()
    
    val logData = spark.read.textFile("README.md").cache()
    val numAs = logData.filter(line => line.contains("a")).count()
    val numBs = logData.filter(line => line.contains("b")).count()
    println(s"Lines with a: $numAs, Lines with b: $numBs")
    
    spark.stop()
  }
}
```

**Compile and Run**:
```bash
scalac -classpath "$SPARK_HOME/jars/*" SimpleApp.scala
jar cvf app.jar SimpleApp*.class
$SPARK_HOME/bin/spark-submit --master local[*] --class SimpleApp app.jar
```

---

### 4. Web UI

- **Port**: 4040 (default)
- **Shows**: Running tasks, executors, storage usage
- Monitor application execution

---

### 5. RDD Operations

**Transformations**:
```scala
// Create RDD
val words = spark.sparkContext.parallelize(myCollection, 2)

// Distinct and count
words.distinct().count()

// Filter
val onlyS = words.filter(word => word.startsWith("S"))

// Sort
words.sortBy(word => word.length() * -1).take(2)

// Random split
val splits = words.randomSplit(Array(0.5, 0.5))

// Reduce
words.reduce((left, right) => if (left.length >= right.length) left else right)
```

**Key-Value Operations**:
```scala
val lines = sc.textFile("data.txt")
val pairs = lines.map(s => (s, 1))
val counts = pairs.reduceByKey((a, b) => a + b)
```

**Common Transformations**:
- `map(func)`: Apply function to each element
- `filter(func)`: Select elements
- `union(otherRDD)`: Combine RDDs
- `intersection(otherRDD)`: Common elements
- `distinct()`: Remove duplicates
- `groupByKey()`: Group by key
- `sortByKey()`: Sort by key

---

### 6. Dataset Operations

```scala
case class Flight(DEST_COUNTRY_NAME: String, ORIGIN_COUNTRY_NAME: String, count: BigInt)

val flightsDF = spark.read.parquet("2010-summary.parquet")
val flights = flightsDF.as[Flight]  // Cast to Dataset

// Filter
flights.filter(f => f.ORIGIN_COUNTRY_NAME == f.DEST_COUNTRY_NAME).first()

// Map
val destinations = flights.map(f => f.DEST_COUNTRY_NAME)
```

---

### 7. DataFrame Operations

**Create DataFrame**:
```scala
val df = spark.read.json("people.json")
df.show()
df.printSchema()
```

**Select**:
```scala
df.select($"name", $"age" + 1).show()
```

**Filter**:
```scala
df.filter($"age" > 21).show()
```

**Group By**:
```scala
df.groupBy("age").count().show()
```

**Register as SQL View**:
```scala
df.createOrReplaceTempView("people")
val sqlDF = spark.sql("SELECT * FROM people")
sqlDF.show()
```

---

### 8. Transformations vs Actions

**Transformations** (Lazy):
- Return new DataFrame/Dataset
- Not executed until action
- Examples: `select()`, `filter()`, `groupBy()`, `map()`

**Actions** (Eager):
- Return results or write to storage
- Trigger computation
- Examples: `show()`, `count()`, `first()`, `collect()`

**Lazy Evaluation Benefits**:
- Reduce passes over data
- Optimize execution plan
- No need to group operations like MapReduce

---

### 9. Spark SQL

**Two Data Abstractions**:
1. **DataFrame**: Available in all languages
2. **Dataset**: Scala/Java only

**SQL Usage**:
```scala
df.createOrReplaceTempView("dfTable")

spark.sql("""
  SELECT DEST_COUNTRY_NAME, sum(count) 
  FROM dfTable
  GROUP BY DEST_COUNTRY_NAME
""")
.where("DEST_COUNTRY_NAME like 'S%'")
.where("'sum(count)' > 10")
.show(2)
```

**Features**:
- Standard SQL statements
- ANSI SQL:2003 subset
- High-level operations for ETL
- Same execution engine for SQL and DataFrame API

---

## TOPIC 24: Spark Streaming

### 1. Why Stream Processing?

**Definition**: Continuously incorporating new data to compute results

**Batch vs Stream**:
| Aspect | Batch | Stream |
|--------|-------|--------|
| **Data** | Fixed set | Unbounded set |
| **Timeliness** | Low requirement | Near real-time |
| **Processing** | Periodic (hours/days) | Continuous (seconds) |

**Stream Sources**:
- Bank transactions
- Website clicks
- IoT sensor readings
- Scientific observations
- Manufacturing processes

---

### 2. Use Cases

**Stream Processing Applications**:
1. **Notifications and alerting**
2. **Real-time reporting**
3. **Incremental ETL**
4. **Real-time decision making**
5. **Online machine learning**

---

### 3. Stream Processing Challenges

**Key Challenges**:
1. **Out-of-order data**: Event time vs processing time
2. **State management**: Maintain large state
3. **High throughput**: Process many events/second
4. **Exactly-once processing**: Despite failures
5. **Load balancing**: Handle stragglers
6. **Low latency**: Respond quickly
7. **Joins**: With external data sources
8. **Output updates**: How to handle new events
9. **Transactional writes**: To output systems
10. **Runtime updates**: Change business logic

---

### 4. Spark Streaming Modules

**Two Modules**:

#### Spark Streaming (Old)
- Based on **low-level RDD API**
- Available since Spark 1.2
- More complex to use

#### Structured Streaming (New)
- Based on **Spark SQL engine**
- Available since Spark 2.1
- Recommended approach

---

### 5. Structured Streaming Quick Start

**Word Count Example**:
```scala
// Read stream
val lines = spark.readStream
  .format("socket")
  .option("host", "localhost")
  .option("port", 9999)
  .load()

import spark.implicits._

// Process stream
val words = lines.as[String].flatMap(_.split(" "))
val wordCounts = words.groupBy("value").count()

// Write stream
val query = wordCounts.writeStream
  .outputMode("complete")  // Accumulate results
  .format("console")       // Output to console
  .start()
```

**Start Data Source** (Terminal 1):
```bash
nc -lk 9999
apache spark
apache hadoop
```

**Output** (Terminal 2 - Spark shell):
```
+-------+-----+
|  value|count|
+-------+-----+
| apache|    2|
|  spark|    1|
| hadoop|    1|
+-------+-----+
```

---

### 6. Programming Model

**Key Idea**: Treat **live data stream** as **continuously appended table**

**Input Table**: Unbounded table with new rows appended

**Result Table**: Output of query on Input Table

**Process**:
1. New data arrives → Appended to Input Table
2. Query runs incrementally → Updates Result Table
3. Every trigger interval (e.g., every X seconds)
4. Changed results written to **sink**

**Conceptual Flow**:
```
Stream → Input Table → Query → Result Table → Sink
         (Append)      (Transform) (Update)   (Write)
```

---

### 7. Structured Streaming Features

**Advantages**:
- ✅ **Fast**: In-memory processing
- ✅ **Scalable**: Distributed across cluster
- ✅ **Fault-tolerant**: Recover from failures
- ✅ **End-to-end exactly-once**: Guaranteed processing
- ✅ **No explicit streaming logic**: Write like batch queries

**Programming Model Benefits**:
- Same as batch processing
- Express as standard SQL/DataFrame operations
- Spark handles incremental execution

---

## Summary: Complete Spark Guide

### Core Concepts
1. **RDD**: Low-level, flexible, untyped
2. **DataFrame**: High-level, structured, optimized
3. **Dataset**: High-level, typed, type-safe (Scala/Java)

### Key Features
- **In-memory**: 100x faster than MapReduce
- **Unified**: One platform for batch, interactive, streaming, ML
- **Multiple languages**: Scala, Java, Python, R, SQL
- **Lazy evaluation**: Optimize execution plans

### Architecture
- **Driver**: Coordinates execution
- **Executors**: Process data on workers
- **Tasks**: Smallest units of work

### Operations
- **Transformations**: Lazy, return new DF/DS
- **Actions**: Eager, trigger computation

### Streaming
- **Structured Streaming**: Treat stream as table
- **Programming model**: Same as batch processing
- **Exactly-once**: Guaranteed processing semantics

---

## Exam Tips

1. **Know data model hierarchy**: RDD < DataFrame < Dataset
2. **Transformations vs Actions**: Lazy vs eager
3. **When to use each**:
   - RDD: Need low-level control
   - DataFrame: Structured data, best performance
   - Dataset: Type safety required (Scala/Java)
4. **Spark faster than MapReduce**: In-memory processing
5. **Lazy evaluation**: Optimizes execution plan
6. **SparkSession**: Entry point for Spark 2.x+
7. **Structured Streaming**: Continuous append to Input Table
8. **Output modes**: Complete, Append, Update
9. **Scala basics**: val (immutable), var (mutable), def (function)
10. **Web UI**: Port 4040, monitor execution

### Common Exam Questions
- Compare RDD, DataFrame, Dataset
- Explain lazy evaluation benefits
- Write simple Spark transformations
- Describe streaming programming model
- When to use Spark vs MapReduce
- Explain in-memory computing advantage