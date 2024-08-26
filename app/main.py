import sys
from dataclasses import dataclass

database_file_path = sys.argv[1]
command = sys.argv[2]

@dataclass(init=False)
class PageHeader:
    page_type: int
    first_free_block_start: int
    number_of_cells: int
    start_of_content_area: int
    fragmented_free_bytes: int

    @classmethod
    def parse_from(cls, database_file):
        instance = cls()
        instance.page_type = int.from_bytes(database_file.read(1), "big")
        instance.first_free_block_start = int.from_bytes(database_file.read(2), "big")
        instance.number_of_cells = int.from_bytes(database_file.read(2), "big")
        instance.start_of_content_area = int.from_bytes(database_file.read(2), "big")
        instance.fragmented_free_bytes = int.from_bytes(database_file.read(1), "big")
        return instance

def parse_varint(file):
    """Parse a variable-length integer (varint) from the file."""
    value = 0
    while True:
        byte = file.read(1)
        if not byte:
            raise ValueError("Unexpected end of file while reading varint.")
        byte_value = ord(byte)
        value = (value << 7) | (byte_value & 0x7F)
        if byte_value & 0x80 == 0:
            break
    return value

def parse_record(file, num_columns):
    """Parse a record with the given number of columns."""
    _payload_length = parse_varint(file)

    record = []
    for _ in range(num_columns):
        column_length = parse_varint(file)
        column_value = file.read(column_length)
        try:
            decoded_value = column_value.decode("utf-8", errors="ignore").strip()
        except UnicodeDecodeError:
            decoded_value = None
        record.append(decoded_value)
    return record

def extract_table_names(database_file, page_header):
    """Extract table names from the SQLite database file."""
    database_file.seek(100 + 8)  # Skip the database header & b-tree page header, get to the cell pointer array
    
    cell_pointers = [
        int.from_bytes(database_file.read(2), "big")
        for _ in range(page_header.number_of_cells)
    ]
    sqlite_schema_rows = []
    
    for cell_pointer in cell_pointers:
        database_file.seek(cell_pointer)
        _number_of_bytes_in_payload = parse_varint(database_file)
        rowid = parse_varint(database_file)
        record = parse_record(database_file, 5)
        
        # Ensure all columns are valid text strings
        if len(record) == 5:
            sqlite_schema_rows.append(
                {
                    "type": record[0],
                    "name": record[1],
                    "tbl_name": record[2],
                    "rootpage": record[3],
                    "sql": record[4],
                }
            )
    
    return sqlite_schema_rows

if command == ".dbinfo" or command == ".tables":
    with open(database_file_path, "rb") as database_file:
        database_file.seek(100)  # Skip the header section
        page_header = PageHeader.parse_from(database_file)
        
        sqlite_schema_rows = extract_table_names(database_file, page_header)
        
        if command == ".dbinfo":
            print(f"number of tables: {len(sqlite_schema_rows)}")
        elif command == ".tables":
            table_names = [table["tbl_name"].decode("utf-8", errors="ignore") for table in sqlite_schema_rows if table["tbl_name"]]
            print(" ".join(table_names))
else:
    print(f"Invalid command: {command}")
