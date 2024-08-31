# import sys
# from dataclasses import dataclass
# # import sqlparse - available if you need it!
# from .record_parser import parse_record
# from .varint_parser import parse_varint
# database_file_path = sys.argv[1]
# command = sys.argv[2]
# @dataclass(init=False)
# class PageHeader:
#     page_type: int
#     first_free_block_start: int
#     number_of_cells: int
#     start_of_content_area: int
#     fragmented_free_bytes: int
#     @classmethod
#     def parse_from(cls, database_file):
#         """
#         Parses a page header as mentioned here: https://www.sqlite.org/fileformat2.html#b_tree_pages
#         """
#         instance = cls()
#         instance.page_type = int.from_bytes(database_file.read(1), "big")
#         instance.first_free_block_start = int.from_bytes(database_file.read(2), "big")
#         instance.number_of_cells = int.from_bytes(database_file.read(2), "big")
#         instance.start_of_content_area = int.from_bytes(database_file.read(2), "big")
#         instance.fragmented_free_bytes = int.from_bytes(database_file.read(1), "big")
#         return instance
# def getMeta():
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(100)  # Skip the header section
#         page_header = PageHeader.parse_from(database_file)
#         database_file.seek(
#             100 + 8
#         )  # Skip the database header & b-tree page header, get to the cell pointer array
#         cell_pointers = [
#             int.from_bytes(database_file.read(2), "big")
#             for _ in range(page_header.number_of_cells)
#         ]
#         sqlite_schema_rows = []
#         # Each of these cells represents a row in the sqlite_schema table.
#         for cell_pointer in cell_pointers:
#             database_file.seek(cell_pointer)
#             _number_of_bytes_in_payload = parse_varint(database_file)
#             rowid = parse_varint(database_file)
#             record = parse_record(database_file, 5)
#             # Table contains columns: type, name, tbl_name, rootpage, sql
#             sqlite_schema_rows.append(
#                 {
#                     "type": record[0],
#                     "name": record[1],
#                     "tbl_name": record[2],
#                     "rootpage": record[3],
#                     "sql": record[4],
#                 }
#             )
#     return sqlite_schema_rows
#     # print(f"number of tables: {len(sqlite_schema_rows)}")
# if command == ".dbinfo":
#     print(f"number of tables: {len(getMeta())}")
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(16)
#         page_size: int = int.from_bytes(database_file.read(2), byteorder="big")
#         print(f"database page size: {page_size}")
# elif command == ".tables":
#     print(" ".join([n["name"].decode("utf-8") for n in getMeta()]))
# else:
#     print(f"Invalid command: {command}")

