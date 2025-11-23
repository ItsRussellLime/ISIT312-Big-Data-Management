# column value
scan 'users', {FILTER => "SingleColumnValueFilter('info', 'age', >, 'binary:25')"}

# Greater than/less than
scan 'products', {FILTER => "SingleColumnValueFilter('pricing', 'price', <, 'binary:100')"}
```

**5. Compound Filters**:
```ruby
# AND condition
scan 'users', {FILTER => "ColumnPrefixFilter('a') AND ValueFilter(>, 'binary:100')"}

# OR condition
scan 'users', {FILTER => "ColumnPrefixFilter('name') OR ColumnPrefixFilter('email')"}

# Complex combination
scan 'users', {FILTER => "(PrefixFilter('user0') AND ValueFilter(=, 'substring:NY')) OR RowFilter(=, 'regexstring:admin.*')"}
```

**6. Page Filter**:
```ruby
# Limit per page
scan 'users', {FILTER => "PageFilter(10)"}
```

**Batch Operations**:

**Batch Put** (Java API concept):
- Improves performance for multiple puts
- Reduces network round trips
- More efficient than individual puts

**Batch Get** (Java API concept):
- Retrieve multiple rows in single operation
- More efficient than multiple individual gets

**Java API Operations** (Conceptual - No coding in exam):

**Basic Structure**:
```java
// Connection setup
Configuration config = HBaseConfiguration.create();
Connection connection = ConnectionFactory.createConnection(config);
Table table = connection.getTable(TableName.valueOf("users"));

// Put operation
Put put = new Put(Bytes.toBytes("user001"));
put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"), Bytes.toBytes("John"));
table.put(put);

// Get operation
Get get = new Get(Bytes.toBytes("user001"));
Result result = table.get(get);
byte[] value = result.getValue(Bytes.toBytes("info"), Bytes.toBytes("name"));

// Scan operation
Scan scan = new Scan();
scan.setStartRow(Bytes.toBytes("user001"));
scan.setStopRow(Bytes.toBytes("user999"));
ResultScanner scanner = table.getScanner(scan);
for (Result res : scanner) {
    // Process result
}

// Delete operation
Delete delete = new Delete(Bytes.toBytes("user001"));
table.delete(delete);

// Close resources
table.close();
connection.close();
```

**Operation Best Practices**:

**1. Row Key Design for Operations**:
```
Good Design:
- Query: Get user's posts
- Row Key: userid_timestamp
- Operation: scan 'posts', {STARTROW => 'user001_', STOPROW => 'user001_~'}

Bad Design:
- Row Key: timestamp_userid
- Would require full table scan to find user's posts
```

**2. Use Filters to Reduce Data Transfer**:
```ruby
# Bad: Get entire row, filter client-side
scan 'users'
# Then filter in application code

# Good: Filter server-side
scan 'users', {FILTER => "SingleColumnValueFilter('info', 'age', >, 'binary:18')"}
```

**3. Use Appropriate Caching**:
```ruby
# Small dataset
scan 'users', {CACHING => 100}

# Large dataset
scan 'users', {CACHING => 1000}
```

**4. Limit Versions Retrieved**:
```ruby
# Only need latest
get 'users', 'user001', {VERSIONS => 1}

# Need history
get 'users', 'user001', {COLUMN => 'info:balance', VERSIONS => 10}
```

**5. Use Batch Operations**:
- Batch multiple puts/gets when possible
- Reduces network overhead
- Improves throughput

**Performance Considerations**:

**Get Operations**:
- Very fast (single row by key)
- O(log n) complexity
- Uses block cache for frequently accessed rows
- Typical latency: single-digit milliseconds

**Scan Operations**:
- Can be slow on large tables
- Always use STARTROW and STOPROW when possible
- Use filters to reduce data transfer
- Consider caching parameter
- Use LIMIT to restrict results
- Typical: Start with narrow scans, widen if needed

**Put Operations**:
- Fast for single row
- Batch for multiple rows
- Writes go to MemStore first (in-memory)
- Flushed to HFiles periodically
- Consider write buffer size for bulk loads

**Delete Operations**:
- Fast (creates tombstone marker)
- Actual data removed during compaction
- Can impact scan performance (scans must skip tombstones)
- Consider delete patterns in design

**Common Use Cases**:

**1. Time-Series Data**:
```ruby
# Row key: sensorid_reversed_timestamp
put 'sensor_data', 'sensor001_9999999999999-1609459200000', 'reading:temp', '72.5'

# Query recent readings
scan 'sensor_data', {
  STARTROW => 'sensor001_9999999999999-1640995200000',
  STOPROW => 'sensor001_9999999999999-1609459200000',
  LIMIT => 100
}
```

**2. User Profile**:
```ruby
# Store user data
put 'users', 'user123', 'info:name', 'John Doe'
put 'users', 'user123', 'info:email', 'john@example.com'
put 'users', 'user123', 'prefs:theme', 'dark'
put 'users', 'user123', 'prefs:language', 'en'

# Get complete profile
get 'users', 'user123'

# Get only preferences
get 'users', 'user123', 'prefs'
```

**3. Web Crawling/URL Storage**:
```ruby
# Row key: reversed_domain
put 'websites', 'com.example.www', 'content:html', '<html>...'
put 'websites', 'com.example.www', 'metadata:title', 'Example Site'
put 'websites', 'com.example.www', 'metadata:crawled_at', '2023-01-01'

# Scan all subdomains
scan 'websites', {STARTROW => 'com.example.', STOPROW => 'com.example.~'}
```

**4. Social Media Feed**:
```ruby
# Row key: userid_reversed_timestamp
put 'posts', 'user001_9999999999-1609459200', 'post:content', 'Hello world!'
put 'posts', 'user001_9999999999-1609459200', 'engagement:likes', '0'

# Get user's recent posts
scan 'posts', {
  STARTROW => 'user001_',
  STOPROW => 'user001_~',
  LIMIT => 20
}
```

**Administrative Operations**:

**Check Status**:
```ruby
status
status 'summary'
status 'simple'
status 'detailed'
```

**Table Management**:
```ruby
# Check if table exists
exists 'users'

# Get table regions
locate_region 'users', 'user001'

# Split table
split 'users'

# Compact table
major_compact 'users'
compact 'users'
```

**Namespace Operations**:
```ruby
# Create namespace
create_namespace 'production'

# List namespaces
list_namespace

# Describe namespace
describe_namespace 'production'

# Create table in namespace
create 'production:users', 'info'

# Drop namespace
drop_namespace 'production'
```

**Troubleshooting Commands**:
```ruby
# Show all regions for table
list_regions 'users'

# Flush MemStore to disk
flush 'users'

# Check region server logs
# (done at OS level, not in shell)
```

**Data Import/Export**:
```ruby
# Export table (command line, not shell)
# hbase org.apache.hadoop.hbase.mapreduce.Export users /export/users

# Import table
# hbase org.apache.hadoop.hbase.mapreduce.Import users /export/users

# Bulk load (for large datasets)
# Use MapReduce to generate HFiles, then bulk load
```

**Security Operations**:
```ruby
# Grant permissions
grant 'username', 'RW', 'tablename'
grant 'username', 'RWXCA', 'tablename'

# Revoke permissions
revoke 'username', 'tablename'

