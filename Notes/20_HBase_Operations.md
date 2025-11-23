# Topic 20: HBase Operations

## 1. HBase Shell

### What is HBase Shell?

**Type**: **JRuby-based** (Java Interactive Ruby - JIRB) shell

**Characteristics**:
- **REPL** (Read-Eval-Print-Loop) shell
- Interactive environment
- Executes commands piecewise
- Allows Ruby script computation

### Script Execution

**Load script from file**:
```ruby
source 'file-name.hb'
```

---

## 2. Data Definition (DDL) Commands

### Command List

**DDL Commands**: `create`, `list`, `describe`, `disable`, `disable_all`, `enable`, `enable_all`, `drop`, `drop_all`, `show_filters`, `alter`, `alter_status`

---

### CREATE - Create Table

**Syntax**:
```ruby
create 'table_name', 'column_family1', 'column_family2', ...
```

**Example**:
```ruby
create 'student', 'personal'
```
- Creates table `student` with one column family `personal`

---

### DESCRIBE - Show Table Structure

```ruby
describe 'student'
```
- Shows table structure and properties

---

### ALTER - Modify Table

#### Add Column Family

```ruby
alter 'student', {NAME=>'uni', VERSIONS=>'4'}
```
- Adds column family `uni` with 4 versions allowed

```ruby
alter 'student', {NAME=>'university', VERSIONS=>5}
```
- Adds column family `university` with 5 versions

#### Modify Column Family Properties

**Set IN_MEMORY**:
```ruby
alter 'student', {NAME=>'personal', IN_MEMORY=>true}
```
- Keeps column family in transient memory (cache)

**Change Version Limit**:
```ruby
alter 'student', {NAME=>'personal', VERSIONS=>3}
```
- Increases versions from default (3) to 3

#### Delete Column Family

```ruby
alter 'student', 'delete'=>'uni'
```
- Removes column family `uni` from table

---

## 3. Data Manipulation (DML) Commands

### Command List

**DML Commands**: `count`, `put`, `get`, `delete`, `deleteall`, `truncate`, `scan`

---

### PUT - Insert/Update Data

**Syntax**:
```ruby
put 'table', 'row_key', 'family:qualifier', 'value'
```

**Examples**:
```ruby
put 'student', '007', 'personal:first-name', 'James'
put 'student', '007', 'personal:last-name', 'Bond'
put 'student', '007', 'personal:dob', '01-OCT-1960'
```

**Create New Version**:
```ruby
put 'student', '007', 'personal:dob', '02-OCT-1960'
```
- Adds second version (new timestamp)

---

### GET - Retrieve Data

**Get Entire Row**:
```ruby
get 'student', '666'
```

**Get Specific Column**:
```ruby
get 'student', '007', {COLUMN=>'personal:dob'}
```

**Get Multiple Versions**:
```ruby
get 'student', '007', {COLUMN=>'personal:dob', VERSIONS=>5}
```
- Returns up to 5 versions

**Get Column Family**:
```ruby
get 'student', '666', {COLUMN=>'grade', VERSIONS=>5}
```

**Get Specific Column with Versions**:
```ruby
get 'student', '666', {COLUMN=>'grade:CSCI235', VERSIONS=>5}
```

---

### SCAN - Retrieve Multiple Rows

**Scan Entire Table (1 version)**:
```ruby
scan 'student'
```

**Scan with Multiple Versions**:
```ruby
scan 'student', {VERSIONS=>5}
```

**Scan Specific Column**:
```ruby
scan 'student', {COLUMNS=>'personal:dob', VERSIONS=>5}
```

**Scan Multiple Column Families**:
```ruby
scan 'student', {COLUMNS=>['personal', 'university']}
```

**Scan with Time Range**:
```ruby
scan 'student', {COLUMNS=>'personal:dob', TIMERANGE=>[1, 1502609828830], VERSIONS=>5}
```

**Scan with Filter (Time)**:
```ruby
scan 'student', {COLUMNS=>'personal:dob', FILTER=>"TimestampsFilter(1,1502609828830)", VERSIONS=>5}
```