# import sys
# from dataclasses import dataclass
# # import sqlparse - available if you need it!
# database_file_path = sys.argv[1]
# command = sys.argv[2]
# def read_int(file, size):
#     return int.from_bytes(file.read(size), byteorder="big")
# def read_varint(file):
#     val = 0
#     USE_NEXT_BYTE = 0x80
#     BITS_TO_USE = 0x7F
#     for _ in range(9):
#         byte = read_int(file, 1)
#         val = (val << 7) | (byte & BITS_TO_USE)
#         if byte & USE_NEXT_BYTE == 0:
#             break
#     return val
# def parse_record_body(srl_type, file):
#     if srl_type == 0:
#         return None
#     elif srl_type == 1:
#         return read_int(file, 1)
#     elif srl_type == 2:
#         return read_int(file, 2)
#     elif srl_type == 3:
#         return read_int(file, 3)
#     elif srl_type == 4:
#         return read_int(file, 4)
#     elif srl_type == 5:
#         return read_int(file, 6)
#     elif srl_type == 6:
#         return read_int(file, 8)
#     elif srl_type >= 12 and srl_type % 2 == 0:
#         datalen = (srl_type - 12) // 2
#         return file.read(datalen).decode()
#     elif srl_type >= 13 and srl_type % 2 == 1:
#         datalen = (srl_type - 13) // 2
#         #print("TEXT LEN:", datalen)
#         return file.read(datalen).decode()
#     else:
#         print("INVALID SERIAL TYPE")
#         return None
# def parse_cell(c_ptr, file):
#     database_file.seek(c_ptr)
#     payload_size = read_varint(file)
#     row_id = read_varint(file)
#     format_hdr_start = file.tell()
#     format_hdr_sz = read_varint(file)
#     serial_types = []
#     format_body_start = format_hdr_start + format_hdr_sz
#     while file.tell() < format_body_start:
#         serial_types.append(read_varint(file))
#     #record = []
#     records = []
#     for srl_type in serial_types:
#     #     record.append(parse_record_body(srl_type, file))
#     # return record
#         records.append(parse_record_body(srl_type, file))
#     return records
# if command == ".dbinfo":
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(16)  # Skip the first 16 bytes of the header
#         page_size = int.from_bytes(database_file.read(2), byteorder="big")
#         database_file.seek(103)
#         table_amt = int.from_bytes(database_file.read(2), byteorder="big")
#         print(f"database page size: {page_size}\nnumber of tables: {table_amt}")
# elif command == ".tables":
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(103)
#         cell_amt = read_int(database_file, 2)
#         database_file.seek(108)
#         cell_ptrs = [read_int(database_file, 2) for _ in range(cell_amt)]
#         records = [parse_cell(cell_ptr, database_file) for cell_ptr in cell_ptrs]
#         tbl_names = [rcd[2] for rcd in records if rcd[2] != "sqlite_sequence"]
#         print(*tbl_names)
# elif command.lower().startswith("select"):
#     query = command.lower().split()
#     tbl_name = query[-1]
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(16)
#         page_size = int.from_bytes(database_file.read(2), byteorder="big")
#         database_file.seek(103)
#         cell_amt = read_int(database_file, 2)
#         database_file.seek(108)
#         cell_ptrs = [read_int(database_file, 2) for _ in range(cell_amt)]
#         records = [parse_cell(cell_ptr, database_file) for cell_ptr in cell_ptrs]
#         tbls_info = {rcd[2]: rcd[3] for rcd in records if rcd[2] != "sqlite_sequence"}
#         tbl_rtpage = tbls_info[tbl_name]
#         database_file.seek(((tbl_rtpage - 1) * page_size) + 3)
#         table_cell_amt = read_int(database_file, 2)
#         print(table_cell_amt)
# else:
#     print(f"Invalid command: {command}")