# Show permissions
user_permission 'tablename'
```

**Key Takeaways**:
1. **Put**: Insert/update cells, creates versions
2. **Get**: Retrieve specific row by key (very fast)
3. **Scan**: Retrieve multiple rows, use filters and limits
4. **Delete**: Remove cells/rows (creates tombstone)
5. **Always design row keys for access patterns**
6. **Use filters to reduce data transfer**
7. **Batch operations for better performance**
8. **Scans can be expensive - optimize with ranges and filters**
9. **Atomic operations only at row level**
10. **HBase Shell for administration and testing**

---

## Topic 17: Spark Introduction

**Summary**: Apache Spark is a fast, unified analytics engine for big data processing that provides in-memory computation achieving up to 100x faster performance than traditional MapReduce by caching intermediate results in memory rather than writing to disk. Supporting multiple programming languages (Scala, Python, Java, R) and providing unified APIs for batch processing (Spark Core), SQL queries (Spark SQL), machine learning (MLlib), graph processing (GraphX), and stream processing (Spark Streaming), Spark's core abstraction is the Resilient Distributed Dataset (RDD) which enables fault-tolerant parallel operations through lazy evaluation and lineage tracking. Unlike MapReduce's rigid two-stage processing, Spark builds a Directed Acyclic Graph (DAG) of operations, optimizing execution through pipelining transformations and efficiently managing shuffles, making it ideal for iterative algorithms, interactive queries, and complex multi-stage workflows.

**Spark Overview**:

**Key Features**:
- **In-Memory Processing**: Cache data in memory across operations
- **Unified Platform**: Single framework for multiple workloads
- **Multi-Language Support**: Scala, Python (PySpark), Java, R (SparkR)
- **Lazy Evaluation**: Operations not executed until action called
- **Fault Tolerance**: Automatic recovery through lineage
- **Speed**: 100x faster than MapReduce for in-memory, 10x faster on disk

**Spark vs MapReduce**:

| Aspect | MapReduce | Spark |
|--------|-----------|-------|
| **Processing Speed** | Slower (disk-based) | Much faster (in-memory) |
| **Execution Model** | Two-stage (Map-Reduce) | DAG-based (multi-stage) |
| **Intermediate Results** | Written to disk | Kept in memory |
| **Ease of Use** | More verbose (Java) | Concise API (Python, Scala) |
| **Iterative Processing** | Inefficient (reload data) | Efficient (cache data) |
| **Real-Time Processing** | Not supported | Supported (Streaming) |
| **Interactive Queries** | Not suitable | Well-suited |
| **Machine Learning** | Require multiple jobs | Built-in MLlib |
| **Best For** | One-pass batch processing | Iterative, interactive, real-time |

**When to Use Spark**:
- Iterative algorithms (machine learning)
- Interactive data exploration
- Real-time stream processing
- Graph processing
- Multiple operations on same dataset
- Complex workflows

**When to Use MapReduce**:
- Simple one-pass transformations
- Very large datasets that don't fit in memory
- When Spark not available
- Linear batch processing

**Spark Architecture**:

**Components**:

**1. Spark Core**:
- Foundation of Spark platform
- Provides basic functionality
- RDD API
- Task scheduling
- Memory management
- Fault recovery
- Storage system interaction

**2. Spark SQL**:
- Work with structured data
- DataFrame and Dataset APIs
- SQL queries on data
- Integration with Hive
- Catalyst query optimizer
- Support for various data sources (JSON, Parquet, JDBC)

**3. Spark Streaming**:
- Real-time stream processing
- Processes data in micro-batches
- DStream (Discretized Stream) abstraction
- Integration with Kafka, Flume, HDFS
- Window operations
- Stateful processing

**4. MLlib (Machine Learning Library)**:
- Scalable machine learning algorithms
- Classification, regression, clustering
- Collaborative filtering
- Dimensionality reduction
- Feature extraction
- Model evaluation

**5. GraphX**:
- Graph processing framework
- Graph algorithms (PageRank, triangle counting)
- Graph operations (filter, mapVertices)
- Pregel API for iterative graph computation

**Cluster Architecture**:

**Cluster Manager Types**:
- **Standalone**: Spark's built-in cluster manager
- **YARN**: Hadoop's resource manager
- **Mesos**: General-purpose cluster manager
- **Kubernetes**: Container orchestration platform

**Execution Model**:

**Components**:

**1. Driver Program**:
- Runs main() function
- Creates SparkContext
- Converts user program into tasks
- Schedules tasks on executors
- Coordinates execution

**2. SparkContext**:
- Entry point to Spark functionality
- Connects to cluster manager
- Acquires executors on cluster
- Sends application code to executors
- Sends tasks to executors

**3. Cluster Manager**:
- Allocates resources across applications
- YARN, Mesos, Standalone, or Kubernetes
- Not part of Spark (except Standalone)

**4. Executors**:
- Worker processes on cluster nodes
- Run tasks assigned by driver
- Store data for cached RDDs
- Return results to driver
- Multiple executors per application

**5. Tasks**:
- Unit of work sent to executor
- Applied to one partition of data
- Many tasks per job

**Execution Flow**:
```
1. Driver creates SparkContext
2. SparkContext connects to Cluster Manager
3. Cluster Manager allocates executors
4. Driver sends application code to executors
5. Driver converts program into DAG of stages
6. Stages divided into tasks
7. Tasks sent to executors
8. Executors run tasks and store results
9. Results returned to driver
10. SparkContext stopped, resources released
```

**Deployment Modes**:

**1. Cluster Mode**:
- Driver runs on worker node
- Cluster manager launches driver
- Best for production
- Driver failure = job failure (but can restart)

**2. Client Mode**:
- Driver runs on client machine
- Cluster manager launches executors
- Good for interactive/development
- Client must stay connected

**3. Local Mode**:
- Everything runs in single JVM
- For testing and development
- Syntax: `local[n]` where n = number of threads

**RDD (Resilient Distributed Dataset)**:

**Characteristics**:
- **Resilient**: Fault-tolerant through lineage
- **Distributed**: Data spread across cluster
- **Dataset**: Collection of partitioned elements
- **Immutable**: Once created, cannot be changed
- **Lazy Evaluated**: Computed only when action called
- **Type-Safe**: Strongly typed (in Scala, Java)

**Five Main Properties**:
1. List of partitions
2. Function to compute each partition
3. List of dependencies on other RDDs
4. Optionally, partitioner for key-value RDDs
5. Optionally, list of preferred locations

**RDD Operations**:

**Two Types**:
1. **Transformations**: Create new RDD (lazy)
2. **Actions**: Return value to driver or write to storage (trigger execution)

**Key Concepts**:

**Lazy Evaluation**:
- Transformations not immediately computed
- Build up execution plan (DAG)
- Optimizations possible
- Executed when action called

**Example**:
```python
# These are transformations (not executed yet)
rdd1 = sc.textFile("input.txt")  # Lazy
rdd2 = rdd1.map(lambda x: x.upper())  # Lazy
rdd3 = rdd2.filter(lambda x: "ERROR" in x)  # Lazy

# This is an action (triggers execution of all above)
count = rdd3.count()  # Executed now!
```

**Lineage (RDD Graph)**:
- Logical execution plan
- Records how RDD was derived
- Enables fault recovery
- Can recompute lost partitions

**Example Lineage**:
```
File RDD -> map() -> Filtered RDD -> reduceByKey() -> Result RDD
```

**DAG (Directed Acyclic Graph)**:
- Represents computation workflow
- Nodes = RDDs
- Edges = transformations
- Optimized by DAG Scheduler

**Stages**:
- DAG divided into stages at shuffle boundaries
- Narrow transformations pipelined in single stage
- Wide transformations create stage boundary

**Example**:
```
Stage 1: textFile -> map -> filter
Stage 2: reduceByKey -> collect
(Shuffle boundary between stages)
```

**Partitioning**:
- RDD divided into partitions
- Each partition processed independently
- Number of partitions affects parallelism
- More partitions = more parallelism (up to limit)

**Creating RDDs**:

**1. Parallelize Collection**:
```python
data = [1, 2, 3, 4, 5]
rdd = sc.parallelize(data)
rdd = sc.parallelize(data, numPartitions=4)
```

**2. External Data Source**:
```python
# Text file
rdd = sc.textFile("hdfs://path/to/file.txt")
rdd = sc.textFile("file.txt", minPartitions=4)

# Multiple files
rdd = sc.textFile("hdfs://path/to/directory")

