import datetime
import os
import sqlite3 as sql3
from threading import Lock


class ServerDB:
    def __init__(self) -> None:
        self.DBPATH = os.path.abspath("../db.sqlite")
        self.read_lock = Lock()
        self.write_lock = Lock()
        self.create_tables()

    def create_tables(self):
        query = """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS Permission(
            name VARCHAR(15) PRIMARY KEY,
            read BOOLEAN DEFAULT 0,
            write BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY NOT NULL,
            username VARCHAR(64) UNIQUE NOT NULL,
            password VARCHAR(128) NOT NULL,
            role VARCHAR(8) DEFAULT 'user',
            permName VARCHAR(15) DEFAULT 'restricted',
            FOREIGN KEY (permName) REFERENCES Permission (name)
            ON DELETE SET DEFAULT
            ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS LoggedIn(
            id INTEGER PRIMARY KEY NOT NULL,
            userID INTEGER NOT NULL,
            authKey VARCHAR(128) NOT NULL UNIQUE,
            login_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userID) REFERENCES Users (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        );"""

        with self.__getConnection() as con:
            try:
                for q in query.strip().split(";"):
                    if q.strip():
                        con.execute(q)
                        print("Executed: ", q.strip())
                print("Database tables created or verified.")
            except sql3.Error as e:
                print(f"Error creating tables: {e}")

    def __getConnection(self):
        try:
            return sql3.connect(self.DBPATH)
        except sql3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def validate_user(self, username: str, password: str) -> bool:
        query = """SELECT 1 FROM Users WHERE username = ? AND password = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (username, password))
                return cur.fetchone() is not None
            except sql3.Error as e:
                print(f"Error validating user {username}: {e}")
                return False

    def add_permission(self, name: str, read: bool, write: bool):
        query = """INSERT INTO Permission (name, read, write) VALUES (?, ?, ?);"""
        with self.read_lock, self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (name, read, write))
                con.commit()
            except sql3.IntegrityError:
                print(f"Permission '{name}' already exists!")
            except sql3.Error as e:
                print(f"Error adding permission '{name}': {e}")

    def add_user(self, username: str, password: str, role: str, perm_name: str = "restricted"):
        query = """INSERT INTO Users (username, password, role, permName) VALUES (?, ?, ?, ?);"""
        with self.read_lock, self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (username, password, role, perm_name))
                con.commit()
            except sql3.IntegrityError:
                print(f"User '{username}' already exists!")
            except sql3.Error as e:
                print(f"Error adding user '{username}': {e}")

    def get_user_by_username(self, username: str) -> dict:
        query = """SELECT u.username, u.role, u.permName, p.read, p.write
                   FROM Users u
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE u.username = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (username,))
                user = cur.fetchone()
                if user:
                    return {
                        "username": user[0],
                        "role": user[1],
                        "permName": user[2],
                        "read": bool(user[3]),
                        "write": bool(user[4]),
                    }
                else:
                    print(f"User '{username}' not found!")
                    return None
            except sql3.Error as e:
                print(f"Error fetching user by username {username}: {e}")
                return None

    def get_user_by_id(self, user_id: int) -> dict:
        query = """SELECT u.username, u.role, u.permName, p.read, p.write
                   FROM Users u
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE u.id = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (user_id,))
                user = cur.fetchone()
                if user:
                    return {
                        "username": user[0],
                        "role": user[1],
                        "permName": user[2],
                        "read": bool(user[3]),
                        "write": bool(user[4]),
                    }
                else:
                    print(f"User ID '{user_id}' not found!")
                    return None
            except sql3.Error as e:
                print(f"Error fetching user by ID {user_id}: {e}")
                return None

    def get_permission_by_name(self, name: str) -> dict:
        query = """SELECT * FROM Permission WHERE name = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (name,))
                permission = cur.fetchone()
                if permission:
                    return {
                        "name": permission[0],
                        "read": bool(permission[1]),
                        "write": bool(permission[2]),
                    }
                else:
                    print(f"Permission '{name}' not found!")
                    return None
            except sql3.Error as e:
                print(f"Error fetching permission by name {name}: {e}")
                return None

    def add_user_logged_in(self, user_id: int, auth_key: str):
        query = """INSERT INTO LoggedIn (userID, authKey,login_datetime) VALUES (?, ?,?);"""
        with self.read_lock, self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (user_id, auth_key,str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                con.commit()
            except sql3.IntegrityError:
                print(f"User ID '{user_id}' is already logged in.")
            except sql3.Error as e:
                print(f"Error adding logged in user ID '{user_id}': {e}")

    def get_user_by_login_key(self, auth_key: str) -> dict:
        query = """SELECT u.username, u.role, u.permName, p.read, p.write
                   FROM Users u
                   JOIN LoggedIn l ON l.userID = u.id
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE l.authKey = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (auth_key,))
                user = cur.fetchone()
                if user:
                    return {
                        "username": user[0],
                        "role": user[1],
                        "permName": user[2],
                        "read": bool(user[3]),
                        "write": bool(user[4]),
                    }
                else:
                    print(f"Auth key '{auth_key}' not valid!")
                    return None
            except sql3.Error as e:
                print(f"Error fetching user by login key {auth_key}: {e}")
                return None

    def check_user_logged_in(self, user_id: int) -> bool:
        query = """SELECT login_datetime FROM LoggedIn WHERE userID = ?;"""
        with self.write_lock, self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (user_id,))
                check = cur.fetchone()
                if check:
                    login_time = datetime.datetime.fromisoformat(check[0])
                    if datetime.datetime.now() - login_time <= datetime.timedelta(minutes=5):
                        return True
                    else:
                        self.remove_user_logged_in(user_id)
                return False
            except sql3.Error as e:
                print(f"Error checking if user {user_id} is logged in: {e}")
                return False

    def remove_user_logged_in(self, user_id: int):
        query = """DELETE FROM LoggedIn WHERE userID = ?;"""
        with self.read_lock, self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (user_id,))
                con.commit()
                print(f"User ID '{user_id}' logged out.")
                return
            except sql3.Error as e:
                print(f"Error logging out user ID '{user_id}': {e}")
                return

    def check_user_login_by_auth_key(self, auth_key: str) -> bool:
        query = """SELECT u.id,l.login_datetime
                   FROM Users u
                   JOIN LoggedIn l ON l.userID = u.id
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE l.authKey = ?;"""
        with self.read_lock, self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (auth_key,))
                check = cur.fetchone()
                if check:
                    login_time = datetime.datetime.fromisoformat(check[1])
                    if datetime.datetime.now() - login_time <= datetime.timedelta(minutes=5):
                        return True
                    else:
                        self.remove_user_logged_in(int(check[0]))
                return False
            except sql3.Error as e:
                print(f"Error checking login by auth key {auth_key}: {e}")
                return False


def main():
    db = ServerDB()
    db.add_permission("restricted", True, False)
    db.add_user("ehsan", "123456", "user")
    db.add_user("mohammad", "12345678", "admin")

    # Example usage
    db.add_user_logged_in(1, "auth_key_12345")
    print(db.get_user_by_username("ehsan"))
    print(db.get_user_by_id(1))
    print(db.validate_user("ehsan", "123456"))
    print(db.get_user_by_login_key("auth_key_12345"))
    print(db.check_user_logged_in(1))
    print(db.check_user_login_by_auth_key("auth_key_12345"))


if __name__ == "__main__":
    main()