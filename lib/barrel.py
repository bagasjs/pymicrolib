#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Barrel is a simple ORM library that only supports sqlite3
all in a single file and with no dependencies other than the
Python Standard Library.

Copyright (c) 2025, bagasjs
License: MIT (see the details at the very bottom)
"""

from __future__ import annotations
from typing import List, Any, Dict
from abc import ABC, abstractmethod
import sqlite3

__author__ = 'bagasjs'
__version__ = '0.0.1'
__license__ = 'MIT'

Record = Dict[str, Any]
Records = List[Record]

def pluck(record: Record, keys: List[str]) -> Record:
    return { key : record[key] for key in keys }

def plucks(records: Records, keys: List[str]) -> Records:
    return [ { key: record[key] for key in keys } for record in records ]

def unplucks(records: Records, key: str, value: Any) -> Records:
    for i in range(len(records)):
        records[i][key] = value
    return records

MIGRATION_TABLE_NAME = "_barrel_migrations"

# STANDARD SET OF SQL DATA TYPES
# Although the library works with sqlite in case
# I need more database in the future
DTYPE_SHORT_STRING = "VARCHAR(256)"
DTYPE_INTEGER  = "INTEGER"
DTYPE_TEXT     = "TEXT"
DTYPE_DATE     = "DATE"
DTYPE_TIME     = "TIME"
DTYPE_DATETIME = "DATETIME"

class WhereClause(object):
    is_or: bool
    lhs: str
    op: str
    rhs: Any

class Field(object):
    def __init__(self, 
                 name: str, 
                 datatype: str, 
                 default_value: Any | None = None,
                 nullable: bool = False,
                 unique: bool = False, 
                 primarykey: bool = False,
                 foreignkey: bool = False,
                 referenced_table_name: str = "",
                 referenced_field_name: str = "",
                 ):
        self.name = name
        self.datatype = datatype
        self.default_value = default_value
        self.is_nullable = nullable
        self.is_unique = unique
        self.is_primarykey = primarykey
        self.is_foreignkey = foreignkey
        self.referenced_table_name = referenced_table_name
        self.referenced_field_name = referenced_field_name

class Entity(object):
    def __init__(self, data: Record, ctx: Context, repo: Repository):
        self.data = data
        self.ctx = ctx
        self.repo = repo

    def belongs_to(self):
        pass

    def has_many(self):
        pass

    def belongs_to_many(self):
        pass

    def __getitem__(self, key: str):
        return self.data[key]

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

class QueryResult(object):
    _cursor: sqlite3.Cursor
    _columns: List[str]

    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor
        self._columns = (
            [ desc[0] for desc in self._cursor.description ] 
            if self._cursor.description else []
        )

    def next(self) -> Dict[str, Any] | None:
        data = self._cursor.fetchone()
        if data is None:
            return None
        return dict(zip(self._columns, data)) 

class Repository(object):
    """
    An abstraction of all SQL operations 
    """
    _table_name: str
    _ctx: Context

    # Query Builder
    _selected_columns: List[str]
    _order_by: str
    _where_clauses: List[WhereClause]

    def __init__(self, table_name: str, ctx: Context):
        self._table_name = table_name
        self._ctx = ctx
        self.reset()

    def create_table(self, fields: List[Field], force=False):
        """
        Run SQL table creation based on the given fields
        """
        field_sqls = []
        constraint_sqls = []
        pk_field_names = []
        for field in fields:
            field_sql_parts = [ field.name, field.datatype ]
            if not field.is_nullable and not field.is_primarykey:
                field_sql_parts.append("NOT NULL")
            if field.default_value is not None:
                field_sql_parts.append(f"DEFAULT {field.default_value}")
            if field.is_unique:
                constraint_sqls.append(f"CONSTRAINT UC_{self._table_name}_{field.name} UNIQUE({field.name})")
            if field.is_primarykey:
                pk_field_names.append(field.name)
            if field.is_foreignkey:
                name = f"FK_{self._table_name}_to_{field.referenced_table_name}_via_{field.referenced_field_name}"
                constraint_sqls.append(f"CONSTRAINT {name} FOREIGN KEY({field.name}) " 
                                       f"REFERENCES {field.referenced_table_name}({field.referenced_field_name})")
            field_sqls.append(" ".join(field_sql_parts))


        if len(pk_field_names) > 0:
            constraint_sqls.append(f"CONSTRAINT PK_{self._table_name}_{field.name} PRIMARY KEY({','.join(pk_field_names)})")

        if force and self.table_exist():
            self.drop_table()
        res = f"CREATE TABLE IF NOT EXISTS {self._table_name} (\n\t{',\n\t'.join(field_sqls)}"
        if len(constraint_sqls) > 0:
            res += f",\n\t{',\n\t'.join(constraint_sqls)}"
        res += "\n)"
        cur = self._ctx._conn.cursor()
        cur.execute(res)

    def drop_table(self):
        cur = self._ctx._conn.cursor()
        cur.execute("DROP TABLE " + self._table_name)

    def table_exist(self) -> bool:
        cur = self._ctx._conn.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{self._table_name}"')
        return cur.fetchone() is not None 

    # Query Builder functions
    def reset(self):
        self._order_by = ""
        self._selected_columns = []
        self._where_clauses = []

    def where(self, lhs: str, op: str, rhs: Any) -> Repository:
        clause = WhereClause()
        clause.is_or = False
        clause.lhs = lhs
        clause.op = op
        clause.rhs = rhs
        self._where_clauses.append(clause)
        return self

    def or_where(self, lhs: str, op: str, rhs: Any) -> Repository:
        clause = WhereClause()
        clause.is_or = True
        clause.lhs = lhs
        clause.op = op
        clause.rhs = rhs
        self._where_clauses.append(clause)
        return self

    def where_eq(self, lhs: str, rhs: Any) -> Repository:
        return self.where(lhs, "=", rhs)

    def or_where_eq(self, lhs: str, rhs: Any) -> Repository:
        return self.or_where(lhs, "=", rhs)

    # Execution functions
    def get(self):
        selected_columns = "*"
        if len(self._selected_columns) > 0:
            selected_columns = ",".join(self._selected_columns)
        query = f"SELECT {selected_columns} FROM {self._table_name}"
        args = []
        if len(self._where_clauses) > 0:
            query += " WHERE "
            for i, clause in enumerate(self._where_clauses):
                if i != 0:
                    if clause.is_or:
                        query += " OR "
                    else:
                        query += " AND "
                query += f"{clause.lhs} {clause.op} ?"
                args.append(clause.rhs)
        cur = self._ctx._conn.cursor()
        cur = cur.execute(query, args)
        self.reset()
        return QueryResult(cur)

    def all(self) -> List[Dict[str, Any]]:
        self.reset()
        res = self.get()
        data = res.next()
        result = []
        while data:
            result.append(data)
            data = res.next()
        return result

    def first(self) -> Dict[str, Any] | None:
        res = self.get()
        data = res.next()
        if not data:
            return None
        return data
    
    def insert(self, record: Dict[str, Any]):
        keys = []
        placeholders = []
        values = []
        for key, value in record.items():
            keys.append(key)
            placeholders.append("?")
            values.append(value)

        sql = f"INSERT INTO {self._table_name}({','.join(keys)}) VALUES ({','.join(placeholders)})"
        cur = self._ctx._conn.cursor()
        cur = cur.execute(sql, values)
        self.reset()

    def update(self, record: Dict[str, Any]):
        args = []
        query = f"UPDATE {self._table_name} SET"
        for key, value in record.items():
            query += f" {key} = ?"
            args.append(value)

        if len(self._where_clauses) > 0:
            query += " WHERE "
            for i, clause in enumerate(self._where_clauses):
                if i != 0:
                    if clause.is_or:
                        query += " OR "
                    else:
                        query += " AND "
                query += f"{clause.lhs} {clause.op} ?"
                args.append(clause.rhs)

        cur = self._ctx._conn.cursor()
        cur = cur.execute(query, args)
        self.reset()

    def delete(self):
        query = f"DELETE FROM {self._table_name}"
        args = []
        if len(self._where_clauses) > 0:
            query += " WHERE "
            for i, clause in enumerate(self._where_clauses):
                if i != 0:
                    if clause.is_or:
                        query += " OR "
                    else:
                        query += " AND "
                query += f"{clause.lhs} {clause.op} ?"
                args.append(clause.rhs)
        cur = self._ctx._conn.cursor()
        cur = cur.execute(query, args)
        self.reset()

class Context(object):
    _conn: sqlite3.Connection

    def __init__(self, config: str):
        self._conn = sqlite3.connect(config)

    def repo(self, table_name: str) -> Repository:
        return Repository(table_name, self)

"""
Copyright (c) 2025 bagasjs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