# Pattern matching
rdd = sc.textFile("hdfs://path/*.txt")
```

**3. Transformation of Existing RDD**:
```python
rdd2 = rdd1.map(lambda x: x * 2)
```

**Persistence (Caching)**:

**Purpose**:
- Reuse RDD in multiple actions
- Avoid recomputation
- Dramatically improves performance for iterative algorithms

**Storage Levels**:
- **MEMORY_ONLY**: Store in memory only (default)
- **MEMORY_AND_DISK**: Spill to disk if memory full
- **MEMORY_ONLY_SER**: Serialize objects in memory
- **DISK_ONLY**: Store only on disk
- **MEMORY_AND_DISK_SER**: Serialize and use disk for overflow
- **OFF_HEAP**: Store in off-heap memory (Tachyon)

**Usage**:
```python
# Cache in memory
rdd.cache()  # Same as persist(MEMORY_ONLY)

# Explicitly choose storage
rdd.persist(StorageLevel.MEMORY_AND_DISK)

# Remove from cache
rdd.unpersist()
```

**When to Cache**:
- RDD used in multiple actions
- Expensive to recompute
- Iterative algorithms (machine learning)
- Interactive exploration

**When NOT to Cache**:
- RDD used only once
- Cheap to recompute
- Very large RDD (doesn't fit in memory)

**Broadcast Variables**:
- Read-only variable cached on each worker
- Efficient distribution of large read-only data
- Avoid sending with each task

```python
# Broadcast large lookup table
broadcast_var = sc.broadcast([1, 2, 3])

# Use in transformation
rdd.map(lambda x: x * broadcast_var.value)
```

**Accumulators**:
- Variables that can only be added to
- Used for counters and sums
- Only driver can read value

```python
# Create accumulator
accum = sc.accumulator(0)

# Use in transformation
rdd.foreach(lambda x: accum.add(1))

# Read value (only in driver)
print(accum.value)
```

**Spark Application Lifecycle**:

1. **Create SparkContext**
2. **Define transformations** (build DAG)
3. **Call action** (triggers execution)
4. **DAG Scheduler** creates stages
5. **Task Scheduler** launches tasks
6. **Executors** run tasks
7. **Results** returned to driver
8. **Stop SparkContext**

**Example Application**:
```python
from pyspark import SparkContext

# Create context
sc = SparkContext("local[4]", "WordCount")

# Load data
lines = sc.textFile("input.txt")

# Transformations (lazy)
words = lines.flatMap(lambda line: line.split())
pairs = words.map(lambda word: (word, 1))
counts = pairs.reduceByKey(lambda a, b: a + b)

# Action (triggers execution)
results = counts.collect()

# Stop context
sc.stop()
```

**Performance Optimization**:

**1. Avoid Shuffles**:
- Expensive operation (network transfer)
- Use narrow transformations when possible
- Example: map() instead of groupByKey()

**2. Use Appropriate Operations**:
```python
# Bad: groupByKey then sum (shuffles all data)
pairs.groupByKey().mapValues(lambda x: sum(x))

# Good: reduceByKey (partial aggregation first)
pairs.reduceByKey(lambda a, b: a + b)
```

**3. Partition Wisely**:
- More partitions = more parallelism
- But too many = overhead
- Rule of thumb: 2-4 partitions per CPU core

**4. Cache Strategically**:
- Cache intermediate RDDs used multiple times
- Choose appropriate storage level

**5. Broadcast Large Variables**:
- Instead of sending with each task

**Key Advantages Over MapReduce**:
1. **In-memory computing**: 100x faster for iterative workloads
2. **Ease of use**: Concise API, multiple languages
3. **Unified platform**: Batch, SQL, streaming, ML, graph in one framework
4. **Interactive**: REPL for Scala and Python
5. **Flexible**: DAG vs rigid two-stage MapReduce
6. **Rich ecosystem**: Many libraries and integrations

**Key Takeaways**:
1. Spark = Fast in-memory analytics engine
2. RDD = Fault-tolerant distributed collection
3. Transformations = Lazy (build DAG)
4. Actions = Eager (trigger execution)
5. Lineage = Fault recovery mechanism
6. DAG = Optimized execution plan
7. Cache = Reuse RDD across operations
8. Much faster than MapReduce for iterative/interactive workloads
9. Unified platform for multiple workload types
10. Scala, Python, Java, R support

---

## Topic 18: Spark Data Model

**Summary**: Spark's data model centers on RDDs (Resilient Distributed Datasets) as immutable distributed collections supporting two operation types: transformations (lazy operations creating new RDDs like map, filter, flatMap) and actions (eager operations returning values like collect, count, reduce) that trigger actual computation through DAG execution. RDD operations are classified as narrow transformations (no shuffle required, each input partition maps to single output partition, pipelined efficiently) and wide transformations (shuffle required, input partitions contribute to multiple output partitions, create stage boundaries). Spark also provides higher-level abstractions including DataFrames (distributed collection of rows with named columns, similar to relational tables) and Datasets (type-safe DataFrames) that leverage the Catalyst query optimizer for better performance, while key-value pair RDDs enable specialized operations like reduceByKey, groupByKey, and join for paired data processing.

**RDD Operations - Complete Reference**:

**Transformations (Lazy)**:

**Narrow Transformations** (No Shuffle):

**1. map(func)**:
- Apply function to each element
- Input: 1 partition → Output: 1 partition
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
rdd2 = rdd.map(lambda x: x * 2)
# Result: [2, 4, 6, 8]
```

**2. filter(func)**:
- Keep elements where function returns True
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4, 5, 6])
rdd2 = rdd.filter(lambda x: x % 2 == 0)
# Result: [2, 4, 6]
```

**3. flatMap(func)**:
- Map then flatten (one-to-many mapping)
- Example:
```python
rdd = sc.parallelize(["hello world", "goodbye world"])
rdd2 = rdd.flatMap(lambda x: x.split())
# Result: ["hello", "world", "goodbye", "world"]
```

**4. mapPartitions(func)**:
- Apply function to each partition
- More efficient than map for some operations
- Example:
```python
def process_partition(iterator):
    yield sum(iterator)

rdd = sc.parallelize([1, 2, 3, 4, 5, 6], 3)
rdd2 = rdd.mapPartitions(process_partition)
# Result: [3, 7, 11] (sum of each partition)
```

**5. mapPartitionsWithIndex(func)**:
- Like mapPartitions but includes partition index
- Example:
```python
def func(partitionIndex, iterator):
    yield (partitionIndex, sum(iterator))

rdd = sc.parallelize([1, 2, 3, 4], 2)
rdd2 = rdd.mapPartitionsWithIndex(func)
# Result: [(0, 3), (1, 7)]
```

**6. sample(withReplacement, fraction, seed)**:
- Random sample of data
- Example:
```python
rdd = sc.parallelize(range(100))
sampled = rdd.sample(False, 0.1, seed=42)
# Result: ~10% of elements
```

**7. union(otherRDD)**:
- Combine two RDDs
- No deduplication
- Example:
```python
rdd1 = sc.parallelize([1, 2, 3])
rdd2 = sc.parallelize([3, 4, 5])
rdd3 = rdd1.union(rdd2)
# Result: [1, 2, 3, 3, 4, 5]
```

**Wide Transformations** (Shuffle Required):

**8. distinct()**:
- Remove duplicates
- Requires shuffle
- Example:
```python
rdd = sc.parallelize([1, 2, 2, 3, 3, 3])
rdd2 = rdd.distinct()
# Result: [1, 2, 3]
```

**9. groupByKey()** [for Pair RDDs]:
- Group values by key
- **Warning**: Expensive, prefer reduceByKey
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])
rdd2 = rdd.groupByKey()
# Result: [("a", [1, 3]), ("b", [2])]
```

