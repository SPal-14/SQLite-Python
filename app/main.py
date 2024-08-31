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

# import re
# import sys
# from dataclasses import dataclass
# # import sqlparse - available if you need it!
# database_file_path = sys.argv[1]
# command = sys.argv[2]
# IS_FIRST_BIT_ZERO_MASKED = 0x80  # 0b10000000
# LAST_SEVEN_BITS_MASK = 0x7F  # 0b01111111
# def starts_with_zero(byte):
#     return (byte & IS_FIRST_BIT_ZERO_MASKED) == 0
# def usable_value(usable_size, byte):
#     return byte if usable_size == 8 else byte & LAST_SEVEN_BITS_MASK
# def read_usable_bytes(stream):
#     usable_bytes = []
#     for i in range(8):
#         byte = int.from_bytes(stream.read(1), byteorder="big")
#         usable_bytes.append(byte)
#         if starts_with_zero(byte):
#             break
#     return usable_bytes
# # def read_varint(stream):
# #     usable_bytes = read_usable_bytes(stream)
# #     value = 0
# #     for index, usable_byte in enumerate(usable_bytes):
# #         usable_size = 8 if index == 8 else 7
# #         shifted = value << usable_size
# #         value = shifted + usable_value(usable_size, usable_byte)
# #     return value
# def read_varint(stream):
#     IS_FIRST_BIT_ZERO_MASKED = 0x80  # 0b10000000
#     LAST_SEVEN_BITS_MASK = 0x7F  # 0b01111111
#     value = 0
#     for _ in range(9):
#         byte = int.from_bytes(stream.read(1), byteorder="big")
#         value = value << 7 | (byte & LAST_SEVEN_BITS_MASK)
#         if byte & IS_FIRST_BIT_ZERO_MASKED == 0:
#             break
#     return value
# def parse_column(stream, serial_type):
#     if serial_type >= 13 and serial_type % 2 == 1:
#         n_bytes = (serial_type - 13) // 2
#         return stream.read(n_bytes).decode()
#     if serial_type >= 12 and serial_type % 2 == 0:
#         n_bytes = (serial_type - 12) // 2
#         return stream.read(n_bytes).decode()
#     if serial_type == 1:
#         return int.from_bytes(stream.read(1), byteorder="big")
#     if serial_type == 0:
#         return None
#     if serial_type == 7 or serial_type == 6:
#         return int.from_bytes(stream.read(8), byteorder="big")
#     raise Exception(f"Unknown Serial Type {serial_type}")
# def parse_record(stream, column_count):
#     serial_types = [read_varint(stream) for i in range(column_count)]
#     return [parse_column(stream, serial_type) for serial_type in serial_types]
# def table_schema(database_file):
#     database_file.seek(100)
#     # print(database_file.tell())
#     page_type = int.from_bytes(database_file.read(1), byteorder="big")
#     free_block = int.from_bytes(database_file.read(2), byteorder="big")
#     cell_count = int.from_bytes(database_file.read(2), byteorder="big")
#     content_start = int.from_bytes(database_file.read(2), byteorder="big")
#     fragmented_free_bytes = int.from_bytes(database_file.read(1), byteorder="big")
#     cell_pointers = [
#         int.from_bytes(database_file.read(2), byteorder="big")
#         for _ in range(cell_count)
#     ]
#     # print(content_start, cell_pointers)
#     # print(cell_pointers)
#     tables = []
#     for cell_pointer in cell_pointers:
#         database_file.seek(cell_pointer)
#         payload_size = read_varint(database_file)
#         row_id = read_varint(database_file)
#         _bytes_in_header = read_varint(database_file)
#         cols = parse_record(database_file, 5)
#         sqlite_schema = {
#             "type": cols[0],
#             "name": cols[1],
#             "tbl_name": cols[2],
#             "rootpage": cols[3],
#             "sql": cols[4],
#         }
#         tables.append(sqlite_schema)
#     return tables
# if command == ".dbinfo":
#     with open(database_file_path, "rb") as database_file:
#         # You can use print statements as follows for debugging, they'll be visible when running tests.
#         print("Logs from your program will appear here!")
#         # Uncomment this to pass the first stage
#         database_file.seek(16)  # Skip the first 16 bytes of the header
#         page_size = int.from_bytes(database_file.read(2), byteorder="big")
#         database_file.seek(103)
#         cell_count = int.from_bytes(database_file.read(2), byteorder="big")
#         print(f"database page size: {page_size}")
#         print(f"number of tables: {cell_count}")
# elif command == ".tables":
#     with open(database_file_path, "rb") as database_file:
#         tables = table_schema(database_file)
#         print(" ".join([x["name"] for x in tables if x["name"] != "sqlite_sequence"]))
# elif "select" in command.lower():
#     has_count = "count(" in command.lower()
#     select_cols = command.lower().split("from")[0].replace("select ", "").split(",")
#     select_cols = [col.strip() for col in select_cols if len(col.strip()) > 0]
#     #table_name = command.lower().split(" ")[-1].replace("\\n", "")
#     table_name = (
#         command.lower().split("from")[1].strip().split(" ")[0].replace("\\n", "")
#     )
#     with open(database_file_path, "rb") as database_file:
#         database_file.seek(16)
#         page_size = int.from_bytes(database_file.read(2), byteorder="big")
#         tables = table_schema(database_file)
#         table_info = [table for table in tables if table["name"] == table_name][0]
#         schema_cols = (
#             table_info["sql"]
#             .replace("\n", "")
#             .replace("\t", "")
#             .split("(")[1]
#             .split(")")[0]
#             .split(",")
#         )
#         #schema_cols = [col.split(" ")[0].strip() for col in schema_cols]
#         schema_cols = [col.strip().split(" ")[0].strip() for col in schema_cols]
#         if table_info is None:
#             print("Table Not Found")
#         table_cell_offset = (table_info["rootpage"] - 1) * page_size
#         database_file.seek(table_cell_offset)
#         page_type = int.from_bytes(database_file.read(1), byteorder="big")
#         free_block = int.from_bytes(database_file.read(2), byteorder="big")
#         cell_count = int.from_bytes(database_file.read(2), byteorder="big")
#         content_start = int.from_bytes(database_file.read(2), byteorder="big")
#         fragmented_free_bytes = int.from_bytes(database_file.read(1), byteorder="big")
#         # right_most_pointer = int.from_bytes(database_file.read(4), byteorder="big")
#         if has_count:
#             print(cell_count)
#             exit()
#         # print(table_info['sql'])
#         # print(schema_cols)
#         cell_pointers = [
#             table_cell_offset + int.from_bytes(database_file.read(2), byteorder="big")
#             for _ in range(cell_count)
#         ]
#         # print(content_start, cell_pointers)
#         if "where" in command.lower():
#             ccolumn, cvalue = [
#                 col.strip() for col in command.split("where")[1].split("=")
#             ]
#         rows = []
#         for cell_pointer in cell_pointers:
#             database_file.seek(cell_pointer)
#             payload_size = read_varint(database_file)
#             row_id = read_varint(database_file)
#             _bytes_in_header = read_varint(database_file)
#             cols = parse_record(database_file, len(schema_cols))
#             output = []
#             show_row = not "where" in command.lower()
#             for select_col in select_cols:
#                 try:
#                     col_index = schema_cols.index(select_col)
#                     # print(cols[col_index])
#                     #output.append(cols[col_index])
#                     value = cols[col_index]
#                     # print(value, cvalue)
#                     if "where" in command.lower():
#                         # print(ccolumn, select_col, value, cvalue)
#                         if ccolumn == select_col and value == cvalue.replace("'", ""):
#                             show_row = True
#                     output.append(value)
#                 except:
#                     print(f"Error: in prepare, no such column: {select_col}")
#                     exit()
#             #print("|".join(output))
#             if show_row:
#                 print("|".join(output))
# else:
#     print(f"Invalid command: {command}")

