"""
SQL Query Parser for Custom RDBMS
Parses SQL-like queries into structured format for execution
"""
import re
from typing import Dict, List, Any, Optional, Tuple

class QueryParser:
    def __init__(self):
        self.keywords = {
            'CREATE', 'TABLE', 'INSERT', 'INTO', 'VALUES', 'SELECT', 'FROM', 
            'WHERE', 'UPDATE', 'SET', 'DELETE', 'JOIN', 'ON', 'AND', 'OR',
            'PRIMARY', 'KEY', 'UNIQUE', 'NOT', 'NULL', 'SHOW', 'TABLES', 'DESCRIBE'
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse SQL query into structured format"""
        query = query.strip().rstrip(';')
        
        # Determine query type
        first_word = query.split()[0].upper()
        
        if first_word == 'CREATE':
            return self._parse_create_table(query)
        elif first_word == 'INSERT':
            return self._parse_insert(query)
        elif first_word == 'SELECT':
            return self._parse_select(query)
        elif first_word == 'UPDATE':
            return self._parse_update(query)
        elif first_word == 'DELETE':
            return self._parse_delete(query)
        elif first_word == 'SHOW':
            return self._parse_show(query)
        elif first_word == 'DESCRIBE':
            return self._parse_describe(query)
        else:
            raise ValueError(f"Unsupported query type: {first_word}")
    
    def _parse_create_table(self, query: str) -> Dict[str, Any]:
        """Parse CREATE TABLE statement"""
        # Pattern: CREATE TABLE table_name (column_definitions)
        pattern = r'CREATE\s+TABLE\s+(\w+)\s*\((.*)\)'
        match = re.match(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        
        columns = self._parse_column_definitions(columns_str)
        
        return {
            'type': 'CREATE_TABLE',
            'table': table_name,
            'columns': columns
        }
    
    def _parse_column_definitions(self, columns_str: str) -> Dict[str, Dict]:
        """Parse column definitions from CREATE TABLE"""
        columns = {}
        
        # Split by comma, but be careful with nested parentheses
        col_defs = self._split_by_comma(columns_str)
        
        for col_def in col_defs:
            col_def = col_def.strip()
            parts = col_def.split()
            
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = parts[0]
            col_type = parts[1]
            
            column_info = {
                'type': col_type,
                'not_null': False,
                'primary_key': False,
                'unique': False
            }
            
            # Parse constraints
            remaining = ' '.join(parts[2:]).upper()
            
            if 'PRIMARY KEY' in remaining:
                column_info['primary_key'] = True
                column_info['not_null'] = True  # Primary keys are automatically NOT NULL
            
            if 'UNIQUE' in remaining and 'PRIMARY KEY' not in remaining:
                column_info['unique'] = True
            
            if 'NOT NULL' in remaining:
                column_info['not_null'] = True
            
            columns[col_name] = column_info
        
        return columns
    
    def _parse_insert(self, query: str) -> Dict[str, Any]:
        """Parse INSERT statement"""
        # Pattern 1: INSERT INTO table VALUES (values)
        pattern1 = r'INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.*)\)'
        match1 = re.match(pattern1, query, re.IGNORECASE | re.DOTALL)
        
        if match1:
            table_name = match1.group(1)
            values_str = match1.group(2)
            values = self._parse_values(values_str)
            
            return {
                'type': 'INSERT',
                'table': table_name,
                'values': values
            }
        
        # Pattern 2: INSERT INTO table (columns) VALUES (values)
        pattern2 = r'INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s+VALUES\s*\((.*)\)'
        match2 = re.match(pattern2, query, re.IGNORECASE | re.DOTALL)
        
        if match2:
            table_name = match2.group(1)
            columns_str = match2.group(2)
            values_str = match2.group(3)
            
            columns = [col.strip() for col in columns_str.split(',')]
            values = self._parse_values(values_str)
            
            return {
                'type': 'INSERT',
                'table': table_name,
                'columns': columns,
                'values': values
            }
        
        raise ValueError("Invalid INSERT syntax")
    
    def _parse_select(self, query: str) -> Dict[str, Any]:
        """Parse SELECT statement"""
        result = {'type': 'SELECT'}
        
        # Handle JOIN
        if ' JOIN ' in query.upper():
            return self._parse_select_with_join(query)
        
        # Basic SELECT pattern
        pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?'
        match = re.match(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_str = match.group(3)
        
        # Parse columns
        if columns_str == '*':
            result['columns'] = ['*']
        else:
            result['columns'] = [col.strip() for col in columns_str.split(',')]
        
        result['table'] = table_name
        
        # Parse WHERE clause
        if where_str:
            result['where'] = self._parse_where_clause(where_str)
        
        return result
    
    def _parse_select_with_join(self, query: str) -> Dict[str, Any]:
        """Parse SELECT with JOIN"""
        # Pattern: SELECT columns FROM table1 JOIN table2 ON condition [WHERE condition]
        pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)\s+JOIN\s+(\w+)\s+ON\s+(.*?)(?:\s+WHERE\s+(.*))?$'
        match = re.match(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid SELECT with JOIN syntax")
        
        columns_str = match.group(1).strip()
        table1 = match.group(2)
        table2 = match.group(3)
        join_condition = match.group(4).strip()
        where_str = match.group(5)
        
        result = {
            'type': 'SELECT_JOIN',
            'table1': table1,
            'table2': table2,
            'join_condition': self._parse_join_condition(join_condition)
        }
        
        # Parse columns
        if columns_str == '*':
            result['columns'] = ['*']
        else:
            result['columns'] = [col.strip() for col in columns_str.split(',')]
        
        # Parse WHERE clause
        if where_str:
            result['where'] = self._parse_where_clause(where_str)
        
        return result
    
    def _parse_update(self, query: str) -> Dict[str, Any]:
        """Parse UPDATE statement"""
        pattern = r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?'
        match = re.match(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_str = match.group(2)
        where_str = match.group(3)
        
        result = {
            'type': 'UPDATE',
            'table': table_name,
            'updates': self._parse_set_clause(set_str)
        }
        
        if where_str:
            result['where'] = self._parse_where_clause(where_str)
        
        return result
    
    def _parse_delete(self, query: str) -> Dict[str, Any]:
        """Parse DELETE statement"""
        pattern = r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?'
        match = re.match(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_str = match.group(2)
        
        result = {
            'type': 'DELETE',
            'table': table_name
        }
        
        if where_str:
            result['where'] = self._parse_where_clause(where_str)
        else:
            raise ValueError("DELETE without WHERE clause not allowed for safety")
        
        return result
    
    def _parse_show(self, query: str) -> Dict[str, Any]:
        """Parse SHOW statement"""
        if query.upper() == 'SHOW TABLES':
            return {'type': 'SHOW_TABLES'}
        else:
            raise ValueError("Invalid SHOW syntax")
    
    def _parse_describe(self, query: str) -> Dict[str, Any]:
        """Parse DESCRIBE statement"""
        pattern = r'DESCRIBE\s+(\w+)'
        match = re.match(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid DESCRIBE syntax")
        
        return {
            'type': 'DESCRIBE',
            'table': match.group(1)
        }
    
    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse VALUES clause"""
        values = []
        
        # Split by comma, handling quoted strings
        parts = self._split_by_comma(values_str)
        
        for part in parts:
            part = part.strip()
            values.append(self._parse_value(part))
        
        return values
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value"""
        value_str = value_str.strip()
        
        # NULL
        if value_str.upper() == 'NULL':
            return None
        
        # String (quoted)
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]  # Remove quotes
        
        # Boolean
        if value_str.upper() in ('TRUE', 'FALSE'):
            return value_str.upper() == 'TRUE'
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Default to string
        return value_str
    
    def _parse_where_clause(self, where_str: str) -> Dict[str, Any]:
        """Parse WHERE clause"""
        conditions = {}
        
        # Split by AND (simple implementation)
        and_parts = re.split(r'\s+AND\s+', where_str, flags=re.IGNORECASE)
        
        for part in and_parts:
            part = part.strip()
            
            # Parse condition: column operator value
            for op in ['>=', '<=', '!=', '=', '>', '<']:
                if op in part:
                    col_name, value_str = part.split(op, 1)
                    col_name = col_name.strip()
                    value = self._parse_value(value_str.strip())
                    
                    if op == '=':
                        conditions[col_name] = value
                    else:
                        conditions[col_name] = {op: value}
                    break
        
        return conditions
    
    def _parse_set_clause(self, set_str: str) -> Dict[str, Any]:
        """Parse SET clause for UPDATE"""
        updates = {}
        
        assignments = self._split_by_comma(set_str)
        
        for assignment in assignments:
            assignment = assignment.strip()
            if '=' not in assignment:
                raise ValueError(f"Invalid assignment: {assignment}")
            
            col_name, value_str = assignment.split('=', 1)
            col_name = col_name.strip()
            value = self._parse_value(value_str.strip())
            
            updates[col_name] = value
        
        return updates
    
    def _parse_join_condition(self, condition_str: str) -> Dict[str, str]:
        """Parse JOIN ON condition"""
        condition_str = condition_str.strip()
        
        if '=' not in condition_str:
            raise ValueError("Invalid JOIN condition")
        
        left, right = condition_str.split('=', 1)
        left = left.strip()
        right = right.strip()
        
        return {
            'left': left,
            'right': right
        }
    
    def _split_by_comma(self, text: str) -> List[str]:
        """Split text by comma, respecting quotes and parentheses"""
        parts = []
        current = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0
        
        for char in text:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == '(' and not in_quotes:
                paren_depth += 1
                current += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                current += char
            elif char == ',' and not in_quotes and paren_depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            parts.append(current.strip())
        
        return parts