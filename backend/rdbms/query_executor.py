"""
Query Executor for Custom RDBMS
Executes parsed SQL queries using the storage engine
"""
from typing import Dict, List, Any, Optional
from .storage_engine import StorageEngine
from .query_parser import QueryParser

class QueryExecutor:
    def __init__(self, storage_engine: StorageEngine):
        self.storage = storage_engine
        self.parser = QueryParser()
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        try:
            parsed_query = self.parser.parse(query)
            
            query_type = parsed_query['type']
            
            if query_type == 'CREATE_TABLE':
                return self._execute_create_table(parsed_query)
            elif query_type == 'INSERT':
                return self._execute_insert(parsed_query)
            elif query_type == 'SELECT':
                return self._execute_select(parsed_query)
            elif query_type == 'SELECT_JOIN':
                return self._execute_select_join(parsed_query)
            elif query_type == 'UPDATE':
                return self._execute_update(parsed_query)
            elif query_type == 'DELETE':
                return self._execute_delete(parsed_query)
            elif query_type == 'SHOW_TABLES':
                return self._execute_show_tables()
            elif query_type == 'DESCRIBE':
                return self._execute_describe(parsed_query)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported query type: {query_type}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_create_table(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute CREATE TABLE"""
        try:
            self.storage.create_table(
                parsed_query['table'],
                parsed_query['columns']
            )
            return {
                'success': True,
                'message': f"Table '{parsed_query['table']}' created successfully"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_insert(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute INSERT"""
        try:
            table_name = parsed_query['table']
            values = parsed_query['values']
            
            # Get table schema
            schema = self.storage.get_table_schema(table_name)
            columns = list(schema['columns'].keys())
            
            # Build row data
            row_data = {}
            
            if 'columns' in parsed_query:
                # INSERT INTO table (col1, col2) VALUES (val1, val2)
                specified_columns = parsed_query['columns']
                if len(specified_columns) != len(values):
                    raise ValueError("Column count doesn't match value count")
                
                for col, val in zip(specified_columns, values):
                    row_data[col] = val
            else:
                # INSERT INTO table VALUES (val1, val2, ...)
                if len(values) != len(columns):
                    raise ValueError(f"Expected {len(columns)} values, got {len(values)}")
                
                for col, val in zip(columns, values):
                    row_data[col] = val
            
            row_id = self.storage.insert_row(table_name, row_data)
            
            return {
                'success': True,
                'message': f"Row inserted with ID {row_id}",
                'row_id': row_id
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_select(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute SELECT"""
        try:
            table_name = parsed_query['table']
            columns = parsed_query['columns']
            where_clause = parsed_query.get('where')
            
            # Get rows
            rows = self.storage.select_rows(table_name, where_clause)
            
            # Project columns
            if columns == ['*']:
                # Return all columns except internal _row_id
                result_rows = []
                for row in rows:
                    clean_row = {k: v for k, v in row.items() if not k.startswith('_')}
                    result_rows.append(clean_row)
            else:
                # Return only specified columns
                result_rows = []
                for row in rows:
                    projected_row = {}
                    for col in columns:
                        if col in row:
                            projected_row[col] = row[col]
                    result_rows.append(projected_row)
            
            return {
                'success': True,
                'rows': result_rows,
                'count': len(result_rows)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_select_join(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute SELECT with JOIN"""
        try:
            table1 = parsed_query['table1']
            table2 = parsed_query['table2']
            join_condition = parsed_query['join_condition']
            columns = parsed_query['columns']
            where_clause = parsed_query.get('where')
            
            # Get all rows from both tables
            rows1 = self.storage.select_rows(table1)
            rows2 = self.storage.select_rows(table2)
            
            # Perform inner join
            joined_rows = []
            
            for row1 in rows1:
                for row2 in rows2:
                    # Check join condition
                    if self._evaluate_join_condition(row1, row2, join_condition, table1, table2):
                        # Combine rows
                        joined_row = {}
                        
                        # Add columns from table1 with table prefix
                        for col, val in row1.items():
                            if not col.startswith('_'):
                                joined_row[f"{table1}.{col}"] = val
                        
                        # Add columns from table2 with table prefix
                        for col, val in row2.items():
                            if not col.startswith('_'):
                                joined_row[f"{table2}.{col}"] = val
                        
                        joined_rows.append(joined_row)
            
            # Apply WHERE clause if present
            if where_clause:
                filtered_rows = []
                for row in joined_rows:
                    if self._matches_where_clause_join(row, where_clause):
                        filtered_rows.append(row)
                joined_rows = filtered_rows
            
            # Project columns
            if columns == ['*']:
                result_rows = joined_rows
            else:
                result_rows = []
                for row in joined_rows:
                    projected_row = {}
                    for col in columns:
                        col = col.strip()
                        if col in row:
                            projected_row[col] = row[col]
                        else:
                            # Try to find column without table prefix
                            for row_col in row:
                                if row_col.endswith(f".{col}"):
                                    projected_row[col] = row[row_col]
                                    break
                    result_rows.append(projected_row)
            
            return {
                'success': True,
                'rows': result_rows,
                'count': len(result_rows)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_update(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute UPDATE"""
        try:
            table_name = parsed_query['table']
            updates = parsed_query['updates']
            where_clause = parsed_query.get('where')
            
            if not where_clause:
                raise ValueError("UPDATE without WHERE clause not allowed for safety")
            
            updated_count = self.storage.update_rows(table_name, updates, where_clause)
            
            return {
                'success': True,
                'message': f"Updated {updated_count} row(s)",
                'updated_count': updated_count
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_delete(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute DELETE"""
        try:
            table_name = parsed_query['table']
            where_clause = parsed_query['where']
            
            deleted_count = self.storage.delete_rows(table_name, where_clause)
            
            return {
                'success': True,
                'message': f"Deleted {deleted_count} row(s)",
                'deleted_count': deleted_count
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_show_tables(self) -> Dict[str, Any]:
        """Execute SHOW TABLES"""
        try:
            tables = self.storage.list_tables()
            return {
                'success': True,
                'tables': tables,
                'count': len(tables)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_describe(self, parsed_query: Dict) -> Dict[str, Any]:
        """Execute DESCRIBE"""
        try:
            table_name = parsed_query['table']
            schema = self.storage.get_table_schema(table_name)
            
            # Format schema for display
            columns_info = []
            for col_name, col_def in schema['columns'].items():
                constraints = []
                if col_def.get('primary_key'):
                    constraints.append('PRIMARY KEY')
                if col_def.get('unique') and not col_def.get('primary_key'):
                    constraints.append('UNIQUE')
                if col_def.get('not_null'):
                    constraints.append('NOT NULL')
                
                columns_info.append({
                    'column': col_name,
                    'type': col_def['type'],
                    'constraints': ', '.join(constraints) if constraints else None
                })
            
            return {
                'success': True,
                'table': table_name,
                'columns': columns_info,
                'row_count': schema['row_count']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_join_condition(self, row1: Dict, row2: Dict, condition: Dict, 
                                table1: str, table2: str) -> bool:
        """Evaluate JOIN condition"""
        left_col = condition['left']
        right_col = condition['right']
        
        # Extract table and column names
        if '.' in left_col:
            left_table, left_col = left_col.split('.', 1)
        else:
            left_table = table1
        
        if '.' in right_col:
            right_table, right_col = right_col.split('.', 1)
        else:
            right_table = table2
        
        # Get values
        left_val = row1.get(left_col) if left_table == table1 else row2.get(left_col)
        right_val = row2.get(right_col) if right_table == table2 else row1.get(right_col)
        
        return left_val == right_val
    
    def _matches_where_clause_join(self, row: Dict, where_clause: Dict) -> bool:
        """Check if joined row matches WHERE clause"""
        for col_name, condition in where_clause.items():
            # Handle table-prefixed column names
            row_value = None
            
            if col_name in row:
                row_value = row[col_name]
            else:
                # Try to find column with table prefix
                for row_col in row:
                    if row_col.endswith(f".{col_name}"):
                        row_value = row[row_col]
                        break
            
            if isinstance(condition, dict):
                # Handle operators
                for op, value in condition.items():
                    if op == '=' and row_value != value:
                        return False
                    elif op == '>' and (row_value is None or row_value <= value):
                        return False
                    elif op == '<' and (row_value is None or row_value >= value):
                        return False
                    elif op == '>=' and (row_value is None or row_value < value):
                        return False
                    elif op == '<=' and (row_value is None or row_value > value):
                        return False
                    elif op == '!=' and row_value == value:
                        return False
            else:
                # Simple equality
                if row_value != condition:
                    return False
        
        return True
    
    def show_tables(self) -> Dict[str, Any]:
        """Convenience method to show tables"""
        return self._execute_show_tables()
    
    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Convenience method to describe table"""
        return self._execute_describe({'table': table_name})