**10. reduceByKey(func)** [for Pair RDDs]:
- Aggregate values by key
- More efficient than groupByKey
- Combiner function applied locally first
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 1), ("a", 1)])
rdd2 = rdd.reduceByKey(lambda a, b: a + b)
# Result: [("a", 2), ("b", 1)]
```

**11. aggregateByKey(zeroValue, seqFunc, combFunc)** [for Pair RDDs]:
- Flexible aggregation by key
- Different types for input and output
- Example:
```python
rdd = sc.parallelize([("a", 1), ("a", 2), ("b", 3)])
rdd2 = rdd.aggregateByKey(
    0,  # zero value
    lambda acc, value: acc + value,  # within partition
    lambda acc1, acc2: acc1 + acc2   # combine partitions
)
# Result: [("a", 3), ("b", 3)]
```

**12. sortByKey(ascending=True)** [for Pair RDDs]:
- Sort by key
- Requires shuffle
- Example:
```python
rdd = sc.parallelize([("c", 1), ("a", 2), ("b", 3)])
rdd2 = rdd.sortByKey()
# Result: [("a", 2), ("b", 3), ("c", 1)]
```

**13. join(otherRDD)** [for Pair RDDs]:
- Inner join on keys
- Example:
```python
rdd1 = sc.parallelize([("a", 1), ("b", 2)])
rdd2 = sc.parallelize([("a", 3), ("c", 4)])
rdd3 = rdd1.join(rdd2)
# Result: [("a", (1, 3))]
```

**14. leftOuterJoin(otherRDD)** [for Pair RDDs]:
```python
rdd3 = rdd1.leftOuterJoin(rdd2)
# Result: [("a", (1, Some(3))), ("b", (2, None))]
```

**15. rightOuterJoin(otherRDD)** [for Pair RDDs]:
```python
rdd3 = rdd1.rightOuterJoin(rdd2)
# Result: [("a", (Some(1), 3)), ("c", (None, 4))]
```

**16. cogroup(otherRDD)** [for Pair RDDs]:
- Group both RDDs by key
- Example:
```python
rdd1 = sc.parallelize([("a", 1), ("a", 2)])
rdd2 = sc.parallelize([("a", 3), ("b", 4)])
rdd3 = rdd1.cogroup(rdd2)
# Result: [("a", ([1, 2], [3])), ("b", ([], [4]))]
```

**17. cartesian(otherRDD)**:
- Cartesian product (all combinations)
- Very expensive!
- Example:
```python
rdd1 = sc.parallelize([1, 2])
rdd2 = sc.parallelize(['a', 'b'])
rdd3 = rdd1.cartesian(rdd2)
# Result: [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
```

**18. repartition(numPartitions)**:
- Change number of partitions
- Causes shuffle
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4], 2)
rdd2 = rdd.repartition(4)
# Now has 4 partitions
```

**19. coalesce(numPartitions, shuffle=False)**:
- Reduce number of partitions
- More efficient than repartition (no shuffle by default)
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4], 4)
rdd2 = rdd.coalesce(2)
# Now has 2 partitions, no shuffle
```

**Actions (Eager - Trigger Computation)**:

**1. collect()**:
- Return all elements to driver
- **Warning**: Can cause OOM if dataset large
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
result = rdd.collect()
# Returns: [1, 2, 3, 4]
```

**2. count()**:
- Return number of elements
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
count = rdd.count()
# Returns: 4
```

**3. first()**:
- Return first element
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
first = rdd.first()
# Returns: 1
```

**4. take(n)**:
- Return first n elements
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4, 5])
taken = rdd.take(3)
# Returns: [1, 2, 3]
```

**5. takeSample(withReplacement, num, seed)**:
- Return random sample
- Example:
```python
rdd = sc.parallelize(range(100))
sample = rdd.takeSample(False, 5, seed=42)
# Returns: 5 random elements
```

**6. takeOrdered(n, key=func)**:
- Return top n elements (sorted)
- Example:
```python
rdd = sc.parallelize([5, 3, 1, 4, 2])
ordered = rdd.takeOrdered(3)
# Returns: [1, 2, 3]

# With custom key
ordered = rdd.takeOrdered(3, key=lambda x: -x)
# Returns: [5, 4, 3]
```

**7. reduce(func)**:
- Aggregate elements using function
- Must be associative and commutative
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
sum_result = rdd.reduce(lambda a, b: a + b)
# Returns: 10
```

**8. fold(zeroValue, func)**:
- Like reduce but with initial value
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
result = rdd.fold(0, lambda a, b: a + b)
# Returns: 10
```

**9. aggregate(zeroValue, seqFunc, combFunc)**:
- Flexible aggregation
- Different types for input and output
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
result = rdd.aggregate(
    (0, 0),  # (sum, count)
    lambda acc, value: (acc[0] + value, acc[1] + 1),
    lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])
)
# Returns: (10, 4)
average = result[0] / result[1]  # 2.5
```

**10. foreach(func)**:
- Apply function to each element
- Used for side effects (e.g., printing, writing)
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
rdd.foreach(lambda x: print(x))
# Prints each element (on executors)
```

**11. countByKey()** [for Pair RDDs]:
- Count occurrences of each key
- Returns dict to driver
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])
counts = rdd.countByKey()
# Returns: {"a": 2, "b": 1}
```

**12. countByValue()**:
- Count occurrences of each value
- Example:
```python
rdd = sc.parallelize([1, 2, 2, 3, 3, 3])
counts = rdd.countByValue()
# Returns: {1: 1, 2: 2, 3: 3}
```

**13. saveAsTextFile(path)**:
- Write RDD to text files
- One file per partition
- Example:
```python
rdd = sc.parallelize([1, 2, 3, 4])
rdd.saveAsTextFile("hdfs://output/data")
```

**14. saveAsSequenceFile(path)** [for Pair RDDs]:
- Write as Hadoop SequenceFile
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 2)])
rdd.saveAsSequenceFile("hdfs://output/seq")
```

**15. keys()** [for Pair RDDs]:
- Return RDD of just keys
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 2)])
keys = rdd.keys()
# Returns RDD: ["a", "b"]
```

**16. values()** [for Pair RDDs]:
- Return RDD of just values
- Example:
```python
rdd = sc.parallelize([("a", 1), ("b", 2)])
vals = rdd.values()
# Returns RDD: [1, 2]
```

**Narrow vs Wide Transformations**:

**Narrow** (Fast, Pipelined):
- Each input partition → one output partition
- No shuffle
- Examples: map, filter, flatMap, union, mapPartitions
- Can be pipelined in single stage

**Wide** (Slow, Shuffle):
- Input partitions → multiple output partitions
- Requires shuffle (network transfer)
- Examples: groupByKey, reduceByKey, join, distinct, repartition
- Creates stage boundary in DAG

**Pair RDD Operations**:

**Creating Pair RDDs**:
```python
# From tuples
pairs = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])

# From regular RDD
words = sc.parallelize(["hello", "world", "hello"])
pairs = words.map(lambda w: (w, 1))
```

**Common Pair Transformations**:
```python
# reduceByKey - sum values per key
rdd.reduceByKey(lambda a, b: a + b)

# mapValues - transform only values
rdd.mapValues(lambda v: v * 2)

# flatMapValues - one-to-many on values
rdd.flatMapValues(lambda v: range(v))

# keys() and values()
rdd.keys()
rdd.values()

# sortByKey()
rdd.sortByKey(ascending=True)

# groupByKey() - use carefully!
rdd.groupByKey()
```

**DataFrames and Datasets** (Higher-Level Abstractions):

**DataFrames**:
- Distributed collection of rows with named columns
- Like relational table
- Catalyst query optimizer
- Much faster than RDDs for structured data

**Creating DataFrames**:
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("app").getOrCreate()

# From list of tuples
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])

# From RDD
rdd = sc.parallelize(data)
df = spark.createDataFrame(rdd, ["name", "age"])

# From file
df = spark.read.json("file.json")
df = spark.read.csv("file.csv", header=True, inferSchema=True)
df = spark.read.parquet("file.parquet")
```

**DataFrame Operations**:
```python
# Select columns
df.select("name", "age")

# Filter
df.filter(df.age > 25)
df.where(df.age > 25)

# Group by and aggregate
df.groupBy("age").count()
df.groupBy("department").agg({"salary": "avg"})

# Sort
df.orderBy("age", ascending=False)

# Join
df1.join(df2, "id")
df1.join(df2, df1.id == df2.id, "inner")

