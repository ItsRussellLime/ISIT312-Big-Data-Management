# Topic 11: Apache Spark

## 1. Introduction to Spark

### What is Apache Spark?
- **Cluster computing platform** designed to be **fast** and **general-purpose**
- **Unified analytics engine** for large-scale data processing
- **In-memory computing** framework
- **Extends MapReduce** model efficiently

### Why Spark?

#### Speed
- **100x faster** than MapReduce in memory
- **10x faster** than MapReduce on disk
- Achieved by **reducing I/O operations**
- Stores intermediate data in **memory**

#### Generality
- **Unified environment** for diverse workloads:
  - Batch processing
  - Interactive queries
  - Streaming
  - Machine learning
  - Graph processing
- Makes combining different engines **easy and inexpensive**

#### Multiple Languages
- **Scala** (native)
- **Python** (PySpark)
- **Java**
- **SQL** (Spark SQL)
- **R** (SparkR)

#### Rich Libraries
- **Spark SQL**: Structured data processing
- **Spark Streaming**: Real-time data processing
- **MLlib**: Machine learning
- **GraphX**: Graph processing
- Fast-growing ecosystem

## 2. MapReduce Challenges (Why Spark?)

### Problems with MapReduce

#### 1. Low-Level API
- **Java MapReduce API** too low-level
- Difficult to express complex logic
- Verbose code for simple tasks
- Example: Multi-stage pipelines require multiple jobs

#### 2. I/O Latency
- **Persistent storage I/O** dominates execution time
- **>90% time** spent in HDFS read/write
- Every MapReduce job:
  - Reads from HDFS
  - Writes results to HDFS
- **Data replication** overhead
- **Serialization/deserialization** overhead

#### 3. Data Sharing Inefficiency
- **Reuse data** between computations requires HDFS
- Example: Iterative algorithms (machine learning)
  - Each iteration: Read from HDFS → Process → Write to HDFS
  - Substantial overhead accumulates

#### 4. Not Suitable for Interactive/Iterative Computing
- **Interactive queries**: Need low latency
- **Iterative algorithms**: Reuse intermediate results
- MapReduce optimized for **batch processing only**

### Spark's Solutions

1. **In-Memory Computing**
   - Store intermediate results in memory
   - Avoid disk I/O between stages
   - Dramatically faster for iterative workloads

2. **High-Level APIs**
   - Declarative programming model
   - RDD (Resilient Distributed Dataset) abstraction
   - DataFrame and Dataset APIs

3. **DAG Execution Engine**
   - More flexible than MapReduce
   - Optimizes entire workflow
   - Efficient data sharing

4. **Unified Platform**
   - Single engine for multiple workloads
   - No need for separate systems

## 3. Spark Architecture

### Components

#### 1. Driver Program
- **Main Spark application**
- Contains **data processing logic**
- Creates **SparkContext**
- Coordinates executors
- Schedules tasks

**Key Responsibilities**:
- Parse user program
- Create execution plan
- Schedule tasks on executors
- Monitor task execution
- Aggregate results

#### 2. SparkContext
- **Entry point** to Spark functionality
- Connects to cluster manager
- Acquires executors
- Sends application code to executors

#### 3. Cluster Manager
- **External service** for acquiring resources
- Types:
  - **Standalone**: Spark's built-in manager
  - **YARN**: Hadoop's resource manager
  - **Mesos**: Apache Mesos
  - **Kubernetes**: K8s orchestration

#### 4. Executor
- **JVM process** running on worker node
- Runs **tasks** submitted by driver
- Stores data in memory/disk for caching
- Returns results to driver

**Characteristics**:
- One or more per worker node
- Lives for entire application duration
- Isolated from other applications

#### 5. Task
- **Unit of work** sent to executor
- **Smallest unit** of execution
- Operates on **data partition**

### Deployment Modes

#### 1. Client Mode
- **Driver runs** on client machine
- Good for **interactive** use
- **Executors** on cluster
- Results returned to client

**Use Case**: 
- Interactive shells (spark-shell, pyspark)
- Jupyter notebooks
- Development and testing

#### 2. Cluster Mode
- **Driver runs** on cluster (within ApplicationMaster on YARN)
- Good for **production** jobs
- Fully distributed
- More resilient

**Use Case**:
- Production batch jobs
- Long-running applications
- No client dependency after submission

### Spark on YARN

