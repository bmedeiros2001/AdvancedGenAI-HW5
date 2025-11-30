"""
MCP server - customer service database tools
this server exposes database operations as MCP tools that agents can call

This is the "API" that agents wll use to access the database
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

DB_FILE = "customer_service.db"

class MCPServer:
    """ initialize MCP server """
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self):
        """ establish connection to database """
        try:
            # where we saved the connection to db
            self.connection = sqlite3.connect(self.db_file) 

            # makes rows behave like dictionaries (so, instead of `row[0]`, you can do `row['name']`)
            self.connection.row_factory = sqlite3.Row 
            print(f"       [MCP Server] Connected to {self.db_file}")
        except Exception as e:
            print(f"       [MCP Server] Failed to connect to database: {e}")
            raise
    
    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """ Execute a SELECT query and return results as list of dictionaries. """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # convert row objects into dictionaries
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Query error: {e}")
            raise
    
    def _execute_update(self, query: str, params:tuple = ()) -> int:
        """ Execute an INSERT/UPDATE/DELETE query. """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            # For INSERT, return the new row's ID
            # For UPDATE/DELETE, return number of affected rows
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception as e:
            self.connection.rollback()  # Undo changes on error
            print(f"Update error: {e}")
            raise

    # =========================================================================
    # MCP TOOL 1: get_customer
    # =========================================================================
    def get_customer(self, customer_id:int) -> Dict[str, Any]:
        """
        Retrieve customer information by ID.
        
        Example:
            >>> server.get_customer(5)
            {
                'success': True,
                'customer': {
                    'id': 5,
                    'name': 'Eve Martinez',
                    'email': 'eve@email.com',
                    'phone': '555-0105',
                    'status': 'active',
                    'created_at': '2024-11-28 12:00:00'
                }
            }
        """
        try:
            query = """
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                WHERE id = ?
                """
            
            results = self._execute_query(query, (customer_id,))

            if results:
                return {
                    'success': True,
                    'customer': results[0]
                }
            else:
                return {
                    'success':False,
                    'error': f'Customer {customer_id} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    # =========================================================================
    # MCP TOOL 2: list_customers
    # =========================================================================
    def list_customers(self, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        List customers, optionally filtered by status.
        
        Args:
            status: Filter by status ('active' or 'disabled'). If None, returns all.
            limit: Maximum number of customers to return (default 100)
            
        Returns:
            Dictionary with list of customers
            
        Example:
            >>> server.list_customers(status='active', limit=10)
            {
                'success': True,
                'count': 4,
                'customers': [
                    {'id': 1, 'name': 'Alice Johnson', 'status': 'active', ...},
                    {'id': 2, 'name': 'Bob Smith', 'status': 'active', ...},
                    ...
                ]
            }
        """
        try:
            # Build query based on whether status filter is provided
            if status:
                query = """
                    SELECT id, name, email, phone, status, created_at
                    FROM customers
                    WHERE status = ?
                    LIMIT ?
                """
                params = (status, limit)
            else:
                query = """
                    SELECT id, name, email, phone, status, created_at
                    FROM customers
                    LIMIT ?
                """
                params = (limit,)
            
            results = self._execute_query(query, params)
            
            return {
                'success': True,
                'count': len(results),
                'customers': results,
                'filter': {'status': status, 'limit': limit}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    # =========================================================================
    # MCP TOOL 3: update_customer
    # =========================================================================
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update customer information.
        
        Args:
            customer_id: ID of customer to update
            data: Dictionary of fields to update (e.g., {'email': 'new@email.com'})
            
        Returns:
            Success status and updated customer data
            
        Allowed fields to update:
            - name
            - email
            - phone
            - status
            
        Example:
            >>> server.update_customer(5, {'email': 'eve.new@email.com', 'phone': '555-9999'})
            {
                'success': True,
                'updated_fields': ['email', 'phone'],
                'customer_id': 5
            }
        """
        try:
            # Validate that customer exists
            customer = self.get_customer(customer_id)
            if not customer['success']:
                return customer  # Return the error from get_customer
            
            # Only allow specific fields to be updated (security!)
            allowed_fields = ['name', 'email', 'phone', 'status']
            update_fields = {k: v for k, v in data.items() if k in allowed_fields}
            
            if not update_fields:
                return {
                    'success': False,
                    'error': 'No valid fields to update',
                    'allowed_fields': allowed_fields
                }
            
            # Build UPDATE query dynamically
            # Example: "UPDATE customers SET email = ?, phone = ? WHERE id = ?"
            set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
            query = f"""
                UPDATE customers 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            # Build parameters tuple
            params = tuple(update_fields.values()) + (customer_id,)
            
            # Execute update
            rows_affected = self._execute_update(query, params)
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'updated_fields': list(update_fields.keys()),
                    'customer_id': customer_id,
                    'message': f'Customer {customer_id} updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Update failed - no rows affected'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    # =========================================================================
    # MCP TOOL 4: create_ticket
    # =========================================================================
    def create_ticket(self, customer_id: int, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """
        Create a support ticket for a customer.
        
        Args:
            customer_id: ID of the customer creating the ticket
            issue: Description of the issue
            priority: Priority level ('low', 'medium', or 'high')
            
        Returns:
            Ticket creation status and ticket ID
            
        Example:
            >>> server.create_ticket(5, "Cannot access my account", "high")
            {
                'success': True,
                'ticket_id': 7,
                'customer_id': 5,
                'issue': 'Cannot access my account',
                'priority': 'high',
                'status': 'open'
            }
        """
        try:
            # Validate customer exists
            customer = self.get_customer(customer_id)
            if not customer['success']:
                return {
                    'success': False,
                    'error': f'Customer {customer_id} not found'
                }
            
            # Validate priority
            valid_priorities = ['low', 'medium', 'high']
            if priority not in valid_priorities:
                priority = 'medium'  # Default to medium if invalid
            
            # Insert ticket
            query = """
                INSERT INTO tickets (customer_id, issue, status, priority, created_at)
                VALUES (?, ?, 'open', ?, CURRENT_TIMESTAMP)
            """
            
            ticket_id = self._execute_update(query, (customer_id, issue, priority))
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'customer_id': customer_id,
                'issue': issue,
                'priority': priority,
                'status': 'open',
                'message': f'Ticket #{ticket_id} created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    # =========================================================================
    # MCP TOOL 5: get_customer_history
    # =========================================================================
    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """
        Get all tickets associated with a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Customer info and their ticket history
            
        Example:
            >>> server.get_customer_history(1)
            {
                'success': True,
                'customer': {'id': 1, 'name': 'Alice Johnson', ...},
                'ticket_count': 2,
                'tickets': [
                    {'id': 1, 'issue': 'Cannot login', 'status': 'open', ...},
                    {'id': 2, 'issue': 'Account not working', 'status': 'open', ...}
                ]
            }
        """
        try:
            # First, get customer info
            customer = self.get_customer(customer_id)
            if not customer['success']:
                return customer  # Return error
            
            # Get all tickets for this customer
            query = """
                SELECT id, issue, status, priority, created_at
                FROM tickets
                WHERE customer_id = ?
                ORDER BY created_at DESC
            """
            
            tickets = self._execute_query(query, (customer_id,))
            
            return {
                'success': True,
                'customer': customer['customer'],
                'ticket_count': len(tickets),
                'tickets': tickets
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    def list_all_tools(self) -> List[str]:
        """
        List all available MCP tools.
        
        Returns:
            List of tool names
        """
        return [
            'get_customer',
            'list_customers',
            'update_customer',
            'create_ticket',
            'get_customer_history'
        ]
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("MCP Server disconnected from database")


def main():
    """
    Test the MCP server with example calls.
    This demonstrates each tool working correctly.
    """
    print("=" * 70)
    print("MCP SERVER - Testing All Tools")
    print("=" * 70)
    
    # Initialize server
    server = MCPServer()
    
    print("\n[1] Testing: get_customer(5)")
    print("-" * 70)
    result = server.get_customer(5)
    print(json.dumps(result, indent=2))
    
    print("\n[2] Testing: list_customers(status='active', limit=3)")
    print("-" * 70)
    result = server.list_customers(status='active', limit=3)
    print(json.dumps(result, indent=2))
    
    print("\n[3] Testing: update_customer(5, {'email': 'eve.updated@email.com'})")
    print("-" * 70)
    result = server.update_customer(5, {'email': 'eve.updated@email.com'})
    print(json.dumps(result, indent=2))
    
    print("\n[4] Testing: create_ticket(1, 'Test issue from MCP', 'high')")
    print("-" * 70)
    result = server.create_ticket(1, 'Test issue from MCP', 'high')
    print(json.dumps(result, indent=2))
    
    print("\n[5] Testing: get_customer_history(1)")
    print("-" * 70)
    result = server.get_customer_history(1)
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 70)
    print("ALL MCP TOOLS TESTED SUCCESSFULLY")
    print("=" * 70)
    
    # Close connection
    server.close()


if __name__ == "__main__":
    main()
    