# SQL queries
df.createOrReplaceTempView("people")
spark.sql("SELECT * FROM people WHERE age > 25")
```

**Datasets** (Scala/Java only):
- Type-safe DataFrames
- Compile-time type checking
- Object-oriented programming
- Not available in PySpark

**RDD vs DataFrame**:

| Aspect | RDD | DataFrame |
|--------|-----|-----------|
| **Type Safety** | Yes | No (PySpark), Yes (Scala Datasets) |
| **Optimization** | No automatic optimization | Catalyst optimizer |
| **Performance** | Slower for structured data | Faster |
| **API** | Functional (map, reduce) | Declarative (select, filter) |
| **Schema** | No schema | Has schema |
| **Use Case** | Unstructured data, fine control | Structured data, SQL-like queries |

**When to Use Each**:

**Use RDDs**:
- Unstructured data (text, logs)
- Need fine-grained control
- Complex transformations
- Low-level operations

**Use DataFrames**:
- Structured/semi-structured data
- SQL-like operations
- Better performance needed
- Integration with SQL tools

**Key Takeaways**:
1. **Transformations**: Lazy, return new RDD
2. **Actions**: Eager, return value or write data
3. **Narrow transformations**: No shuffle, fast, pipelined
4. **Wide transformations**: Shuffle required, slower, stage boundary
5. **Pair RDDs**: Special operations for key-value pairs
6. **reduceByKey > groupByKey**: More efficient aggregation
7. **DataFrames**: Higher-level, optimized for structured data
8. **Lazy evaluation**: Build DAG, optimize, then execute on action
9. **Lineage**: Track dependencies for fault tolerance
10. **Cache frequently used RDDs**: Especially in iterative algorithms

---

## Topic 19: Spark Operations

**Summary**: Spark operations are categorized into transformations (create new RDDs) and actions (trigger execution), with understanding of narrow vs wide transformations critical for performance optimization as narrow transformations (map, filter) don't require shuffle and can be pipelined efficiently while wide transformations (reduceByKey, groupByKey, join) require expensive shuffle operations creating stage boundaries in the DAG. Key optimization principles include preferring reduceByKey over groupByKey for aggregations (local pre-aggregation reduces shuffle data), avoiding unnecessary shuffles through appropriate transformations, using broadcast variables for large read-only lookup tables shared across tasks, and leveraging shared variables (accumulators for write-only counters, broadcast for read-only data). Performance tuning involves appropriate partitioning (2-4 partitions per CPU core), strategic caching of reused RDDs, and understanding the execution model where Spark builds a DAG of operations, divides it into stages at shuffle boundaries, and executes tasks in parallel across executors.

**Detailed Operation Analysis**:

**Transformation Deep Dive**:

**map() vs flatMap()**:

**map()** - One-to-One:
```python
# Input: [1, 2, 3]
rdd.map(lambda x: x * 2)
# Output: [2, 4, 6]

# Input: ["hello world"]
rdd.map(lambda x: x.split())
# Output: [["hello", "world"]] - nested list
```

**flatMap()** - One-to-Many, then Flatten:
```python
# Input: ["hello world", "goodbye world"]
rdd.flatMap(lambda x: x.split())
# Output: ["hello", "world", "goodbye", "world"] - flat list

# Input: [1, 2, 3]
rdd.flatMap(lambda x: range(x))
# Output: [0, 0, 1, 0, 1, 2]
```

**filter() Optimization**:
```python
# Early filtering reduces data processed
rdd = sc.textFile("large_file.txt")
filtered = rdd.filter(lambda line: "ERROR" in line)  # Filter early
result = filtered.map(some_expensive_function)  # Process less data
```

**groupByKey() vs reduceByKey()**:

**groupByKey()** - AVOID when possible:
```python
# BAD: Shuffles ALL values
pairs = sc.parallelize([("a", 1), ("a", 2), ("b", 3), ("b", 4)])
grouped = pairs.groupByKey()  # Shuffles: ("a", [1,2]), ("b", [3,4])
result = grouped.mapValues(sum)  # Then sums on reducer side

# Problems:
# - Transfers all values over network
# - No local aggregation
# - High memory usage on reducers
# - Slower performance
```

**reduceByKey()** - PREFERRED:
```python
# GOOD: Local aggregation before shuffle
pairs = sc.parallelize([("a", 1), ("a", 2), ("b", 3), ("b", 4)])
result = pairs.reduceByKey(lambda a, b: a + b)

# Benefits:
# - Combines locally first (like combiner in MapReduce)
# - Transfers less data over network
# - Lower memory usage
# - Much faster
```

**Visual Comparison**:
```
groupByKey():
Mapper 1: (a,1), (a,2) → Shuffle → Reducer: (a,[1,2]) → sum → (a,3)
Mapper 2: (b,3), (b,4) → Shuffle → Reducer: (b,[3,4]) → sum → (b,7)
(Transfers 4 values: 1,2,3,4)

reduceByKey():
Mapper 1: (a,1), (a,2) → Local: (a,3) → Shuffle → Reducer: (a,3)
Mapper 2: (b,3), (b,4) → Local: (b,7) → Shuffle → Reducer: (b,7)
(Transfers 2 values: 3,7)
```

**Join Operations**:

**Inner Join**:
```python
rdd1 = sc.parallelize([("a", 1), ("b", 2), ("c", 3)])
rdd2 = sc.parallelize([("a", "x"), ("b", "y"), ("d", "z")])

result = rdd1.join(rdd2)
# Result: [("a", (1, "x")), ("b", (2, "y"))]
# Only keys in both RDDs
```

**Left Outer Join**:
```python
result = rdd1.leftOuterJoin(rdd2)
# Result: [("a", (1, Some("x"))), 
#          ("b", (2, Some("y"))),
#          ("c", (3, None))]
# All keys from left, None for missing right
```

**Right Outer Join**:
```python
result = rdd1.rightOuterJoin(rdd2)
# Result: [("a", (Some(1), "x")),
#          ("b", (Some(2), "y")),
#          ("d", (None, "z"))]
# All keys from right, None for missing left
```

**Broadcast Join Optimization**:
```python
# When one RDD is small (< few MB)
small_rdd = sc.parallelize([("a", "A"), ("b", "B")])
large_rdd = sc.parallelize([(i, i%2) for i in range(1000000)])

# Create broadcast variable
broadcast_dict = sc.broadcast(small_rdd.collectAsMap())

# Map-side join (no shuffle!)
def map_join(pair):
    key, value = pair
    if key in broadcast_dict.value:
        return (key, (value, broadcast_dict.value[key]))
    return None

result = large_rdd.map(map_join).filter(lambda x: x is not None)
```

**Aggregation Operations**:

**reduceByKey()** - Commutative and Associative:
```python
# Sum
rdd.reduceByKey(lambda a, b: a + b)

# Max
rdd.reduceByKey(lambda a, b: max(a, b))

# Min
rdd.reduceByKey(lambda a, b: min(a, b))

# Concatenate (must be associative!)
rdd.reduceByKey(lambda a, b: a + b)  # For strings/lists
```

**aggregateByKey()** - Different Input/Output Types:
```python
# Calculate average per key
pairs = sc.parallelize([("a", 10), ("a", 20), ("b", 5), ("b", 15)])

result = pairs.aggregateByKey(
    (0, 0),  # Initial: (sum, count)
    lambda acc, value: (acc[0] + value, acc[1] + 1),  # Add to partition
    lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])  # Merge partitions
)

averages = result.mapValues(lambda v: v[0] / v[1])
# Result: [("a", 15.0), ("b", 10.0)]
```

**foldByKey()** - Like reduceByKey with zero value:
```python
pairs = sc.parallelize([("a", 1), ("a", 2), ("b", 3)])
result = pairs.foldByKey(0, lambda a, b: a + b)
# Result: [("a", 3), ("b", 3)]
```

**combineByKey()** - Most general aggregation:
```python
# Calculate average using combineByKey
pairs = sc.parallelize([("a", 10), ("a", 20), ("b", 5)])