# import sys
# from dataclasses import dataclass
# # import sqlparse - available if you need it!
# from .record_parser import parse_record
# from .varint_parser import parse_varint
# def readInt(df, n):
#     return int.from_bytes(df.read(n), "big")
# @dataclass(init=False)
# class PageHeader:
#     page_type: int
#     first_free_block_start: int
#     number_of_cells: int
#     start_of_content_area: int
#     fragmented_free_bytes: int
#     @classmethod
#     def parse_from(cls, database_file):
#         """
#         Parses a page header as mentioned here: https://www.sqlite.org/fileformat2.html#b_tree_pages
#         """
#         instance = cls()
#         instance.page_type = int.from_bytes(database_file.read(1), "big")
#         instance.first_free_block_start = int.from_bytes(database_file.read(2), "big")
#         instance.number_of_cells = int.from_bytes(database_file.read(2), "big")
#         instance.start_of_content_area = int.from_bytes(database_file.read(2), "big")
#         instance.fragmented_free_bytes = int.from_bytes(database_file.read(1), "big")
#         return instance
# database_file_path = sys.argv[1]
# command = sys.argv[2]
# def extractCellPointers(databaseFile):
#     pageHeader = PageHeader.parse_from(databaseFile)
#     return [
#         int.from_bytes(databaseFile.read(2), "big")
#         for _ in range(pageHeader.number_of_cells)
#     ]
# def goToPage(rootpage, offset=0):
#     pageRef = (rootpage - 1) * pageSize
#     return databaseFile.seek(pageRef + offset)
# def getPageContent(rootpage, numberOfFields, offset=0):
#     goToPage(rootpage, offset)
#     cellPointers = extractCellPointers(databaseFile)
#     values = []
#     for cellPointer in cellPointers:
#         goToPage(rootpage, cellPointer)
#         parse_varint(databaseFile)
#         parse_varint(databaseFile)
#         record = parse_record(databaseFile, numberOfFields)
#         values.append(record)
#     return values
# def initDb():
#     return open(database_file_path, "rb")
# def getInitInfo(databaseFile):
#     databaseFile.seek(16)
#     pageSize = readInt(databaseFile, 2)
#     databaseFile.seek(100)
#     return pageSize
# def getDbInfo():
#     info = getPageContent(1, 5, 100)
#     return [
#         {
#             "type": record[0].decode("utf8"),
#             "name": record[1].decode("utf8"),
#             "tbl_name": record[2].decode("utf8"),
#             "rootpage": record[3],
#             "sql": record[4].decode("utf8"),
#         }
#         for record in info
#     ]
# databaseFile = initDb()
# pageSize = getInitInfo(databaseFile)
# sqliteSchemaRows = getDbInfo()
# def parseSelect(sql):
#     select, rest = sql[7:].split(" from ")
#     table, where = rest.split(" where ") if rest else None, None
#     fields = [x.strip() for x in select.split(",")]
#     filter_ = [x.strip().replace("'", "") for x in where.split("=")] if where else None
#     # .reduce((accum, item, idx, arr) => idx % 2 === 1 ? accum : ({ ...accum, [item]: arr[idx + 1] }), {})
#     filter_ = (
#         {filter_[i]: filter_[i + 1] for i in range(0, len(filter_), 2)}
#         if where
#         else None
#     )
#     return fields, table[0], filter_
# def parseCreateTable(sql, table):
#     qry = list(
#         map(lambda x: x.strip(), sql[13 + len(table) :].replace("\n", " ").split(","))
#     )
#     qry = list(map(lambda x: x[1:] if x.startswith("(") else x, qry))
#     #qry = list(map(lambda x: x[0 : len(x) - 2] if x.endsWith(")") else x))
#     qry = list(map(lambda x: x[0 : len(x) - 2] if x.endswith(")") else x, qry))
#     fields = list(map(lambda x: x.split(" ")[0].strip(), qry))
#     return fields
# def countTableRows(table):
#     f = list(filter(lambda x: x["name"] == table, sqliteSchemaRows))
#     rootpage = f[0]["rootpage"]
#     goToPage(rootpage)
#     cellPointers = extractCellPointers(databaseFile)
#     return len(cellPointers)
# def getValues(tableFields, selectFields, whereFilter, values):
#     # asignateName = row => selectFields
#     #   .reduce((accum, field) => ({ ...accum, [field]: row[tableFields.indexOf(field)] }), {})
#     # filterWhereClauses = row =>
#     #   Object.entries(whereFilter ?? {}).reduce((accum, [key, value]) => accum && row[key] === value, true)
#     def asignateName(row):
#         return {
#             field: row[tableFields.index(field)].decode("utf-8")
#             for field in selectFields
#         }
#     #rows = values.map(asignateName)
#     #filteredRows = rows.filter(filterWhereClauses)
#     def filterWhereClauses(row):
#         if not whereFilter:
#             return True
#         for k, v in whereFilter:
#             if row[k] != v:
#                 return False
#         return True
#     rows = list(map(asignateName, values))
#     filteredRows = list(filter(filterWhereClauses, rows))
#     return filteredRows
# if command == ".dbinfo":
#     with open(database_file_path, "rb") as database_file:
#          database_file.seek(16)  # Skip the first 16 bytes of the header
#          page_size = int.from_bytes(database_file.read(2), byteorder="big")
#          database_file.seek(103)
#          table_amt = int.from_bytes(database_file.read(2), byteorder="big")
#          print(f"database page size: {page_size}\nnumber of tables: {table_amt}")
# elif command == ".tables":
#     print(" ".join([table["name"] for table in sqliteSchemaRows]))
# elif command.upper().startswith("SELECT COUNT("):
#     _, tableName, _ = parseSelect(command)
#     rowCounter = countTableRows(tableName)
#     print(rowCounter)
# elif command.upper().startswith("SELECT "):
#     qryFields, table, filter_ = parseSelect(command)
#     info = list(filter(lambda x: x["name"] == table, sqliteSchemaRows))[0]
#     rootpage = info["rootpage"]
#     sql = info["sql"]
#     tableFields = parseCreateTable(sql, table)
#     values = getPageContent(rootpage, len(tableFields))
#     result = getValues(tableFields, qryFields, filter_, values)
#     def printResult(row):
#         return "|".join(list(row.values()))
#     print("\n".join(list(map(printResult, result))))