---

### Filters in SCAN

**Qualifier Filter** (Column name >= 'f'):
```ruby
scan 'student', {FILTER=>"QualifierFilter(>=,'binary:f')"}
```

**Value Filter** (Cell value >= 'J'):
```ruby
scan 'student', {FILTER=>"ValueFilter(>=,'binary:J')"}
```

**Combined Filter** (Value in range [J,K]):
```ruby
scan 'student', {FILTER=>"ValueFilter(>=,'binary:J') AND ValueFilter(<=,'binary:K')"}
```

**Multiple Filters**:
```ruby
scan 'student', {COLUMNS=>'personal:dob', FILTER=>"QualifierFilter(=,'binary:dob') AND ValueFilter(=,'binary:02-OCT-1960')"}
```
- Returns rows where dob column = '02-OCT-1960'

---

### DELETE - Remove Data

**Delete Single Cell**:
```ruby
delete 'student', '666', 'grade:CSCI235'
```
- Deletes cell `CSCI235` from row `666`

**Delete Entire Row**:
```ruby
deleteall 'student', '007'
```
- Deletes all cells in row `007`

---

### COUNT - Count Rows

```ruby
count 'student'
```
- Returns total number of rows

---

## 4. HBase Java API

### Overview

**Purpose**: Access HBase from Java programs

**Features**:
- Data definition (DDL)
- Data manipulation (DML)

---

### Create Table

**Required Imports**:
```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.HBaseAdmin;
```

**Code**:
```java
public class CreateTable {
    public static void main(String[] args) throws Exception {
        Configuration conf = HBaseConfiguration.create();
        HBaseAdmin admin = new HBaseAdmin(conf);
        
        HTableDescriptor tableDescriptor = new HTableDescriptor(TableName.valueOf("my-table"));
        tableDescriptor.addFamily(new HColumnDescriptor("Address"));
        tableDescriptor.addFamily(new HColumnDescriptor("Name"));
        
        admin.createTable(tableDescriptor);
        
        boolean tableAvailable = admin.isTableAvailable("my-table");
        System.out.println("tableAvailable = " + tableAvailable);
    }
}
```

---

### Insert Data (PUT)

**Additional Import**:
```java
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.util.Bytes;
```

**Code**:
```java
public class PutRow {
    public static void main(String[] args) throws Exception {
        Configuration conf = HBaseConfiguration.create();
        HTable table = new HTable(conf, "my-table");
        
        Put put = new Put(Bytes.toBytes("007"));  // Row key
        put.add(Bytes.toBytes("Address"), Bytes.toBytes("City"), Bytes.toBytes("Dapto"));
        put.add(Bytes.toBytes("Address"), Bytes.toBytes("Street"), Bytes.toBytes("Ellenborough"));
        put.add(Bytes.toBytes("Name"), Bytes.toBytes("First"), Bytes.toBytes("James"));
        put.add(Bytes.toBytes("Name"), Bytes.toBytes("Last"), Bytes.toBytes("Bond"));
        
        table.put(put);
        table.flushCommits();
        table.close();
    }
}
```

**Key Points**:
- Use `Bytes.toBytes()` to convert strings to bytes
- `flushCommits()` ensures data is written
- Always `close()` table

---

### Retrieve Data (GET)

**Additional Imports**:
```java
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Result;
import java.util.Map;
import java.util.NavigableMap;
```