# import sys
# from dataclasses import dataclass
# import sqlparse
# from .record_parser import parse_record
# from .varint_parser import parse_varint
# database_file_path = sys.argv[1]
# command = sys.argv[2]
# class SqliteFileParser:
#     def __init__(self, database_file_path):
#         self.database_file = open(database_file_path, "rb")
#         self.database_file.seek(16)
#         self.page_size = int.from_bytes(self.database_file.read(2), "big")
#         self.database_file.seek(28)
#         self.page_num = int.from_bytes(self.database_file.read(4), "big")
#         self.page_headers = self.read_pages()
#         self.sqlite_schema_rows = self.get_sqlite_schema_rows(
#             self.database_file, self.get_cell_pointers(self.page_headers[0])
#         )
#     def get_cell_pointers(self, page_header):
#         #self.database_file.seek(page_header.offset + 8)
#         additional_offset = 4 if page_header.page_type in (2, 5) else 0
#         self.database_file.seek(page_header.offset + 8 + additional_offset)
#         return [
#             int.from_bytes(self.database_file.read(2), "big")
#             for _ in range(page_header.number_of_cells)
#         ]
#     def read_pages(self):
#         all_pages = []
#         self.database_file.seek(100)
#         curr_offset = 100
#         for i in range(self.page_num):
#             all_pages.append(PageHeader.parse_from(self.database_file, curr_offset))
#             curr_offset = self.database_file.seek(self.page_size * (i + 1))
#         return all_pages
#     def get_sqlite_schema_rows(self, database_file, cell_pointers):
#         sqlite_schema_rows = {}
#         # Each of these cells represents a row in the sqlite_schema table.
#         for cell_pointer in cell_pointers:
#             database_file.seek(cell_pointer)
#             _number_of_bytes_in_payload = parse_varint(database_file)
#             rowid = parse_varint(database_file)
#             record = parse_record(database_file, 5)
#             # Table contains columns: type, name, tbl_name, rootpage, sql
#             sqlite_schema_rows[record[2].decode()] = {
#                 "type": record[0].decode(),
#                 "name": record[1].decode(),
#                 "tbl_name": record[2].decode(),
#                 "rootpage": record[3],
#                 "sql": record[4].decode(),
#             }
#         return sqlite_schema_rows
#     def get_row_count(self, table):
#         table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
#         table_page = self.page_headers[table_rootpage - 1]
#         """
#         self.database_file.seek(table_page.offset + 8)
#         cell_pointers = self.get_cell_pointers(table_page)
#         for pointer in cell_pointers:
#             self.database_file.seek(pointer + table_page.offset)
#             print(self.database_file.read(30))
#         """
#         print(table_page.number_of_cells)
#     def get_sql_info(self, sql_statement):
#         # separate out select, and where clause
#         # get: table, columns of interest, and table
#         columns = None
#         table = None
#         where = []
#         sql_tokens = sqlparse.parse(sql_statement)[0].tokens
#         for token in sql_tokens:
#             if isinstance(token, sqlparse.sql.IdentifierList) or isinstance(
#                 token, sqlparse.sql.Function
#             ):
#                 columns = str(token)
#             if isinstance(token, sqlparse.sql.Identifier):
#                 if columns is None:
#                     columns = str(token)
#                 else:
#                     table = str(token)
#             if isinstance(token, sqlparse.sql.Where):
#                 for where_token in token.tokens:
#                     if isinstance(where_token, sqlparse.sql.Comparison):
#                         #where = str(where_token)
#                         for comp_token in where_token.tokens:
#                             if str(comp_token) != " ":
#                                 where.append(str(comp_token))
#                             # if comp_token != sqlparse.sql.Whitespace:
#                             #    where.append(str(comp_token))
#         #return {"select": columns, "table": table, "where": where}
#         return {"select": columns, "table": table, "where": where if where else None}
#     def get_column_count(self, table):
#         create_sql = sqlparse.parse(self.sqlite_schema_rows[table]["sql"])
#         columns = create_sql[0][-1].tokens
#         total_columns = []
#         for token in columns:
#             if isinstance(token, sqlparse.sql.Identifier):
#                 total_columns.append(str(token))
#             if isinstance(token, sqlparse.sql.IdentifierList):
#                 for sub_token in token:
#                     if (
#                         isinstance(sub_token, sqlparse.sql.Identifier)
#                         and str(sub_token) != "autoincrement"
#                     ):
#                         total_columns.append(str(sub_token))
#         return total_columns
#     def get_records(self, table_page, columns):
#         cell_pointers = self.get_cell_pointers(table_page)
#         records = []
#         column_count = len(columns)
#         for pointer in cell_pointers:
#             self.database_file.seek(pointer + table_page.offset)
#             if table_page.page_type == 13:
#                 total_bytes = parse_varint(self.database_file)
#                 row_id = parse_varint(self.database_file)
#                 record = parse_record(self.database_file, column_count)
#                 record[0] = row_id
#                 record = [c.decode() if isinstance(c, bytes) else c for c in record]
#                 record = {columns[i]: record[i] for i in range(len(columns))}
#                 records.append(record)
#             elif table_page.page_type == 5:
#                 left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
#                 int_key = parse_varint(self.database_file)
#                 records += self.get_records(
#                     self.page_headers[left_child_pointer - 1], columns
#                 )
#             else:
#                 print("NEW PAGE TYPE: " + table_page.page_type)
#         return records
#     def execute_sql(self, sql_statement):
#         sql_info = self.get_sql_info(sql_statement)
#         table = sql_info["table"]
#         if sql_info["select"].upper() == "COUNT(*)":
#             self.get_row_count(table)
#             return
#         columns = self.get_column_count(table)
#         column_count = len(columns)
#         table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
#         table_page = self.page_headers[table_rootpage - 1]
#         self.database_file.seek(table_page.offset + 8)
#         # cell_pointers = self.get_cell_pointers(table_page)
#         # records = []
#         # for pointer in cell_pointers:
#         #     self.database_file.seek(pointer + table_page.offset)
#         #     # asssume this is a leaf file
#         #     total_bytes = parse_varint(self.database_file)
#         #     row_id = parse_varint(self.database_file)
#         #     record = parse_record(self.database_file, column_count)
#         #     record[0] = row_id
#         #     record = [c.decode() if isinstance(c, bytes) else c for c in record]
#         #     record = {columns[i]: record[i] for i in range(len(columns))}
#         #     records.append(record)
#         records = self.get_records(table_page, columns)
#         columns_of_interest = sql_info["select"].split(", ")
#         for i, record in enumerate(records):
#             total_row = []
#             if sql_info["where"] is None:
#                 for col in columns_of_interest:
#                     total_row.append(str(record[col]))
#             else:
#                 #comparison = sql_info["where"].split()
#                 comparison = sql_info["where"]
#                 comp_col = comparison[0]
#                 comp_val = comparison[2].replace("'", "")
#                 # assume this is an equality comparison
#                 if record[comp_col] == comp_val:
#                     for col in columns_of_interest:
#                         total_row.append(str(record[col]))
#             if len(total_row) > 0:
#                 print("|".join(total_row))
# @dataclass(init=False)
# class PageHeader:
#     page_type: int
#     first_free_block_start: int
#     number_of_cells: int
#     start_of_content_area: int
#     fragmented_free_bytes: int
#     offset: int
#     @classmethod
#     def parse_from(cls, database_file, offset):
#         """
#         Parses a page header as mentioned here: https://www.sqlite.org/fileformat2.html#b_tree_pages
#         """
#         instance = cls()
#         instance.offset = offset
#         instance.page_type = int.from_bytes(database_file.read(1), "big")
#         instance.first_free_block_start = int.from_bytes(database_file.read(2), "big")
#         instance.number_of_cells = int.from_bytes(database_file.read(2), "big")
#         instance.start_of_content_area = int.from_bytes(database_file.read(2), "big")
#         instance.fragmented_free_bytes = int.from_bytes(database_file.read(1), "big")
#         return instance
# sqllite_file_parser = SqliteFileParser(database_file_path)
# if command == ".dbinfo":
#     with open(database_file_path, "rb") as database_file:
#          database_file.seek(16)  # Skip the first 16 bytes of the header
#          page_size = int.from_bytes(database_file.read(2), byteorder="big")
#          database_file.seek(103)
#          table_amt = int.from_bytes(database_file.read(2), byteorder="big")
#          print(f"database page size: {page_size}\nnumber of tables: {table_amt}")
# elif command == ".tables":
#     print(" ".join(sqllite_file_parser.sqlite_schema_rows.keys()))
# else:
#     # assume this is "SELECT COUNT(*) FROM {table}
#     sqllite_file_parser.execute_sql(command)