#### Client Mode
```
Client Machine
├─ Driver Program
└─ SparkContext
        ↓
YARN Cluster
├─ ApplicationMaster (Executor Launcher)
└─ Executors on NodeManagers
```

#### Cluster Mode
```
Client Machine
└─ Submit application
        ↓
YARN Cluster
├─ ApplicationMaster (contains Driver)
└─ Executors on NodeManagers
```

## 4. Spark Core Components

### 1. Spark Core
- **Underlying execution engine**
- Foundation for all other components
- Provides:
  - In-memory computing
  - Referencing external storage systems
  - Task scheduling
  - Memory management
  - Fault recovery
  - Basic I/O operations

### 2. Spark SQL
- **Component for structured data**
- Introduces **SchemaRDD** (now DataFrame/Dataset)
- Supports:
  - SQL queries
  - Hive integration
  - Multiple data sources (JSON, Parquet, Avro, JDBC)
  - Catalyst optimizer

**Key Features**:
- Unified data access
- Hive compatibility
- Standard connectivity (JDBC/ODBC)

### 3. Spark Streaming
- **Real-time stream processing**
- Leverages Spark Core for **fast scheduling**
- **Micro-batch** processing model
- Processes data in small batches

**Key Concepts**:
- **DStream** (Discretized Stream)
- Batch intervals (e.g., 1 second)
- Integration with Kafka, Flume, Kinesis

**Use Cases**:
- Real-time analytics
- Log processing
- IoT data processing
- Fraud detection

### 4. MLlib (Machine Learning Library)
- **Distributed ML framework**
- Built on top of Spark Core
- Leverages in-memory computing

**Algorithms**:
- Classification and regression
- Clustering
- Collaborative filtering
- Dimensionality reduction
- Feature extraction

**Advantages**:
- Scalable ML
- Iterative algorithms efficient
- Integration with Spark SQL

### 5. GraphX
- **Distributed graph processing**
- API for graph computation
- **Optimized runtime** for graph algorithms

**Key Features**:
- Graph-parallel computation
- Built-in graph algorithms (PageRank, Triangle Counting)
- Property graph model

### 6. SparkR
- **R package** for Spark
- Lightweight frontend to use Spark from R
- Enables:
  - Large-scale data analysis from R
  - Distributed machine learning from R

## 5. Key Features of Spark

### 1. In-Memory Computing
**How It Works**:
- Store intermediate results in **memory**
- Avoid disk I/O between stages
- **Spill to disk** only when memory full

**Benefits**:
- **Dramatically faster** for iterative algorithms
- Enables **interactive queries**
- Better for **machine learning**

**Example**:
```
MapReduce:
Iteration 1: HDFS Read → Process → HDFS Write
Iteration 2: HDFS Read → Process → HDFS Write
Iteration 3: HDFS Read → Process → HDFS Write

Spark:
Initial: HDFS Read → Cache in Memory
Iteration 1: Memory Read → Process
Iteration 2: Memory Read → Process
Iteration 3: Memory Read → Process
Final: Memory Write → HDFS Write
```

### 2. DAG (Directed Acyclic Graph) Execution
- **More flexible** than MapReduce model
- Represents entire **workflow**
- **Optimizes** full pipeline, not individual stages
- **Catalyst optimizer** for SQL queries

**Advantages**:
- Better optimization opportunities
- Efficient pipeline execution
- Avoids unnecessary intermediate writes

### 3. Fault Tolerance
- **Lineage-based recovery**
- RDDs remember **how they were built**
- Can **recompute** lost partitions
- No need to replicate intermediate data

**How It Works**:
- If partition lost, recompute from parent RDD
- Uses **lineage graph**
- More efficient than data replication

### 4. Lazy Evaluation
- **Transformations** are lazy (not executed immediately)
- **Actions** trigger execution
- Allows Spark to **optimize** entire workflow

**Transformations** (Lazy):
- `map()`, `filter()`, `flatMap()`, `groupBy()`

**Actions** (Eager):
- `count()`, `collect()`, `save()`, `reduce()`

### 5. Multiple Processing Models
- **Batch processing** (like MapReduce)
- **Interactive queries** (like SQL databases)
- **Iterative algorithms** (machine learning)
- **Stream processing** (real-time)

## 6. Spark vs MapReduce