import re
import sys
from dataclasses import dataclass
# import sqlparse - available if you need it!
database_file_path = sys.argv[1]
command = sys.argv[2]
IS_FIRST_BIT_ZERO_MASKED = 0x80  # 0b10000000
LAST_SEVEN_BITS_MASK = 0x7F  # 0b01111111
def starts_with_zero(byte):
    return (byte & IS_FIRST_BIT_ZERO_MASKED) == 0
def usable_value(usable_size, byte):
    return byte if usable_size == 8 else byte & LAST_SEVEN_BITS_MASK
def read_usable_bytes(stream):
    usable_bytes = []
    for i in range(8):
        byte = int.from_bytes(stream.read(1), byteorder="big")
        usable_bytes.append(byte)
        if starts_with_zero(byte):
            break
    return usable_bytes
# def read_varint(stream):
#     usable_bytes = read_usable_bytes(stream)
#     value = 0
#     for index, usable_byte in enumerate(usable_bytes):
#         usable_size = 8 if index == 8 else 7
#         shifted = value << usable_size
#         value = shifted + usable_value(usable_size, usable_byte)
#     return value
def read_varint(stream):
    IS_FIRST_BIT_ZERO_MASKED = 0x80  # 0b10000000
    LAST_SEVEN_BITS_MASK = 0x7F  # 0b01111111
    value = 0
    for _ in range(9):
        byte = int.from_bytes(stream.read(1), byteorder="big")
        value = value << 7 | (byte & LAST_SEVEN_BITS_MASK)
        if byte & IS_FIRST_BIT_ZERO_MASKED == 0:
            break
    return value
def parse_column(stream, serial_type):
    if serial_type >= 13 and serial_type % 2 == 1:
        n_bytes = (serial_type - 13) // 2
        return stream.read(n_bytes).decode()
    if serial_type >= 12 and serial_type % 2 == 0:
        n_bytes = (serial_type - 12) // 2
        return stream.read(n_bytes).decode()
    if serial_type == 1:
        return int.from_bytes(stream.read(1), byteorder="big")
    if serial_type == 0:
        return None
    if serial_type == 7 or serial_type == 6:
        return int.from_bytes(stream.read(8), byteorder="big")
    raise Exception(f"Unknown Serial Type {serial_type}")
def parse_record(stream, column_count):
    serial_types = [read_varint(stream) for i in range(column_count)]
    return [parse_column(stream, serial_type) for serial_type in serial_types]
def table_schema(database_file):
    database_file.seek(100)
    # print(database_file.tell())
    page_type = int.from_bytes(database_file.read(1), byteorder="big")
    free_block = int.from_bytes(database_file.read(2), byteorder="big")
    cell_count = int.from_bytes(database_file.read(2), byteorder="big")
    content_start = int.from_bytes(database_file.read(2), byteorder="big")
    fragmented_free_bytes = int.from_bytes(database_file.read(1), byteorder="big")
    cell_pointers = [
        int.from_bytes(database_file.read(2), byteorder="big")
        for _ in range(cell_count)
    ]
    # print(content_start, cell_pointers)
    # print(cell_pointers)
    tables = []
    for cell_pointer in cell_pointers:
        database_file.seek(cell_pointer)
        payload_size = read_varint(database_file)
        row_id = read_varint(database_file)
        _bytes_in_header = read_varint(database_file)
        cols = parse_record(database_file, 5)
        sqlite_schema = {
            "type": cols[0],
            "name": cols[1],
            "tbl_name": cols[2],
            "rootpage": cols[3],
            "sql": cols[4],
        }
        tables.append(sqlite_schema)
    return tables