result = pairs.combineByKey(
    lambda value: (value, 1),  # Create combiner
    lambda acc, value: (acc[0] + value, acc[1] + 1),  # Add to combiner
    lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])  # Merge combiners
)

averages = result.mapValues(lambda v: v[0] / v[1])
```

**Partitioning Operations**:

**repartition()** - Increase or Decrease:
```python
rdd = sc.parallelize(range(100), 2)  # 2 partitions
rdd2 = rdd.repartition(10)  # Now 10 partitions
# Causes full shuffle
# Use when: Need more partitions or different distribution
```

**coalesce()** - Decrease Only (More Efficient):
```python
rdd = sc.parallelize(range(100), 10)  # 10 partitions
rdd2 = rdd.coalesce(2)  # Now 2 partitions
# No shuffle by default (just combines partitions)
# Use after filter that significantly reduces data
```

**partitionBy()** - Custom Partitioner for Pair RDDs:
```python
pairs = sc.parallelize([("a", 1), ("b", 2), ("c", 3)])
partitioned = pairs.partitionBy(2)  # 2 partitions
# Uses hash partitioner by default

# Custom partitioner
def custom_partitioner(key):
    return 0 if key < "m" else 1

partitioned = pairs.partitionBy(2, custom_partitioner)
```

**Set Operations**:

**union()** - Combine RDDs:
```python
rdd1 = sc.parallelize([1, 2, 3])
rdd2 = sc.parallelize([3, 4, 5])
result = rdd1.union(rdd2)
# Result: [1, 2, 3, 3, 4, 5] - keeps duplicates
```

**intersection()** - Common elements:
```python
result = rdd1.intersection(rdd2)
# Result: [3]
# Requires shuffle
```

**subtract()** - Elements in first but not second:
```python
result = rdd1.subtract(rdd2)
# Result: [1, 2]
# Requires shuffle
```

**cartesian()** - All combinations:
```python
rdd1 = sc.parallelize([1, 2])
rdd2 = sc.parallelize(['a', 'b'])
result = rdd1.cartesian(rdd2)
# Result: [(1,'a'), (1,'b'), (2,'a'), (2,'b')]
# VERY EXPENSIVE - avoid on large datasets
```

**Action Operations Deep Dive**:

**Collect Actions** - Be Careful:
```python
# collect() - Returns ALL data to driver
result = rdd.collect()  # Can cause OOM!

# take(n) - Returns first n elements
result = rdd.take(10)  # Safe

# first() - Returns first element
result = rdd.first()  # Safe

# top(n) - Returns top n elements
result = rdd.top(5)  # Returns [5, 4, 3, 2, 1] for [1,2,3,4,5]
```

**Reduction Actions**:
```python
# reduce() - Aggregate all elements
rdd = sc.parallelize([1, 2, 3, 4])
sum = rdd.reduce(lambda a, b: a + b)  # 10

# fold() - reduce with initial value
sum = rdd.fold(0, lambda a, b: a + b)  # 10

# aggregate() - Different types
result = rdd.aggregate(
    (0, 0),  # (sum, count)
    lambda acc, val: (acc[0] + val, acc[1] + 1),
    lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])
)
average = result[0] / result[1]
```

**Counting Actions**:
```python
# count() - Number of elements
count = rdd.count()

# countByValue() - Count of each value
counts = rdd.countByValue()  # Returns dict

# countByKey() - Count of each key (Pair RDD)
counts = rdd.countByKey()  # Returns dict
```

**Shared Variables**:

**Broadcast Variables** (Read-Only):

**Purpose**:
- Efficiently distribute large read-only data
- Avoid sending with each task
- Cached on each executor

**Usage**:
```python
# Create broadcast variable
large_lookup = {"a": 1, "b": 2, "c": 3, ...}  # Large dict
broadcast_var = sc.broadcast(large_lookup)

# Use in transformation
def lookup_value(key):
    return broadcast_var.value.get(key, 0)

rdd = sc.parallelize(["a", "b", "c", "d"])
result = rdd.map(lookup_value)

# Destroy when done
broadcast_var.unpersist()
broadcast_var.destroy()
```

**When to Use**:
- Lookup tables/dictionaries
- ML model parameters
- Configuration data
- Any large read-only data used across tasks

**Benefits**:
- Sent once per executor (not per task)
- Efficient broadcast algorithm
- Stored in serialized form

**Accumulators** (Write-Only):

**Purpose**:
- Implement counters and sums
- Write-only from tasks
- Read from driver

**Usage**:
```python
# Create accumulator
error_count = sc.accumulator(0)
valid_count = sc.accumulator(0)

# Use in transformations/actions
def process_line(line):
    if "ERROR" in line:
        error_count.add(1)
    else:
        valid_count.add(1)
    return line

rdd = sc.textFile("log.txt")
rdd.foreach(process_line)

# Read in driver
print(f"Errors: {error_count.value}")
print(f"Valid: {valid_count.value}")
```

**Important Notes**:
- Only actions guarantee accumulator updates
- Transformations may update multiple times (re-execution)
- Use only in actions or be aware of lazy evaluation

**Custom Accumulators**:
```python
from pyspark.accumulators import AccumulatorParam

class SetAccumulatorParam(AccumulatorParam):
    def zero(self, initialValue):
        return set()
    
    def addInPlace(self, v1, v2):
        v1.update(v2)
        return v1

# Use custom accumulator
unique_words = sc.accumulator(set(), SetAccumulatorParam())
```

**Performance Optimization Patterns**:

**1. Avoid groupByKey Pattern**:
```python
# BAD
pairs.groupByKey().mapValues(sum)
pairs.groupByKey().mapValues(len)

# GOOD
pairs.reduceByKey(lambda a,b: a+b)
pairs.mapValues(lambda v: 1).reduceByKey(lambda a,b: a+b)
```

**2. Use combineByKey for Complex Aggregations**:
```python
# Calculate multiple statistics at once
def create_combiner(value):
    return (value, value, value, 1)  # (sum, min, max, count)

def merge_value(acc, value):
    return (acc[0]+value, min(acc[1],value), 
            max(acc[2],value), acc[3]+1)

def merge_combiners(acc1, acc2):
    return (acc1[0]+acc2[0], min(acc1[1],acc2[1]), 
            max(acc1[2],acc2[2]), acc1[3]+acc2[3])

stats = pairs.combineByKey(create_combiner, merge_value, merge_combiners)
```

**3. Broadcast Small Tables in Joins**:
```python
# Instead of shuffle join
large_rdd.join(small_rdd)  # Shuffles both

# Use broadcast
broadcast_small = sc.broadcast(small_rdd.collectAsMap())
large_rdd.map(lambda pair: (pair[0], (pair[1], broadcast_small.value.get(pair[0]))))
```

**4. Filter Early**:
```python
# BAD - processes unnecessary data
rdd.map(expensive_func).filter(predicate)

# GOOD - filters first
rdd.filter(predicate).map(expensive_func)
```

**5. Cache Appropriately**:
```python
# Cache RDDs used multiple times
filtered_rdd = rdd.filter(lambda x: x > 10)
filtered_rdd.cache()  # Will be reused

result1 = filtered_rdd.count()
result2 = filtered_rdd.reduce(lambda a,b: a+b)  # Uses cached data
```

**6. Avoid Unnecessary Shuffles**:
```python
# BAD - multiple shuffles
rdd.groupByKey().mapValues(list).flatMap(lambda x: x[1])

# GOOD - no shuffle needed
rdd.values()
```

**7. Choose Right Partition Count**:
```python
# Rule of thumb: 2-4 partitions per CPU core
num_cores = 8
ideal_partitions = num_cores * 3  # 24 partitions

rdd = sc.textFile("file.txt", minPartitions=ideal_partitions)
```

**Common Patterns**:

**WordCount**:
```python
text = sc.textFile("file.txt")
counts = text.flatMap(lambda line: line.split()) \
             .map(lambda word: (word, 1)) \
             .reduceByKey(lambda a, b: a + b)
