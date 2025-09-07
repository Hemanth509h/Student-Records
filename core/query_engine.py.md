# core/query_engine.py - SQL-like Query Processing Engine

## Overview
This module implements a custom SQL-like query processing engine that operates on the LinkedList-based student data storage. It contains 315 lines of code that provide powerful data filtering, sorting, and aggregation capabilities without requiring a traditional database.

## Purpose
- **Query Processing**: Execute SQL-like commands on custom data structures
- **Data Analysis**: Enable complex data filtering and aggregation
- **User Interface**: Provide familiar SQL syntax for data queries
- **Educational Tool**: Demonstrate query processing algorithms and techniques

## Supported SQL Operations

### SELECT Statement
- **Basic Selection**: `SELECT * FROM students`
- **Field Selection**: `SELECT name, email FROM students`
- **Calculated Fields**: Support for basic calculations and expressions

### WHERE Clause
- **Comparison Operators**: `=`, `!=`, `>`, `<`, `>=`, `<=`
- **String Matching**: `LIKE` with wildcard support
- **Logical Operators**: `AND`, `OR`, `NOT`
- **Parentheses**: Grouped conditions for complex logic

### ORDER BY Clause
- **Ascending Order**: `ORDER BY name ASC`
- **Descending Order**: `ORDER BY grade DESC`
- **Multiple Fields**: `ORDER BY course, grade DESC`
- **Numeric Sorting**: Proper handling of numeric vs. string sorting

### LIMIT Clause
- **Result Limiting**: `LIMIT 10` - restrict number of results
- **Pagination Support**: Useful for large dataset management
- **Performance Optimization**: Reduces processing time for large queries

### GROUP BY Clause
- **Data Aggregation**: Group students by course, grade level, etc.
- **Count Operations**: Count students in each group
- **Statistical Functions**: Average, sum, min, max calculations

## Core Classes and Methods

### QueryEngine Class
Main class that orchestrates all query processing operations.

#### Key Methods:
- **`execute_query(query_string)`**: Main entry point for query execution
- **`_parse_query(query)`**: Breaks down SQL string into components
- **`_apply_where_clause(students, conditions)`**: Filters data based on conditions
- **`_apply_order_by(students, order_clause)`**: Sorts results
- **`_apply_group_by(students, group_clause)`**: Groups and aggregates data
- **`_apply_limit(students, limit_clause)`**: Restricts result set size

### Query Parsing Engine
Advanced parsing system that handles complex SQL syntax.

#### Features:
- **Tokenization**: Breaks query into meaningful components
- **Syntax Validation**: Ensures query follows proper SQL structure
- **Error Detection**: Identifies and reports syntax errors
- **Case Insensitive**: Handles both uppercase and lowercase SQL keywords

### Condition Evaluation System
Sophisticated system for evaluating WHERE clause conditions.

#### Supported Patterns:
- **Field Comparisons**: `grade > 85`
- **String Matching**: `name LIKE 'John%'`
- **Numeric Ranges**: `grade BETWEEN 80 AND 90`
- **Multiple Conditions**: `grade > 80 AND course = 'Math'`
- **Nested Logic**: `(grade > 90) OR (course = 'Computer Science' AND grade > 85)`

## Technical Implementation

### Query Processing Pipeline
1. **Lexical Analysis**: Break query into tokens
2. **Syntax Parsing**: Validate SQL structure
3. **Semantic Analysis**: Verify field names and data types
4. **Execution Planning**: Optimize query execution order
5. **Data Processing**: Apply filters, sorts, and aggregations
6. **Result Formatting**: Prepare output for display

### Performance Optimizations
- **Early Filtering**: Apply WHERE conditions before sorting
- **Efficient Sorting**: Use optimized sorting algorithms
- **Lazy Evaluation**: Process only necessary data
- **Memory Management**: Minimize memory usage during processing

### Error Handling
- **Syntax Errors**: Clear messages for invalid SQL syntax
- **Runtime Errors**: Graceful handling of data type mismatches
- **Field Validation**: Check for valid field names
- **Data Integrity**: Ensure operations don't corrupt data

## Advanced Features

### Wildcard Support
- **LIKE Operator**: Pattern matching with % and _ wildcards
- **Case Insensitive**: Flexible string matching
- **Partial Matches**: Find substrings within fields

### Aggregation Functions
- **COUNT()**: Count records in groups
- **AVG()**: Calculate average values
- **SUM()**: Total numeric values
- **MIN()**: Find minimum values
- **MAX()**: Find maximum values

### Complex Queries
Example of supported complex query:
```sql
SELECT name, course, grade 
FROM students 
WHERE (grade > 85 AND course LIKE 'Computer%') 
   OR (grade > 90) 
ORDER BY grade DESC, name ASC 
LIMIT 10
```

## Integration with Application

### Web Interface Integration
- **Query Form**: HTML form for entering SQL commands
- **Result Display**: Formatted table output for query results
- **Error Messages**: User-friendly error reporting
- **Query History**: Optional storage of previous queries

### Data Source Integration
- **StudentManager Connection**: Direct access to LinkedList data
- **Real-time Processing**: Operates on current data state
- **Data Consistency**: Maintains data integrity during queries
- **Performance Monitoring**: Tracks query execution time

## Use Cases

### Academic Analytics
- Find top performers in specific courses
- Identify students needing academic support
- Analyze grade distributions across subjects
- Track course enrollment patterns

### Administrative Queries
- Generate student lists for specific criteria
- Create reports for academic committees
- Export data for external systems
- Validate data quality and completeness

### Educational Demonstrations
- Show practical applications of data structures
- Demonstrate query optimization techniques
- Illustrate algorithm design principles
- Provide hands-on learning experiences

## Future Enhancement Possibilities
- **JOIN Operations**: Connect multiple data sources
- **Subqueries**: Nested query support
- **Views**: Saved query definitions
- **Indexes**: Performance optimization for large datasets
- **Transactions**: Multi-operation data consistency