""" Functions to manage the database for trstats """
import sqlite3
from . import schema

class Database():
    """ Class to handle all database interactions """

    def __init__(self, file):
        """ Initialize the database by adding handles to all tables """

        # "Connect" to the database
        self.dbh = sqlite3.connect(file)

        # Populate the database with tables
        for table in schema.TABLES:
            setattr(self, table, Table(table, self.dbh))

    def rebuild(self):
        """ Rebuild the entire database """
        for table in schema.TABLES:
            getattr(self, table).rebuild()

    def vacuum(self):
        """ Re-acquire free space after heavy database operations """
        self.dbh.execute('VACUUM;')
        self.dbh.commit()


class Table():
    """ Class for each table of a database """

    def __init__(self, table, dbh):
        ''' Initialize this table '''

        # Store incoming varaibles
        self.dbh = dbh
        self.table = table

        # Get extrapolated data
        self.columns = schema.TABLES[self.table]['columns']
        self.indices = schema.TABLES[self.table]['indices']

        # Check yourself before you wreck yourself
        self.check()

    def check(self):
        """ Run a complete check on the database table. """
        self.check_columns()
        self.check_indices()

    def check_columns(self):
        """ Check that all columns for a table exist """
        # pylint: disable=too-many-branches

        # Acquire database cursor
        dbc = self.dbh.cursor()

        current_columns = self.get_current_columns()
        if not current_columns:
            # Assume the table doesn't exist, and make it.
            self.create_full_table()
            return

        # Check what needs to be done for each column
        rebuild = False
        for column in self.columns:
            if column[0] not in current_columns:
                print(f'DB: add column {column[0]} to table {self.table}')
                query = f'ALTER TABLE {self.table} ADD "{column[0]}" {column[1]}'
                if column[2]: # Not Null
                    query += ' NOT NULL'
                if column[3] is not None: # Default
                    if isinstance(column[3], (float, int)):
                        query += f' DEFAULT {str(column[3])}'
                    elif isinstance(column[3], bool):
                        query += f' DEFAULT {"1" if column[3] else "0"}'
                    else:
                        query += f' DEFAULT \'{str(column[3])}\''
                if column[4]: # Primary Key
                    query += ' PRIMARY KEY'
                if column[5]: # Unique
                    query += ' UNIQUE'
                query += ';'
                dbc.execute(query)
            elif column[1] != current_columns[column[0]]['type']:
                print(f'DB: {self.table}.{column[0]} type changed from '
                      f'{str(current_columns[column[0]]["type"])} to {str(column[1])}')
                rebuild = True
            elif column[2] != current_columns[column[0]]['notnull']:
                print(f'DB: {self.table}.{column[0]} not null changed from '
                      f'{str(current_columns[column[0]]["notnull"])} to {str(column[2])}')
                rebuild = True
            elif column[3] != current_columns[column[0]]['default']:
                print(f'DB: {self.table}.{column[0]} default value changed from '
                      f'{str(current_columns[column[0]]["default"])} to {str(column[3])}')
                rebuild = True

        # Rebuild the database table, if it needs to be
        if rebuild:
            self.rebuild()

    def rebuild(self):
        """ Rebuild the whole database table """
        dbc = self.dbh.cursor()
        current_columns = self.get_current_columns()
        print(f'DB: Rebuilding table {self.table}, this may take awhile...')
        self.create_full_table(rebuild=True)
        common = list()
        for column in self.columns:
            if column[0] in current_columns:
                common.append(column[0])
        common = ', '.join(common)
        print(f'DB: copy data from \'{self.table}\' table to \'new_{self.table}\' table')
        dbc.execute(f'INSERT INTO new_{self.table} ({common}) '
                    f'SELECT {common} FROM {self.table}')
        print(f'DB: remove table \'{self.table}\'')
        dbc.execute(f'DROP TABLE {self.table}')
        print(f'DB: move \'new_{self.table}\' table to \'{self.table}\' table')
        dbc.execute(f'ALTER TABLE new_{self.table} RENAME TO {self.table}')

    def create_full_table(self, rebuild=False):
        ''' Create a table with the specified schema from scratch. '''
        if rebuild:
            table = 'new_' + self.table
        else:
            table = self.table
        dbc = self.dbh.cursor()
        print(f'DB: Creating \'{table}\' table')
        query = f'CREATE TABLE "{table}" ( '
        for column in self.columns:
            query += f'"{column[0]}" {column[1]}'
            if column[2]: # Not Null
                query += ' NOT NULL'
            if column[3] is not None: # Default
                if isinstance(column[3], (float, int)):
                    query += f' DEFAULT {str(column[3])}'
                elif isinstance(column[3], bool):
                    query += f' DEFAULT {"1" if column[3] else "0"}'
                else:
                    query += f' DEFAULT \'{str(column[3])}\''
            if column[4]: # Primary Key
                query += ' PRIMARY KEY'
            if column[5]: # Unique
                query += ' UNIQUE'
            query += ', '
        query = query[:-2] + ' );'
        dbc.execute(query)

    def get_current_columns(self):
        """ Get information on what columns are currently in the table """
        dbc = self.dbh.cursor()
        dbr = dbc.execute(f'PRAGMA table_info({self.table});').fetchall()
        values = dict()
        for column in dbr:
            values[column[1]] = {
                'type': column[2],
                'notnull': bool(column[3]),
                'default': column[4]
            }
            # Fix defaults because numbers are given as strings
            if column[2] == 'INTEGER' and column[4] is not None:
                values[column[1]]['default'] = int(column[4])
            elif column[2] == 'REAL' and column[4] is not None:
                values[column[1]]['default'] = float(column[4])
        return values

    def check_indices(self):
        """ Check all indices for the current table """
        dbc = self.dbh.cursor()
        # Check indices
        dbr = dbc.execute(f'PRAGMA index_list({self.table});').fetchall()
        schema_indices = dict()
        for index in dbr:
            if index[3] == 'c':
                dbx = dbc.execute(f'PRAGMA index_info({index[1]})').fetchall()
                schema_indices[index[1]] = {
                    'columns': [column[2] for column in dbx],
                    'unique': bool(index[2])
                }
        # Check for indices that need to be removed first
        for indexname, index in schema_indices.items():
            if indexname not in self.indices:
                print('DB: remove index ' + indexname)
                dbc.execute(f'DROP INDEX {indexname}')
        # Check for indices that need to be added or replaced
        for indexname, index in self.indices.items():
            if indexname not in schema_indices:
                print('DB: add index ' + indexname)
                query = 'CREATE'
                if index[1]:
                    query += ' UNIQUE'
                query += f' INDEX "{indexname}" ON "{self.table}" ( '
                for column in index[0]:
                    query += f'"{column}", '
                query = query[:-2] + ' );'
                dbc.execute(query)
            elif index[0] != schema_indices[indexname]['columns'] or\
                index[1] != schema_indices[indexname]['unique']:
                print('DB: replace index ' + indexname)
                dbc.execute(f'DROP INDEX {indexname}')
                query = 'CREATE'
                if index[1]:
                    query += ' UNIQUE'
                query += f' INDEX "{indexname}" ON "{self.table}" ( '
                for column in index[0]:
                    query += f'"{column}", '
                query = query[:-2] + ' );'
                dbc.execute(query)
        self.dbh.commit()