```

**Top N**:
```python
top10 = rdd.takeOrdered(10, key=lambda x: -x[1])  # By value descending
```

**Distinct Values**:
```python
distinct_values = rdd.distinct()
```

**Sample**:
```python
sample = rdd.sample(False, 0.1, seed=42)  # 10% sample
```

**Key Takeaways**:
1. **reduceByKey > groupByKey**: Always prefer for aggregations
2. **Broadcast small tables**: Avoid shuffle in joins
3. **Filter early**: Reduce data processed
4. **Cache wisely**: Reused RDDs only
5. **Partition appropriately**: 2-4 per core
6. **Avoid unnecessary shuffles**: Use narrow transformations
7. **Accumulators for counters**: Broadcast for lookups
8. **Understand narrow vs wide**: Impacts performance significantly
9. **Use appropriate actions**: Avoid collect() on large datasets
10. **Lazy evaluation**: Build efficient DAG before execution

---

## Topic 20: Spark Streaming

**Summary**: Spark Streaming enables scalable, high-throughput, fault-tolerant stream processing by discretizing continuous data streams into micro-batches processed as a series of RDDs (DStreams - Discretized Streams), treating streams as continuous sequences of RDDs where each batch represents data received during a time interval. This micro-batch architecture leverages Spark's batch processing capabilities while providing near-real-time processing with latencies typically in seconds, supporting various input sources (Kafka, Flume, TCP sockets, HDFS) and output operations (save to databases, filesystems, dashboards). DStreams provide the same functional API as RDDs (map, filter, reduce) plus stateful operations (updateStateByKey for maintaining state across batches) and windowing operations (window, countByWindow, reduceByWindow) for time-based analysis over sliding intervals, enabling complex stream processing patterns like sessionization, trending topics, and real-time dashboards while maintaining exactly-once semantics and fault tolerance through checkpointing.

**Spark Streaming Fundamentals**:

**Core Concept - Micro-Batch Architecture**:
```
Continuous Stream:
[data][data][data][data][data][data][data][data]...

Discretized into Batches (e.g., 1-second intervals):
[Batch 1] [Batch 2] [Batch 3] [Batch 4]...
   ↓         ↓         ↓         ↓
  RDD      RDD       RDD       RDD
```

**DStream (Discretized Stream)**:
- Continuous sequence of RDDs
- Each RDD contains data from one time interval
- Operations on DStream applied to each underlying RDD
- Maintains lineage for fault tolerance

**Basic Structure**:
```python
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# Create contexts
sc = SparkContext("local[2]", "NetworkWordCount")
ssc = StreamingContext(sc, 1)  # 1-second batch interval

# Create DStream
lines = ssc.socketTextStream("localhost", 9999)

# Transformations (like RDD operations)
words = lines.flatMap(lambda line: line.split())
pairs = words.map(lambda word: (word, 1))
wordCounts = pairs.reduceByKey(lambda a, b: a + b)

# Output operation
wordCounts.pprint()

# Start streaming
ssc.start()
ssc.awaitTermination()  # Wait for termination signal
```

**StreamingContext**:
- Entry point for Spark Streaming
- Requires SparkContext
- Defines batch interval (e.g., 1 second, 5 seconds)
- Can only be started once

**Key Parameters**:
- **Batch Interval**: Time to collect data into RDD (e.g., 1 second)
- **Window Length**: Duration of window operations (e.g., 30 seconds)
- **Sliding Interval**: How often window operations execute (e.g., 10 seconds)

**Input Sources**:

**1. Socket Streams**:
```python
# TCP socket source
stream = ssc.socketTextStream("localhost", 9999)
```

**2. File Streams**:
```python
# Monitor directory for new files
stream = ssc.textFileStream("hdfs://path/to/directory")
```

**3. Kafka**:
```python
from pyspark.streaming.kafka import KafkaUtils

# Kafka source
stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {"topic": 1})
```

**4. Flume**:
```python
from pyspark.streaming.flume import FlumeUtils

stream = FlumeUtils.createStream(ssc, "localhost", 9999)
```

**5. Custom Sources**:
```python
# Queue of RDDs for testing
rddQueue = []
for i in range(5):
    rddQueue.append(sc.parallelize([i] * 10))

stream = ssc.queueStream(rddQueue)
```

**DStream Transformations**:

**Standard RDD-like Operations**:

**map()**:
```python
lines = ssc.socketTextStream("localhost", 9999)
lengths = lines.map(lambda line: len(line))
```

**flatMap()**:
```python
words = lines.flatMap(lambda line: line.split())
```

**filter()**:
```python
errors = lines.filter(lambda line: "ERROR" in line)
```

**reduceByKey()**:
```python
pairs = words.map(lambda word: (word, 1))
wordCounts = pairs.reduceByKey(lambda a, b: a + b)
```

**join()** - Join two DStreams:
```python
stream1 = ...  # DStream of (key, value1)
stream2 = ...  # DStream of (key, value2)
joined = stream1.join(stream2)  # DStream of (key, (value1, value2))
```

**union()**:
```python
stream1 = ssc.socketTextStream("localhost", 9999)
stream2 = ssc.socketTextStream("localhost", 9998)
combined = stream1.union(stream2)
```

**transform()** - Apply arbitrary RDD operations:
```python
def process_rdd(time, rdd):
    # Custom processing on underlying RDD
    return rdd.filter(lambda x: x > 10).map(lambda x: x * 2)

processed = stream.transform(process_rdd)
```

**Window Operations**:

**Concept**:
- Apply operations over sliding window of data
- Window length: how much data to include
- Sliding interval: how often to compute

**Visual**:
```
Time: →→→→→→→→→→→→→→→
Batches: [B1][B2][B3][B4][B5][B6][B7][B8]

Window Length = 3 batches
Sliding Interval = 2 batches

Window 1: [B1][B2][B3]
Window 2:       [B3][B4][B5]
Window 3:             [B5][B6][B7]
```

**window(windowLength, slideInterval)**:
```python
# Every 10 seconds, compute on last 30 seconds of data
windowedStream = stream.window(30, 10)

# Count words in each window
windowedWordCounts = pairs.reduceByKeyAndWindow(
    lambda a, b: a + b,  # Reduction function
    lambda a, b: a - b,  # Inverse reduction (optional, for efficiency)
    30,  # Window length (seconds)
    10   # Slide interval (seconds)
)
```

**countByWindow(windowLength, slideInterval)**:
```python
# Count elements in each window
counts = stream.countByWindow(30, 10)
```

**reduceByWindow()**:
```python
# Sum all elements in window
sums = stream.reduceByWindow(
    lambda a, b: a + b,
    lambda a, b: a - b,  # Inverse (optional)
    30, 10
)
```

**reduceByKeyAndWindow()**:
```python
# Aggregate by key over window
wordCounts = pairs.reduceByKeyAndWindow(
    lambda a, b: a + b,  # Add new values
    lambda a, b: a - b,  # Subtract old values (inverse)
    30, 10
)
```

**countByValueAndWindow()**:
```python
# Count occurrences of each value in window
valueCounts = stream.countByValueAndWindow(30, 10)
```

**Stateful Operations**:

**updateStateByKey()** - Maintain State Across Batches:

**Concept**:
- Maintain and update state for each key
- State persists across batches
- Requires checkpointing

**Usage**:
```python
def update_function(new_values, running_count):
    if running_count is None:
        running_count = 0
    return sum(new_values) + running_count

# Enable checkpointing (required for stateful operations)
ssc.checkpoint("hdfs://path/to/checkpoint")

# Running total of word counts
runningCounts = pairs.updateStateByKey(update_function)
```

**Example - Running Word Count**:
```python
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

sc = SparkContext("local[2]", "StatefulWordCount")
ssc = StreamingContext(sc, 1)
ssc.checkpoint("checkpoint")

lines = ssc.socketTextStream("localhost", 9999)
words = lines.flatMap(lambda line: line.split())
pairs = words.map(lambda word: (word, 1))

