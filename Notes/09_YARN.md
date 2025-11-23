# Topic 9: YARN (Yet Another Resource Negotiator)

## 1. What is YARN?

### Definition
- **Core subsystem** in Hadoop for resource management
- **Introduced in Hadoop 2** to improve MapReduce
- **General enough** to support other distributed computing paradigms (not just MapReduce)

### Purpose
- **Govern, allocate, and manage** distributed processing resources
- **Resource management layer** for Hadoop cluster
- Separates resource management from application logic

## 2. YARN Architecture

### Key Components

#### 1. ResourceManager (One per cluster)
**Role**: Master daemon managing cluster resources

**Location**: Runs on **master node**

**Key Functions**:
- **Allocate cluster resources** to applications
- **Track heartbeats** from NodeManagers
- **Run Scheduler** to determine resource allocation
- **Manage cluster-level security**
- **Handle resource requests** from ApplicationMasters
- **Monitor ApplicationMaster** status
- **Restart containers** upon ApplicationMaster failure
- **Deallocate containers** when application completes

**Components**:
1. **Scheduler**: Allocates resources (doesn't monitor/track)
2. **ApplicationManager**: Accepts jobs, negotiates first container

**Important**: ResourceManager is **pure management** - does NOT execute actual data processing

#### 2. NodeManager (One per slave node)
**Role**: Slave daemon managing resources on individual nodes

**Location**: Runs on **every slave/worker node**

**Key Functions**:
- **Launch and monitor containers** on the node
- **Register with ResourceManager** through heartbeats
- **Communicate container status** to ResourceManager
- **Manage resource consumption** (CPU/memory) by containers
- **Track node health** and report to ResourceManager
- **Provide auxiliary services** (e.g., MapReduce shuffle)
- **Manage application lifecycle** on the node

**Heartbeat Communication**:
- Sends periodic heartbeats to ResourceManager
- Confirms NodeManager is alive and healthy
- Reports available resources
- Receives container launch/kill commands

#### 3. ApplicationMaster (One per application)
**Role**: Per-application coordinator

**Location**: Runs in a **container** on a NodeManager

**Lifecycle**: 
- **First container** allocated by ResourceManager
- Created when application starts
- **Destroyed** when application completes

**Key Functions**:
- **Request resources** from ResourceManager
- **Negotiate containers** for application tasks
- **Monitor task execution** and progress
- **Manage task scheduling** within application
- **Handle task failures** and retries
- **Report progress** to ResourceManager
- **Coordinate application completion**

**Resource Requests**:
Very specific, including:
- File blocks needed for processing
- Number of containers required
- Size of each container (memory, CPU)
- Data locality preferences

#### 4. Container
**Definition**: 
- **Logical construct** representing resources
- **Running environment** for an application

**Contents**:
- Specific amount of **memory**
- **Processing cores** (CPU)
- **Disk** and **network** resources

**Example**: 
- Container = 2GB memory + 2 processing cores

**Types**:
1. **ApplicationMaster Container**: First container for application
2. **Task Containers**: For Map and Reduce tasks

## 3. YARN Application Workflow

### Step-by-Step Process

**Step 1: Client Submits Job**
- Client program submits **application** to ResourceManager
- Application includes:
  - Job JAR files
  - Configuration
  - Input data locations

**Step 2: ResourceManager Allocates Container**
- ResourceManager **selects** a NodeManager
- **Allocates first container** for ApplicationMaster
- Considers:
  - Available resources
  - Data locality
  - Node health

**Step 3: ApplicationMaster Starts**
- NodeManager **launches** ApplicationMaster container
- ApplicationMaster **initializes** and **registers** with ResourceManager
- Prepares to execute application

**Step 4: ApplicationMaster Requests Resources**
- Analyzes application requirements
- **Requests containers** from ResourceManager
  - Specifies: memory, CPU, data locality
- May request containers multiple times during execution

**Step 5: ResourceManager Allocates Containers**
- **Scheduler evaluates** resource requests
- **Allocates containers** on available NodeManagers
- Sends **container tokens** to ApplicationMaster
- Considers:
  - Available resources
  - Scheduler policy
  - Data locality

**Step 6: ApplicationMaster Launches Tasks**
- Contacts NodeManagers with **container tokens**
- NodeManagers **launch containers** for tasks
- ApplicationMaster **monitors task execution**
- Tasks execute (e.g., Map/Reduce operations)

**Step 7: Tasks Execute and Report**
- Tasks **process data** in their containers
- **Report progress** to ApplicationMaster
- ApplicationMaster **aggregates progress**
- Reports to ResourceManager

**Step 8: Application Completes**
- All tasks finish successfully (or fail and retry)
- ApplicationMaster **signals completion** to ResourceManager
- ResourceManager **deallocates** all containers
- ApplicationMaster container **terminated**
- Resources **freed** for other applications

## 4. Key Concepts

### Client
- **Program that submits** jobs to cluster
- Can be **gateway machine** where client runs
- Interacts with ResourceManager

### Job/Application
- **Unit of work** submitted to cluster
- Contains one or more **tasks**
- Example: MapReduce job

### Task
- **Unit of execution** within job
- **Map task** or **Reduce task** in MapReduce
- Runs within a **container**

### Container Allocation
- Based on **resource availability**
- Considers **data locality** (move computation to data)
- **Scheduler policy** (FIFO, Fair, Capacity)

### Data Locality
- **Prefer** containers on nodes with data
- **Same node** > **Same rack** > **Different rack**
- Minimizes network transfer

## 5. YARN vs MapReduce 1

### MapReduce 1 (Hadoop 1)
- **JobTracker**: Single point of failure
- **TaskTrackers**: Fixed map/reduce slots
- **Scalability limits**: ~4000 nodes
- **Only MapReduce** supported

### YARN (Hadoop 2+)
- **ResourceManager**: Can have standby (HA)
- **Generic containers**: Flexible resource allocation
- **Scalability**: 10,000+ nodes
- **Multiple frameworks**: MapReduce, Spark, Tez, etc.

### Key Improvements
1. **Separation of concerns**:
   - Resource management (ResourceManager)
   - Application logic (ApplicationMaster)

2. **Scalability**:
   - Better resource utilization
   - Support for larger clusters

3. **Multi-tenancy**:
   - Multiple frameworks simultaneously
   - Better resource sharing

4. **Efficiency**:
   - Generic containers (not fixed slots)
   - Dynamic resource allocation

## 6. YARN Schedulers

### 1. FIFO Scheduler
- **First In, First Out**
- Simple queue
- **Disadvantage**: Large jobs block small ones

### 2. Capacity Scheduler
- **Multiple queues**
- Each queue has **minimum capacity guarantee**
- **Elasticity**: Unused capacity shared
- **Good for**: Multiple organizations sharing cluster

### 3. Fair Scheduler
- **Equal share** of resources to applications
- **Preemption**: Can kill containers to enforce fairness
- **Good for**: Multi-user environments

---

## Key Points for Exam

### Core Architecture
1. **ResourceManager**: Cluster-level resource manager (1 per cluster)
2. **NodeManager**: Node-level resource manager (1 per node)
3. **ApplicationMaster**: Application coordinator (1 per application)
4. **Container**: Resource allocation unit

### Key Daemons
**Master**:
- ResourceManager (YARN master)
- NameNode (HDFS master)

**Slave**:
- NodeManager (YARN slave)
- DataNode (HDFS slave)

### Container Characteristics
- **Memory** + **CPU** allocation
- **Logical construct** (not physical isolation like Docker)
- **First container**: ApplicationMaster
- **Subsequent containers**: Application tasks

### Application Flow (8 Steps)
1. Client submits job
2. RM allocates AM container
3. AM starts
4. AM requests resources
5. RM allocates containers
6. AM launches tasks
7. Tasks execute
8. Application completes

### ResourceManager Components
- **Scheduler**: Allocates resources
- **ApplicationsManager**: Manages ApplicationMasters

### Key Differences from Hadoop 1
- **Separation**: Resource management vs. application logic
- **Scalability**: 10,000+ nodes vs. 4,000
- **Flexibility**: Multiple frameworks vs. MapReduce only
- **Efficiency**: Generic containers vs. fixed slots

### Important Characteristics
- **Pure management**: RM doesn't process data
- **Per-application**: Each application has its own AM
- **Heartbeats**: NodeManagers report to ResourceManager
- **Data locality**: Preferred container placement
- **Resource-aware**: CPU, memory, disk, network

### What Each Component Does

**ResourceManager**:
- Allocates resources
- Monitors cluster
- Manages ApplicationMasters
- Does NOT process data

**NodeManager**:
- Launches containers
- Monitors resources
- Reports to ResourceManager
- Manages node health

**ApplicationMaster**:
- Coordinates application
- Requests resources
- Schedules tasks
- Monitors progress

**Container**:
- Runs task/ApplicationMaster
- Has allocated resources
- Isolated execution environment

### Critical to Remember
1. **YARN = Resource Management Layer**
2. **Separates** resource management from application logic
3. **Generic framework**: Supports MapReduce, Spark, Tez, etc.
4. **First container** always for ApplicationMaster
5. **ResourceManager** is pure management (no data processing)
6. **One ApplicationMaster** per application
7. **Containers** are logical, not physical isolation
8. **Data locality** important for performance
