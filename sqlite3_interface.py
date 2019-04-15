import sqlite3
import datetime


class DataBaseInterface:
    """
    Interface for accessing an sqlite database
    """

    def __init__(self, db_path):
        """
        Opens a database
        :param db_path: path to sqlite3 file
        """
        self.conn = sqlite3.connect(db_path)

    def get_tables(self):
        """
        gets a list of tables
        :return: list of tables
        """
        results = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

        ret = []
        for result in results.fetchall():
            ret.append(result[0])

        return ret

    def get_table_header(self, table_name):
        """
        Gets the full table header
        :param table_name: table name
        :return: list of all the table columns
        """
        results = self.conn.execute("PRAGMA table_info(%s);" % table_name)

        ret = []

        for result in results.fetchall():
            ret.append((result[1], result[2]))

        return ret
    
    def print_table(self, table_name, column):
        """
        Prints all the rows of a table
        :param table_name: table name to print
        :param column: column to print
        """
        cur = self.conn.execute("SELECT _id,%s FROM %s" % (column[0], table_name))

        print("ID\t\t%s" % column[0])
        for row in cur.fetchall():
            print("%s\t\t%s" % (row[0], row[1]))

    def shift_time_column(self, table_name, column, time_shift):
        """
        Shift a time column by a time shift
        :param table_name: table name
        :param column: column to shift
        :param time_shift: amount of time to shift
        """

        cur = self.conn.execute("SELECT _id,%s FROM %s" % (column[0], table_name))

        for row in cur.fetchall():
            id = row[0]
            time_stamp = row[1]

            time_stamp = time_stamp / pow(10, 3)

            new_time = datetime.datetime.fromtimestamp(time_stamp) + datetime.timedelta(time_shift)

            new_time_stamp = int(round(new_time.timestamp(), 3) * pow(10, 3))

            self.conn.execute("UPDATE %s SET %s=? WHERE _id=?" % (table_name, column[0]), (new_time_stamp, id))
            self.conn.commit()