| Aspect | MapReduce | Spark |
|--------|-----------|-------|
| **Speed** | Baseline | 10-100x faster |
| **Processing** | Batch only | Batch, interactive, streaming, ML, graph |
| **Data Sharing** | Disk (HDFS) | Memory (+ disk) |
| **Ease of Use** | Low-level Java API | High-level APIs (Scala, Python, Java, R, SQL) |
| **Execution Model** | Map → Shuffle → Reduce | DAG-based, optimized |
| **Iterative Algorithms** | Inefficient | Efficient |
| **Real-time** | Not suitable | Spark Streaming |
| **Interactive Queries** | Not suitable | Suitable |
| **Learning Curve** | Steep | Moderate |
| **Maturity** | Very mature | Mature |

## 7. Spark Glossary (Key Terms)

### Application
- User program built on Spark
- Consists of driver program and executors

### Driver Program
- Process running `main()` function
- Creates SparkContext

### Cluster Manager
- External service for acquiring resources
- Examples: YARN, Mesos, Kubernetes, Standalone

### Deploy Mode
- Where driver process runs
- **Client**: On client machine
- **Cluster**: On cluster

### Worker Node
- Node that can run application code
- Hosts executors

### Executor
- Process launched for an application on worker node
- Runs tasks
- Keeps data in memory or disk

### Task
- Unit of work sent to executor
- Smallest unit of execution

### Job
- Parallel computation consisting of multiple tasks
- Spawned in response to action

### Stage
- Set of tasks that can be executed together
- Separated by shuffle operations

### RDD (Resilient Distributed Dataset)
- Fundamental data structure
- Immutable, distributed collection
- Fault-tolerant through lineage

### DataFrame
- Distributed collection of data organized into named columns
- Like RDD with schema
- Optimized execution

### Dataset
- Strongly-typed version of DataFrame
- Combines RDD type-safety with DataFrame optimization

---

## Key Points for Exam

### Core Concepts
1. **Spark = In-Memory Computing + DAG Execution**
2. **100x faster** in memory, 10x on disk (vs MapReduce)
3. **Unified platform**: Batch, interactive, streaming, ML, graph
4. **Multiple languages**: Scala, Python, Java, R, SQL
5. **Lazy evaluation**: Transformations lazy, actions eager

### Architecture Components
1. **Driver Program**: Main application, creates SparkContext
2. **SparkContext**: Entry point, coordinates executors
3. **Cluster Manager**: Acquires resources (YARN, Mesos, K8s, Standalone)
4. **Executor**: JVM process running tasks on worker
5. **Task**: Smallest unit of work

### Deployment Modes
**Client Mode**:
- Driver on client
- Good for interactive use
- Results to client

**Cluster Mode**:
- Driver on cluster
- Good for production
- More resilient

### Spark Components
1. **Spark Core**: Foundation, in-memory computing
2. **Spark SQL**: Structured data, DataFrames
3. **Spark Streaming**: Real-time, micro-batches
4. **MLlib**: Machine learning, distributed algorithms
5. **GraphX**: Graph processing, PageRank
6. **SparkR**: R integration

### Why Spark Over MapReduce?
1. **In-memory**: Avoids disk I/O
2. **Fast**: 10-100x faster
3. **General**: Multiple workloads
4. **High-level APIs**: Easier to use
5. **DAG**: Better optimization
6. **Interactive**: Low-latency queries
7. **Iterative**: Efficient ML algorithms

### Key Features
1. **In-memory computing**: Store intermediate results
2. **DAG execution**: Optimize entire workflow
3. **Fault tolerance**: Lineage-based recovery
4. **Lazy evaluation**: Optimize before execution
5. **Unified platform**: One engine, multiple workloads

### MapReduce Problems Spark Solves
1. **I/O latency**: In-memory computing
2. **Low-level API**: High-level abstractions
3. **Data sharing**: Memory storage, not disk
4. **Interactive queries**: Low latency
5. **Iterative algorithms**: Reuse cached data

### Critical to Remember
- **Driver** contains application logic
- **Executor** runs tasks, caches data
- **SparkContext** is entry point
- **Cluster Manager** allocates resources
- **In-memory** is key to speed
- **DAG** enables optimization
- **Lineage** enables fault tolerance
- **Lazy evaluation** allows optimization

### Use Spark When
- Iterative algorithms (ML)
- Interactive queries
- Real-time stream processing
- Complex DAG workflows
- Need speed over MapReduce
- In-memory fits dataset

### Use MapReduce When
- Simple batch processing
- One-pass over data
- Dataset too large for memory
- Conservative, proven technology needed