import sys
from dataclasses import dataclass
import sqlparse
from .record_parser import parse_record
from .varint_parser import parse_varint
database_file_path = sys.argv[1]
command = sys.argv[2]
class SqliteFileParser:
    def __init__(self, database_file_path):
        self.database_file = open(database_file_path, "rb")
        self.database_file.seek(16)
        self.page_size = int.from_bytes(self.database_file.read(2), "big")
        self.database_file.seek(28)
        self.page_num = int.from_bytes(self.database_file.read(4), "big")
        self.page_headers = self.read_pages()
        self.sqlite_schema_rows = self.get_sqlite_schema_rows(
            self.database_file, self.get_cell_pointers(self.page_headers[0])
        )
    def get_cell_pointers(self, page_header):
        additional_offset = 4 if page_header.page_type in (2, 5) else 0
        self.database_file.seek(page_header.offset + 8 + additional_offset)
        return [
            int.from_bytes(self.database_file.read(2), "big")
            for _ in range(page_header.number_of_cells)
        ]
    def read_pages(self):
        all_pages = []
        self.database_file.seek(100)
        curr_offset = 100
        for i in range(self.page_num):
            all_pages.append(PageHeader.parse_from(self.database_file, curr_offset))
            curr_offset = self.database_file.seek(self.page_size * (i + 1))
        return all_pages
    def get_sqlite_schema_rows(self, database_file, cell_pointers):
        sqlite_schema_rows = {}
        # Each of these cells represents a row in the sqlite_schema table.
        for cell_pointer in cell_pointers:
            database_file.seek(cell_pointer)
            _number_of_bytes_in_payload = parse_varint(database_file)
            rowid = parse_varint(database_file)
            record = parse_record(database_file, 5)
            # Table contains columns: type, name, tbl_name, rootpage, sql
            #sqlite_schema_rows[record[2].decode()] = {
            sqlite_schema_rows[record[1].decode()] = {
                "type": record[0].decode(),
                "name": record[1].decode(),
                "tbl_name": record[2].decode(),
                "rootpage": record[3],
                "sql": record[4].decode(),
            }
        return sqlite_schema_rows
    #def get_row_count(self, table):
     #   table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
    def get_row_count(self, cell_key):
        table_rootpage = self.sqlite_schema_rows[cell_key]["rootpage"]
        table_page = self.page_headers[table_rootpage - 1]
        columns = self.get_column_count(cell_key)
        records = self.get_records(table_page, columns)
        """
        self.database_file.seek(table_page.offset + 8)
        cell_pointers = self.get_cell_pointers(table_page)
        for pointer in cell_pointers:
            self.database_file.seek(pointer + table_page.offset)
            print(self.database_file.read(30))
        """
        #print(table_page.number_of_cells)
        print(len(records))
    def get_sql_info(self, sql_statement):
        # separate out select, and where clause
        # get: table, columns of interest, and table
        columns = None
        table = None
        where = []
        sql_tokens = sqlparse.parse(sql_statement)[0].tokens
        for token in sql_tokens:
            if isinstance(token, sqlparse.sql.IdentifierList) or isinstance(
                token, sqlparse.sql.Function
            ):
                columns = str(token)
            if isinstance(token, sqlparse.sql.Identifier):
                if columns is None:
                    columns = str(token)
                else:
                    table = str(token)
            if isinstance(token, sqlparse.sql.Where):
                for where_token in token.tokens:
                    if isinstance(where_token, sqlparse.sql.Comparison):
                        for comp_token in where_token.tokens:
                            if str(comp_token) != " ":
                                where.append(str(comp_token))
                            # if comp_token != sqlparse.sql.Whitespace:
                            #    where.append(str(comp_token))
        return {"select": columns, "table": table, "where": where if where else None}
    #def get_column_count(self, table):
     #   create_sql = sqlparse.parse(self.sqlite_schema_rows[table]["sql"])
    def get_column_count(self, cell_key):
        create_sql = sqlparse.parse(self.sqlite_schema_rows[cell_key]["sql"])
        columns = create_sql[0][-1].tokens
        total_columns = []
        for token in columns:
     #       if isinstance(token, sqlparse.sql.Identifier):
            if isinstance(token, sqlparse.sql.Identifier) or str(token) == "domain":
                total_columns.append(str(token))
            if isinstance(token, sqlparse.sql.IdentifierList):
                for sub_token in token:
                    if (
                        isinstance(sub_token, sqlparse.sql.Identifier)
                        and str(sub_token) != "autoincrement"
                    ):
                        total_columns.append(str(sub_token))
        return total_columns
    def get_record_with_id(self, table_page, value, columns):
        cell_pointers = self.get_cell_pointers(table_page)
        records = []
        column_count = len(columns)
        prev_index, prev_pointer = None, None
        for pointer in cell_pointers:
            self.database_file.seek(pointer + table_page.offset)
            if table_page.page_type == 13:
                # leaf node
                total_bytes = parse_varint(self.database_file)
                row_id = parse_varint(self.database_file)
                record = parse_record(self.database_file, column_count)
                if row_id == value:
                    record[0] = row_id
                    record = [c.decode() if isinstance(c, bytes) else c for c in record]
                    record = {columns[i]: record[i] for i in range(len(columns))}
                    return record
            elif table_page.page_type == 5:
                left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
                int_key = parse_varint(self.database_file)
                if prev_index is None:
                    if value < int_key:
                        return self.get_record_with_id(
                            self.page_headers[left_child_pointer - 1], value, columns
                        )
                elif prev_index <= value and value <= int_key:
                    return self.get_record_with_id(
                        self.page_headers[left_child_pointer - 1], value, columns
                    )
                prev_index, prev_pointer = int_key, left_child_pointer
        if table_page.page_type == 5 and value >= prev_index:
            return self.get_record_with_id(
                self.page_headers[table_page.right_pointer - 1], value, columns
            )
    def get_records_with_index(self, table_page, value, columns):
        cell_pointers = self.get_cell_pointers(table_page)
        records = []
        column_count = len(columns)
        prev_index, prev_pointer = None, None
        for pointer in cell_pointers:
            self.database_file.seek(pointer + table_page.offset)
            if table_page.page_type == 13:
                total_bytes = parse_varint(self.database_file)
                row_id = parse_varint(self.database_file)
                record = parse_record(self.database_file, column_count)
                record[0] = row_id
                record = [c.decode() if isinstance(c, bytes) else c for c in record]
                record = {columns[i]: record[i] for i in range(len(columns))}
                records.append(record)
            elif table_page.page_type == 5:
                left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
                int_key = parse_varint(self.database_file)
                records += self.get_records(
                    self.page_headers[left_child_pointer - 1], columns
                )
            elif table_page.page_type == 2:
                left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
                total_bytes = parse_varint(self.database_file)
                key, row_id = parse_record(self.database_file, 2)
                key = key.decode() if key is not None else None
                if key is not None and key == value:
                    records.append(row_id)
                if prev_index is None:
                    if key is not None and value < key:
                        records += self.get_records_with_index(
                            self.page_headers[left_child_pointer - 1], value, columns
                        )
                elif prev_index <= value and key is not None and value <= key:
                    records += self.get_records_with_index(
                        self.page_headers[left_child_pointer - 1], value, columns
                    )
                prev_index, prev_pointer = key, left_child_pointer
            elif table_page.page_type == 10:
                total_bytes = parse_varint(self.database_file)
                key, row_id = parse_record(self.database_file, 2)
                if key.decode() == value:
                    records.append(row_id)
            else:
                print("NEW PAGE TYPE: " + str(table_page.page_type))
        if table_page.page_type == 2 and value >= prev_index:
            records += self.get_records_with_index(
                self.page_headers[table_page.right_pointer - 1], value, columns
            )
        return records
    def get_records(self, table_page, columns):
        # 1910 pages for companies
        cell_pointers = self.get_cell_pointers(table_page)
        records = []
        column_count = len(columns)
        for pointer in cell_pointers:
            self.database_file.seek(pointer + table_page.offset)
            if table_page.page_type == 13:
                total_bytes = parse_varint(self.database_file)
                row_id = parse_varint(self.database_file)
                record = parse_record(self.database_file, column_count)
                record[0] = row_id
                record = [c.decode() if isinstance(c, bytes) else c for c in record]
                record = {columns[i]: record[i] for i in range(len(columns))}
                records.append(record)
            elif table_page.page_type == 5:
                left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
                int_key = parse_varint(self.database_file)
                records += self.get_records(
                    self.page_headers[left_child_pointer - 1], columns
                )
            elif table_page.page_type == 2:
                left_child_pointer = int.from_bytes(self.database_file.read(4), "big")
                total_bytes = parse_varint(self.database_file)
                record = parse_record(self.database_file, 2)
                # records += self.get_records(self.page_headers[left_child_pointer - 1], columns)
            elif table_page.page_type == 10:
                total_bytes = parse_varint(self.database_file)
                record = parse_record(self.database_file, 2)
                # [b'mozambique', 6161476]
                self.database_file.seek(record[1])
                record = parse_record(self.database_file, column_count)
            else:
                print("NEW PAGE TYPE: " + table_page.page_type)
                print("NEW PAGE TYPE: " + str(table_page.page_type))
        if table_page.page_type in (2, 5):
            records += self.get_records(
                self.page_headers[table_page.right_pointer - 1], columns
            )
        return records
    def execute_sql(self, sql_statement):
        # print(self.sqlite_schema_rows)
        sql_info = self.get_sql_info(sql_statement)
        table = sql_info["table"]
        if sql_info["select"].upper() == "COUNT(*)":
            self.get_row_count(table)
            return
        columns = self.get_column_count(table)
        #column_count = len(columns)
        #table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
        #table_page = self.page_headers[table_rootpage - 1]
        #self.database_file.seek(table_page.offset + 8)
        #records = self.get_records(table_page, columns)
        # if False:
        if sql_info["where"] and sql_info["where"][0] == "country":
            index_root_page = self.sqlite_schema_rows["idx_companies_country"][
                "rootpage"
            ]
            index_page = self.page_headers[index_root_page - 1]
            table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
            table_page = self.page_headers[table_rootpage - 1]
            record_ids = self.get_records_with_index(
                index_page, sql_info["where"][2].replace("'", ""), columns
            )
            records = []
            for record_id in record_ids:
                records.append(self.get_record_with_id(table_page, record_id, columns))
        else:
            table_rootpage = self.sqlite_schema_rows[table]["rootpage"]
            table_page = self.page_headers[table_rootpage - 1]
            records = self.get_records(table_page, columns)
        columns_of_interest = sql_info["select"].split(", ")
        for i, record in enumerate(records):
            total_row = []
            if sql_info["where"] is None:
                for col in columns_of_interest:
                    total_row.append(str(record[col]))
            else:
                comparison = sql_info["where"]
                comp_col = comparison[0]
                comp_val = comparison[2].replace("'", "")
                # assume this is an equality comparison
                if record[comp_col] == comp_val:
                    for col in columns_of_interest:
                        total_row.append(str(record[col]))
            if len(total_row) > 0:
                print("|".join(total_row))
