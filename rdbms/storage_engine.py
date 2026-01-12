"""
Storage Engine for Custom RDBMS
Handles data persistence, indexing, and basic storage operations
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class StorageEngine:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.tables: Dict[str, Dict] = {}
        self.indexes: Dict[str, Dict] = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing tables
        self._load_tables()
    
    def _load_tables(self):
        """Load existing tables from disk"""
        try:
            tables_file = os.path.join(self.data_dir, "tables.json")
            if os.path.exists(tables_file):
                with open(tables_file, 'r') as f:
                    self.tables = json.load(f)
            
            indexes_file = os.path.join(self.data_dir, "indexes.json")
            if os.path.exists(indexes_file):
                with open(indexes_file, 'r') as f:
                    self.indexes = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")
            self.tables = {}
            self.indexes = {}
    
    def _save_tables(self):
        """Save tables to disk"""
        try:
            with open(os.path.join(self.data_dir, "tables.json"), 'w') as f:
                json.dump(self.tables, f, indent=2)
            
            with open(os.path.join(self.data_dir, "indexes.json"), 'w') as f:
                json.dump(self.indexes, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def create_table(self, table_name: str, columns: Dict[str, Dict]):
        """Create a new table with specified columns and constraints"""
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists")
        
        # Validate column definitions
        primary_keys = []
        unique_keys = []
        
        for col_name, col_def in columns.items():
            if col_def.get('primary_key'):
                primary_keys.append(col_name)
            if col_def.get('unique'):
                unique_keys.append(col_name)
        
        if len(primary_keys) > 1:
            raise ValueError("Multiple primary keys not supported")
        
        self.tables[table_name] = {
            'columns': columns,
            'rows': [],
            'primary_key': primary_keys[0] if primary_keys else None,
            'unique_keys': unique_keys
        }
        
        # Create indexes for primary and unique keys
        self.indexes[table_name] = {}
        for key in primary_keys + unique_keys:
            self.indexes[table_name][key] = {}
        
        self._save_tables()
        return True
    
    def insert_row(self, table_name: str, row_data: Dict[str, Any]):
        """Insert a new row into the table"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        
        # Validate row data
        validated_row = {}
        for col_name, col_def in table['columns'].items():
            value = row_data.get(col_name)
            
            # Check NOT NULL constraint
            if col_def.get('not_null') and value is None:
                raise ValueError(f"Column '{col_name}' cannot be NULL")
            
            # Type validation and conversion
            if value is not None:
                validated_row[col_name] = self._validate_type(value, col_def['type'])
            else:
                validated_row[col_name] = None
        
        # Check primary key constraint
        if table['primary_key']:
            pk_value = validated_row[table['primary_key']]
            if pk_value in self.indexes[table_name][table['primary_key']]:
                raise ValueError(f"Primary key violation: {pk_value} already exists")
        
        # Check unique constraints
        for unique_key in table['unique_keys']:
            if unique_key != table['primary_key']:  # Primary key already checked
                uk_value = validated_row[unique_key]
                if uk_value and uk_value in self.indexes[table_name][unique_key]:
                    raise ValueError(f"Unique constraint violation: {uk_value} already exists")
        
        # Add row
        row_id = len(table['rows'])
        validated_row['_row_id'] = row_id
        table['rows'].append(validated_row)
        
        # Update indexes
        for index_col in self.indexes[table_name]:
            value = validated_row.get(index_col)
            if value is not None:
                self.indexes[table_name][index_col][value] = row_id
        
        self._save_tables()
        return row_id
    
    def select_rows(self, table_name: str, where_clause: Optional[Dict] = None):
        """Select rows from table with optional WHERE clause"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        rows = self.tables[table_name]['rows']
        
        if not where_clause:
            return rows
        
        # Simple WHERE clause filtering
        filtered_rows = []
        for row in rows:
            if self._matches_where_clause(row, where_clause):
                filtered_rows.append(row)
        
        return filtered_rows
    
    def update_rows(self, table_name: str, updates: Dict[str, Any], where_clause: Dict):
        """Update rows matching WHERE clause"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        updated_count = 0
        
        for i, row in enumerate(table['rows']):
            if self._matches_where_clause(row, where_clause):
                # Validate updates
                for col_name, new_value in updates.items():
                    if col_name in table['columns']:
                        col_def = table['columns'][col_name]
                        
                        # Check constraints for updated values
                        if col_def.get('primary_key') or col_name in table['unique_keys']:
                            # Check if new value conflicts with existing values
                            for j, other_row in enumerate(table['rows']):
                                if i != j and other_row.get(col_name) == new_value:
                                    raise ValueError(f"Constraint violation: {new_value} already exists")
                        
                        # Update the value
                        old_value = row.get(col_name)
                        row[col_name] = self._validate_type(new_value, col_def['type'])
                        
                        # Update indexes
                        if col_name in self.indexes[table_name]:
                            if old_value in self.indexes[table_name][col_name]:
                                del self.indexes[table_name][col_name][old_value]
                            self.indexes[table_name][col_name][new_value] = i
                
                updated_count += 1
        
        self._save_tables()
        return updated_count
    
    def delete_rows(self, table_name: str, where_clause: Dict):
        """Delete rows matching WHERE clause"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        rows_to_delete = []
        
        # Find rows to delete
        for i, row in enumerate(table['rows']):
            if self._matches_where_clause(row, where_clause):
                rows_to_delete.append(i)
        
        # Delete rows (in reverse order to maintain indices)
        for i in reversed(rows_to_delete):
            row = table['rows'][i]
            
            # Remove from indexes
            for index_col in self.indexes[table_name]:
                value = row.get(index_col)
                if value in self.indexes[table_name][index_col]:
                    del self.indexes[table_name][index_col][value]
            
            del table['rows'][i]
        
        # Rebuild row IDs and indexes
        self._rebuild_indexes(table_name)
        
        self._save_tables()
        return len(rows_to_delete)
    
    def _rebuild_indexes(self, table_name: str):
        """Rebuild indexes after row deletion"""
        table = self.tables[table_name]
        self.indexes[table_name] = {}
        
        # Reinitialize indexes
        for col_name in table['columns']:
            col_def = table['columns'][col_name]
            if col_def.get('primary_key') or col_def.get('unique'):
                self.indexes[table_name][col_name] = {}
        
        # Rebuild indexes
        for i, row in enumerate(table['rows']):
            row['_row_id'] = i
            for index_col in self.indexes[table_name]:
                value = row.get(index_col)
                if value is not None:
                    self.indexes[table_name][index_col][value] = i
    
    def _matches_where_clause(self, row: Dict, where_clause: Dict) -> bool:
        """Check if row matches WHERE clause conditions"""
        for col_name, condition in where_clause.items():
            row_value = row.get(col_name)
            
            if isinstance(condition, dict):
                # Handle operators like {'=': value}, {'>', value}
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
                # Simple equality check
                if row_value != condition:
                    return False
        
        return True
    
    def _validate_type(self, value: Any, data_type: str) -> Any:
        """Validate and convert value to specified data type"""
        if value is None:
            return None
        
        try:
            if data_type == 'INT':
                return int(value)
            elif data_type.startswith('VARCHAR'):
                str_val = str(value)
                # Extract max length from VARCHAR(n)
                if '(' in data_type:
                    max_len = int(data_type.split('(')[1].split(')')[0])
                    if len(str_val) > max_len:
                        raise ValueError(f"String too long: {len(str_val)} > {max_len}")
                return str_val
            elif data_type == 'FLOAT':
                return float(value)
            elif data_type == 'BOOLEAN':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif data_type == 'DATETIME':
                if isinstance(value, str):
                    return value  # Store as ISO string
                return str(value)
            else:
                return value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value '{value}' for type '{data_type}': {e}")
    
    def get_table_schema(self, table_name: str) -> Dict:
        """Get table schema information"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        return {
            'columns': self.tables[table_name]['columns'],
            'primary_key': self.tables[table_name]['primary_key'],
            'unique_keys': self.tables[table_name]['unique_keys'],
            'row_count': len(self.tables[table_name]['rows'])
        }
    
    def list_tables(self) -> List[str]:
        """Get list of all table names"""
        return list(self.tables.keys())
    
    def drop_table(self, table_name: str):
        """Drop a table"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        del self.tables[table_name]
        if table_name in self.indexes:
            del self.indexes[table_name]
        
        self._save_tables()
        return True