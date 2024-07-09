import pyodbc

server = 'DESKTOP-EQQ552C\\MSSQLSERVER01'
database = 'BOSA'
username = 'your_username'
password = 'your_password'

connection_string_online = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)

class DatabaseManager:
    @staticmethod
    def connect():
        """Establishes a connection to the MySQL database."""
        try:
            connection = pyodbc.connect(connection_string)
            if connection:
                return connection
        except Exception as e:
            print(f"Error while connecting to MySQL: {str(e)}")
            return None
        return None
    @staticmethod
    def insert(stmt):
        """Inserts a new record into the users table."""
        conn = DatabaseManager.connect()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(stmt)
            conn.commit()
            print(f"Inserted row ID: ")
            return True
        except Exception as e:
            print(f"Error inserting record: {str(e)}")
            
        finally:
            cursor.close()
            conn.close()
        return False  
    @staticmethod
    def update(stmt):
        """Updates an existing record in the users table."""
        
        conn = DatabaseManager.connect()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(stmt)
            conn.commit()
            
            print(f"Updated rows: {cursor.rowcount}")
            return True
        except Exception as e:
            print(f"Error updating record: {str(e)}")
            
        finally:
            cursor.close()
            conn.close()
        return None 
    @staticmethod
    async def query(stmt):
        conn = DatabaseManager.connect()
        if conn is None:
            return
        result = None
        try:
            cursor = conn.cursor()
            cursor.execute(stmt)
            result = cursor.fetchall()
            
        except Exception as e:
            print(f"Error finding record: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()
            return result
    @staticmethod
    def find(user_id):
        """Finds a record in the users table by ID."""
        conn = DatabaseManager.connect()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM MEMBERS WHERE id = %s
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                print(f"Found user: ID={result[0]}, Name={result[1]}, Age={result[2]}")
            else:
                print("User not found.")
        except Exception as e:
            print(f"Error finding record: {str(e)}")
        finally:
            cursor.close()
            conn.close()
