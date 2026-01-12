"""
Interactive REPL for Custom RDBMS
Provides command-line interface for direct database interaction
"""
import sys
import os
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from storage_engine import StorageEngine
from query_executor import QueryExecutor

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    print("Warning: tabulate not installed. Install with: pip install tabulate")

class RDBMSREPL:
    def __init__(self, data_dir: str = "data"):
        self.storage = StorageEngine(data_dir)
        self.executor = QueryExecutor(self.storage)
        self.running = True
        
        print("🗄️  Custom RDBMS Interactive Shell")
        print("Type 'help' for commands, 'exit' to quit")
        print("-" * 50)
    
    def run(self):
        """Main REPL loop"""
        while self.running:
            try:
                query = input("sql> ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ('exit', 'quit', 'q'):
                    self.running = False
                    print("Goodbye! 👋")
                    break
                
                if query.lower() == 'help':
                    self.show_help()
                    continue
                
                if query.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                # Execute query
                result = self.executor.execute(query)
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def display_result(self, result: Dict[str, Any]):
        """Display query result in a formatted way"""
        if not result.get('success', False):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        query_type = result.get('type', 'unknown')
        
        if 'rows' in result:
            # SELECT query results
            rows = result['rows']
            count = result.get('count', len(rows))
            
            if not rows:
                print("📭 No rows returned")
                return
            
            if HAS_TABULATE:
                # Use tabulate for nice formatting
                headers = list(rows[0].keys()) if rows else []
                table_data = []
                
                for row in rows:
                    table_data.append([row.get(col, '') for col in headers])
                
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                # Simple formatting without tabulate
                if rows:
                    headers = list(rows[0].keys())
                    
                    # Print headers
                    print(" | ".join(f"{h:15}" for h in headers))
                    print("-" * (len(headers) * 18))
                    
                    # Print rows
                    for row in rows:
                        values = [str(row.get(col, ''))[:15] for col in headers]
                        print(" | ".join(f"{v:15}" for v in values))
            
            print(f"\n📊 {count} row(s) returned")
        
        elif 'tables' in result:
            # SHOW TABLES result
            tables = result['tables']
            if not tables:
                print("📭 No tables found")
            else:
                print("📋 Tables:")
                for table in tables:
                    print(f"  • {table}")
                print(f"\n📊 {len(tables)} table(s)")
        
        elif 'columns' in result:
            # DESCRIBE result
            table_name = result.get('table', 'unknown')
            columns = result['columns']
            row_count = result.get('row_count', 0)
            
            print(f"📋 Table: {table_name}")
            print(f"📊 Rows: {row_count}")
            print()
            
            if HAS_TABULATE:
                headers = ['Column', 'Type', 'Constraints']
                table_data = []
                
                for col in columns:
                    table_data.append([
                        col['column'],
                        col['type'],
                        col.get('constraints', '') or ''
                    ])
                
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                print("Column           | Type             | Constraints")
                print("-" * 55)
                for col in columns:
                    constraints = col.get('constraints', '') or ''
                    print(f"{col['column']:15} | {col['type']:15} | {constraints}")
        
        else:
            # Other results (CREATE, INSERT, UPDATE, DELETE)
            message = result.get('message', 'Operation completed')
            print(f"✅ {message}")
            
            # Show additional info if available
            if 'row_id' in result:
                print(f"   Row ID: {result['row_id']}")
            if 'updated_count' in result:
                print(f"   Updated: {result['updated_count']} row(s)")
            if 'deleted_count' in result:
                print(f"   Deleted: {result['deleted_count']} row(s)")
    
    def show_help(self):
        """Display help information"""
        help_text = """
🗄️  Custom RDBMS Help

📋 Supported SQL Commands:

CREATE TABLE:
  CREATE TABLE table_name (
    column1 TYPE [PRIMARY KEY] [UNIQUE] [NOT NULL],
    column2 TYPE [constraints]
  );

INSERT:
  INSERT INTO table_name VALUES (value1, value2, ...);
  INSERT INTO table_name (col1, col2) VALUES (val1, val2);

SELECT:
  SELECT * FROM table_name;
  SELECT col1, col2 FROM table_name WHERE condition;
  SELECT * FROM table1 JOIN table2 ON table1.col = table2.col;

UPDATE:
  UPDATE table_name SET col1 = value1 WHERE condition;

DELETE:
  DELETE FROM table_name WHERE condition;

SHOW/DESCRIBE:
  SHOW TABLES;
  DESCRIBE table_name;

📊 Data Types:
  INT, VARCHAR(n), FLOAT, BOOLEAN, DATETIME

🔧 Constraints:
  PRIMARY KEY, UNIQUE, NOT NULL

💡 Examples:
  CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));
  INSERT INTO users VALUES (1, 'Alice');
  SELECT * FROM users WHERE id = 1;

🎮 REPL Commands:
  help  - Show this help
  clear - Clear screen
  exit  - Quit REPL
"""
        print(help_text)

def main():
    """Main entry point"""
    data_dir = "data"
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    repl = RDBMSREPL(data_dir)
    repl.run()

if __name__ == "__main__":
    main()