**Code - Get Specific Values**:
```java
public class GetRow {
    public static void main(String[] args) throws Exception {
        Configuration conf = HBaseConfiguration.create();
        HTable table = new HTable(conf, "my-table");
        
        Get get = new Get(Bytes.toBytes("007"));
        get.setMaxVersions(3);  // Get up to 3 versions
        get.addFamily(Bytes.toBytes("Address"));
        get.addColumn(Bytes.toBytes("Name"), Bytes.toBytes("First"));
        get.addColumn(Bytes.toBytes("Name"), Bytes.toBytes("Last"));
        
        Result result = table.get(get);
        String row = Bytes.toString(result.getRow());
        
        // Get specific value
        String specificValue = Bytes.toString(result.getValue(
            Bytes.toBytes("Address"), Bytes.toBytes("City")));
        System.out.println("Latest Address:City is: " + specificValue);
        
        specificValue = Bytes.toString(result.getValue(
            Bytes.toBytes("Address"), Bytes.toBytes("Street")));
        System.out.println("Latest Address:Street is: " + specificValue);
        
        specificValue = Bytes.toString(result.getValue(
            Bytes.toBytes("Name"), Bytes.toBytes("First")));
        System.out.println("Latest Name:First is: " + specificValue);
        
        specificValue = Bytes.toString(result.getValue(
            Bytes.toBytes("Name"), Bytes.toBytes("Last")));
        System.out.println("Latest Name:Last is: " + specificValue);
```

---

**Code - Traverse Entire Result**:
```java
        System.out.println("Row key: " + row);
        NavigableMap<byte[], NavigableMap<byte[], NavigableMap<Long, byte[]>>> map = result.getMap();
        
        for (Map.Entry<byte[], NavigableMap<byte[], NavigableMap<Long, byte[]>>> navigableMapEntry : map.entrySet()) {
            String family = Bytes.toString(navigableMapEntry.getKey());
            System.out.println("\t" + family);
            
            NavigableMap<byte[], NavigableMap<Long, byte[]>> familyContents = navigableMapEntry.getValue();
            for (Map.Entry<byte[], NavigableMap<Long, byte[]>> mapEntry : familyContents.entrySet()) {
                String qualifier = Bytes.toString(mapEntry.getKey());
                System.out.println("\t\t" + qualifier);
                
                NavigableMap<Long, byte[]> qualifierContents = mapEntry.getValue();
                for (Map.Entry<Long, byte[]> entry : qualifierContents.entrySet()) {
                    Long timestamp = entry.getKey();
                    String value = Bytes.toString(entry.getValue());
                    System.out.printf("\t\t\t%s, %d\n", value, timestamp);
                }
            }
        }
        table.close();
    }
}
```

**Output Structure**:
```
Row key: 007
    Address
        City
            Dapto, 1502609828830
        Street
            Ellenborough, 1502609828831
    Name
        First
            James, 1502609828832
        Last
            Bond, 1502609828833
```

---

## Summary: HBase Operations

### Shell Commands
- **DDL**: create, describe, alter (add/delete families, change versions)
- **DML**: put, get, scan, delete, deleteall, count
- **Filters**: QualifierFilter, ValueFilter, TimestampsFilter

### Java API Key Classes
- **Configuration**: HBaseConfiguration
- **Admin**: HBaseAdmin (create/modify tables)
- **Table**: HTable (data operations)
- **Operations**: Put, Get, Result
- **Utility**: Bytes (convert strings ↔ bytes)

### Important Patterns
- Always convert to bytes: `Bytes.toBytes()`
- Always close resources: `table.close()`
- Flush for immediate write: `flushCommits()`
- Navigate result hierarchically: Family → Qualifier → Timestamp

---

## Exam Tips

1. **Shell Syntax**: Know basic commands (create, put, get, scan, delete)
2. **Versions**: Default 3, configurable via ALTER
3. **Filters**: QualifierFilter, ValueFilter, combined with AND
4. **SCAN vs GET**: SCAN for multiple rows, GET for single row
5. **Java API Structure**:
   - Configuration → Admin/Table
   - Put/Get/Result classes
   - Bytes.toBytes() conversion
6. **NavigableMap**: Hierarchical structure for traversing results
7. **TIMERANGE vs TimestampsFilter**: Two ways to filter by time
8. **alter command**: Can add/delete families, change versions, set IN_MEMORY
9. **deleteall vs delete**: deleteall removes entire row, delete removes cell
10. **flushCommits()**: Ensures data written immediately

### Common Exam Questions
- Write HBase shell commands for given scenarios
- Create Java code to insert/retrieve data
- Explain filter usage in scan operations
- Modify table schema using alter
- Traverse Result object in Java