def updateFunc(new_values, last_sum):
    return sum(new_values) + (last_sum or 0)

runningCounts = pairs.updateStateByKey(updateFunc)
runningCounts.pprint()

ssc.start()
ssc.awaitTermination()
```

**mapWithState()** - More Efficient State Management:
```python
from pyspark.streaming import StateSpec

def mapping_function(key, value, state):
    # More efficient than updateStateByKey
    current_state = state.get() if state.exists() else 0
    new_state = current_state + value
    state.update(new_state)
    return (key, new_state)

state_spec = StateSpec(mapping_function)
statefulStream = pairs.mapWithState(state_spec)
```

**Output Operations**:

**pprint()**:
- Print first few elements of each batch
```python
stream.pprint()
stream.pprint(num=20)  # Print first 20 elements
```

**saveAsTextFiles()**:
```python
stream.saveAsTextFiles("hdfs://path/prefix", "suffix")
# Creates: prefix-TIME.suffix
```

**saveAsObjectFiles()**:
```python
stream.saveAsObjectFiles("hdfs://path/prefix")
```

**foreachRDD()**:
- Apply custom function to each RDD
- Most flexible output operation

```python
def process_rdd(time, rdd):
    # Custom processing
    if not rdd.isEmpty():
        # Write to database
        rdd.foreachPartition(write_to_db)
        
        # Or collect and process in driver
        results = rdd.collect()
        for result in results:
            print(result)

stream.foreachRDD(process_rdd)
```

**Example - Write to Database**:
```python
def write_partition_to_db(iterator):
    # Create connection per partition
    connection = get_db_connection()
    for record in iterator:
        connection.insert(record)
    connection.close()

def save_to_database(time, rdd):
    if not rdd.isEmpty():
        rdd.foreachPartition(write_partition_to_db)

wordCounts.foreachRDD(save_to_database)
```

**Checkpointing**:

**Purpose**:
- Fault tolerance for stateful operations
- Periodic saving of state
- Recovery from driver failures

**Types**:
1. **Metadata Checkpointing**: Save DStream DAG
2. **Data Checkpointing**: Save actual data (for stateful operations)

**Setup**:
```python
ssc.checkpoint("hdfs://path/to/checkpoint")
```

**Fault Tolerance**:

**Data Loss Prevention**:
- Write-ahead logs (WAL) for input sources
- Receiver reliability
- Checkpointing for state

**Receiver Reliability Levels**:
- **Reliable**: Acknowledges data only after processing
- **Unreliable**: May lose data on failure

**Kafka Example with Reliability**:
```python
from pyspark.streaming.kafka import KafkaUtils

# Direct approach (more reliable)
stream = KafkaUtils.createDirectStream(ssc, ["topic"], {"metadata.broker.list": "localhost:9092"})
```

**Performance Tuning**:

**1. Batch Interval**:
```python
# Too small: Overhead of job scheduling
# Too large: Latency increases, memory issues
# Sweet spot: 0.5-10 seconds typically

ssc = StreamingContext(sc, 2)  # 2-second batches
```

**2. Parallelism**:
```python
# Increase parallelism for data receiving
ssc = StreamingContext(sc, 1)
lines = ssc.socketTextStream("localhost", 9999)
parallelLines = lines.repartition(4)  # Process in 4 partitions

# Or specify when creating stream
lines = ssc.textFileStream("path").repartition(8)
```

**3. Memory**:
```python
# Persist strategically
stream.persist(StorageLevel.MEMORY_AND_DISK_SER)
```

**4. Checkpointing Interval**:
```python
# Set checkpoint interval (default: 10 * batch interval)
stream.checkpoint(20)  # Checkpoint every 20 seconds
```

**Real-World Use Cases**:

**1. Real-Time Dashboard**:
```python
# Count events per minute
events = ssc.socketTextStream("localhost", 9999)
counts = events.countByWindow(60, 10)  # 60s window, 10s slide

def update_dashboard(time, rdd):
    if not rdd.isEmpty():
        count = rdd.collect()[0]
        update_web_dashboard(count)

counts.foreachRDD(update_dashboard)
```

**2. Trending Topics**:
```python
# Top hashtags in last 10 minutes
tweets = ssc.socketTextStream("localhost", 9999)
hashtags = tweets.flatMap(lambda tweet: extract_hashtags(tweet))
hashtag_counts = hashtags.map(lambda tag: (tag, 1)) \
                         .reduceByKeyAndWindow(lambda a,b: a+b, 600, 60)

def print_top_10(time, rdd):
    if not rdd.isEmpty():
        top10 = rdd.takeOrdered(10, key=lambda x: -x[1])
        print(f"Top 10 at {time}: {top10}")

hashtag_counts.foreachRDD(print_top_10)
```

**3. Fraud Detection**:
```python
# Detect accounts with >100 transactions in 5 minutes
transactions = ssc.socketTextStream("localhost", 9999)
account_txns = transactions.map(lambda t: (extract_account(t), 1))
txn_counts = account_txns.reduceByKeyAndWindow(lambda a,b: a+b, 300, 60)

suspicious = txn_counts.filter(lambda x: x[1] > 100)
suspicious.foreachRDD(lambda time, rdd: alert_fraud_team(rdd))
```

**4. Session Analysis**:
```python
# Track user sessions
events = ssc.socketTextStream("localhost", 9999)
user_events = events.map(lambda e: (extract_user_id(e), e))

def update_session(new_events, old_session):
    # Update session with new events
    if old_session is None:
        old_session = []
    return old_session + list(new_events)

sessions = user_events.updateStateByKey(update_session)
```

**Spark Streaming vs Other Frameworks**:

| Aspect | Spark Streaming | Kafka Streams | Flink |
|--------|----------------|---------------|-------|
| **Processing** | Micro-batch | True streaming | True streaming |
| **Latency** | Seconds | Milliseconds | Milliseconds |
| **Throughput** | Very High | High | Very High |
| **Exactly-Once** | Yes (with checkpointing) | Yes | Yes |
| **State Management** | Good | Excellent | Excellent |
| **Ease of Use** | Easy (Spark API) | Medium | Medium |
| **Batch Integration** | Excellent | Limited | Good |

**Key Takeaways**:
1. **DStream = Sequence of RDDs**: Micro-batch architecture
2. **Batch Interval**: Determines latency and throughput
3. **Window Operations**: Sliding analysis over time
4. **Stateful Processing**: updateStateByKey for cross-batch state
5. **Checkpointing**: Required for stateful operations
6. **foreachRDD**: Most flexible output operation
7. **Fault Tolerance**: Through lineage and checkpointing
8. **Latency**: Typically seconds (not milliseconds)
9. **Integration**: Leverages entire Spark ecosystem
10. **Use Cases**: Dashboards, monitoring, ETL, trending analysis

---

## Summary

This comprehensive topic-wise summary covers all 20 major topics in ISIT312 Big Data Management, providing:

- Clear 3-5 sentence summaries for each topic
- Key concepts, models, and techniques
- Important definitions and terminology
- Relevant examples and use cases
- Exam-focused content aligned with the subject review

**Exam Preparation Notes**:
- The exam is **3 hours, closed-book, face-to-face**
- **50 marks total, 6 short answer questions**
- **No multiple choice, no Java programming questions**
- **A cheat sheet will be provided** with HDFS, HQL, HBase, and Spark examples
- **40% TF clause** on final examination

**Study Priority** (Based on Subject Review):
1. **HIGH**: MapReduce Model, HDFS Architecture, Hive/HQL, Data Warehousing, Spark
2. **MEDIUM**: HBase, Multidimensional Data Model
3. **FOUNDATIONAL**: Hadoop Architecture, Cluster Computing

All topics are interconnected and understanding the fundamentals is essential for success in this examination.

---

*Document Created: November 17, 2025*  
*Course: ISIT312 Big Data Management*  
*Session: SIM S4 2025*  
*Lecturer: Dr Fenghui Ren*