if command == ".dbinfo":
    with open(database_file_path, "rb") as database_file:
        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
        # Uncomment this to pass the first stage
        database_file.seek(16)  # Skip the first 16 bytes of the header
        page_size = int.from_bytes(database_file.read(2), byteorder="big")
        database_file.seek(103)
        cell_count = int.from_bytes(database_file.read(2), byteorder="big")
        print(f"database page size: {page_size}")
        print(f"number of tables: {cell_count}")
elif command == ".tables":
    with open(database_file_path, "rb") as database_file:
        tables = table_schema(database_file)
        print(" ".join([x["name"] for x in tables if x["name"] != "sqlite_sequence"]))
elif "select" in command.lower():
    has_count = "count(" in command.lower()
    select_cols = command.lower().split("from")[0].replace("select ", "").split(",")
    select_cols = [col.strip() for col in select_cols if len(col.strip()) > 0]
    #table_name = command.lower().split(" ")[-1].replace("\\n", "")
    table_name = (
        command.lower().split("from")[1].strip().split(" ")[0].replace("\\n", "")
    )
    with open(database_file_path, "rb") as database_file:
        database_file.seek(16)
        page_size = int.from_bytes(database_file.read(2), byteorder="big")
        tables = table_schema(database_file)
        table_info = [table for table in tables if table["name"] == table_name][0]
        schema_cols = (
            table_info["sql"]
            .replace("\n", "")
            .replace("\t", "")
            .split("(")[1]
            .split(")")[0]
            .split(",")
        )
        #schema_cols = [col.split(" ")[0].strip() for col in schema_cols]
        schema_cols = [col.strip().split(" ")[0].strip() for col in schema_cols]
        if table_info is None:
            print("Table Not Found")
        table_cell_offset = (table_info["rootpage"] - 1) * page_size
        database_file.seek(table_cell_offset)
        page_type = int.from_bytes(database_file.read(1), byteorder="big")
        free_block = int.from_bytes(database_file.read(2), byteorder="big")
        cell_count = int.from_bytes(database_file.read(2), byteorder="big")
        content_start = int.from_bytes(database_file.read(2), byteorder="big")
        fragmented_free_bytes = int.from_bytes(database_file.read(1), byteorder="big")
        # right_most_pointer = int.from_bytes(database_file.read(4), byteorder="big")
        if has_count:
            print(cell_count)
            exit()
        # print(table_info['sql'])
        # print(schema_cols)
        cell_pointers = [
            table_cell_offset + int.from_bytes(database_file.read(2), byteorder="big")
            for _ in range(cell_count)
        ]
        # print(content_start, cell_pointers)
        if "where" in command.lower():
            ccolumn, cvalue = [
                col.strip() for col in command.split("where")[1].split("=")
            ]
        rows = []
        for cell_pointer in cell_pointers:
            database_file.seek(cell_pointer)
            payload_size = read_varint(database_file)
            row_id = read_varint(database_file)
            _bytes_in_header = read_varint(database_file)
            cols = parse_record(database_file, len(schema_cols))
            output = []
            show_row = not "where" in command.lower()
            for select_col in select_cols:
                try:
                    col_index = schema_cols.index(select_col)
                    # print(cols[col_index])
                    #output.append(cols[col_index])
                    value = cols[col_index]
                    # print(value, cvalue)
                    if "where" in command.lower():
                        # print(ccolumn, select_col, value, cvalue)
                        if ccolumn == select_col and value == cvalue.replace("'", ""):
                            show_row = True
                    output.append(value)
                except:
                    print(f"Error: in prepare, no such column: {select_col}")
                    exit()
            #print("|".join(output))
            if show_row:
                print("|".join(output))
else:
    print(f"Invalid command: {command}")