@dataclass(init=False)
class PageHeader:
    page_type: int
    first_free_block_start: int
    number_of_cells: int
    start_of_content_area: int
    fragmented_free_bytes: int
    offset: int
    right_pointer: int
    @classmethod
    def parse_from(cls, database_file, offset):
        """
        Parses a page header as mentioned here: https://www.sqlite.org/fileformat2.html#b_tree_pages
        """
        instance = cls()
        instance.offset = offset
        instance.page_type = int.from_bytes(database_file.read(1), "big")
        instance.first_free_block_start = int.from_bytes(database_file.read(2), "big")
        instance.number_of_cells = int.from_bytes(database_file.read(2), "big")
        instance.start_of_content_area = int.from_bytes(database_file.read(2), "big")
        instance.fragmented_free_bytes = int.from_bytes(database_file.read(1), "big")
        if instance.page_type in (2, 5):
            instance.right_pointer = int.from_bytes(database_file.read(4), "big")
        else:
            instance.right_pointer = None
        return instance
sqllite_file_parser = SqliteFileParser(database_file_path)
if command == ".dbinfo":
    with open(database_file_path, "rb") as database_file:
         database_file.seek(16)  # Skip the first 16 bytes of the header
         page_size = int.from_bytes(database_file.read(2), byteorder="big")
         database_file.seek(103)
         table_amt = int.from_bytes(database_file.read(2), byteorder="big")
         print(f"database page size: {page_size}\nnumber of tables: {table_amt}")
elif command == ".tables":
    #print(" ".join(sqllite_file_parser.sqlite_schema_rows.keys()))
    tables = [
        sqllite_file_parser.sqlite_schema_rows[table]["tbl_name"]
        for table in sqllite_file_parser.sqlite_schema_rows
        if sqllite_file_parser.sqlite_schema_rows[table]["type"] == "table"
    ]
    print(" ".join(tables))
else:
    # assume this is "SELECT COUNT(*) FROM {table}
    sqllite_file_parser.execute_sql(command)