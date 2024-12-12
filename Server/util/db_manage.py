import datetime
import os
import sqlite3 as sql3
import time

from Server.util.logging_config import server_logger
from utils.auth import password_hash, check_password


class ServerDB:
    def __init__(self,debug_flag:bool=False) -> None:
        self.DBPATH = os.path.abspath("../db.sqlite")
        self.debug_flag = debug_flag
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
            password VARCHAR(256) NOT NULL,
            role VARCHAR(8) DEFAULT 'user',
            accessPath VARCHAR(512) NOT NULL,
            permName VARCHAR(15) DEFAULT 'restricted',
            FOREIGN KEY (permName) REFERENCES Permission (name)
            ON DELETE SET DEFAULT
            ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS LoggedIn(
            id INTEGER PRIMARY KEY NOT NULL,
            userID INTEGER NOT NULL UNIQUE,
            authKey VARCHAR(256) NOT NULL UNIQUE,
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
                        if self.debug_flag:
                            server_logger.info("Executed: ", q.strip())
                server_logger.info("Database tables created or verified.")
            except sql3.Error as e:
                server_logger.info(f"Error creating tables: {e}")

    def __getConnection(self):
        try:
            return sql3.connect(self.DBPATH)
        except sql3.Error as e:
            server_logger.info(f"Error connecting to database: {e}")
            return None

    def validate_user(self, username: str, password: str) -> bool:
        query = """SELECT password FROM Users WHERE username = ?;"""
        with  self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (username,))
                user = cur.fetchone()
                if user is not None:
                    if check_password(user[0], password):
                        return True
                    else:
                        return False
                else:
                    return False
            except sql3.Error as e:
                server_logger.info(f"Error validating user {username}: {e}")
                return False

    def add_permission(self, name: str, read: bool, write: bool):
        query = """INSERT INTO Permission (name, read, write) VALUES (?, ?, ?);"""
        with  self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (name, read, write))
                con.commit()
            except sql3.IntegrityError:
                server_logger.info(f"Permission '{name}' already exists!")
            except sql3.Error as e:
                server_logger.info(f"Error adding permission '{name}': {e}")

    def add_user(self, username: str, password: str, role: str, access_path:str, perm_name: str = "restricted", ):
        query = """INSERT INTO Users (username, password, role, permName,accessPath) VALUES (?, ?, ?, ?,?);"""
        with  self.__getConnection() as con:
            if con is None:
                return
            try:
                hashed_password = password_hash(password)
                access_path = os.path.abspath(access_path)
                con.execute(query, (username, hashed_password, role, perm_name, access_path))
                con.commit()
            except sql3.IntegrityError:
                server_logger.info(f"User '{username}' already exists!")
            except sql3.Error as e:
                server_logger.info(f"Error adding user '{username}': {e}")

    def get_user_by_username(self, username: str) -> dict:
        query = """SELECT u.id, u.username, u.role, u.permName,u.accessPath, p.read, p.write
                   FROM Users u
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE u.username = ?;"""
        with self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (username,))
                user = cur.fetchone()
                if user:
                    return {
                        "id":user[0],
                        "username": user[1],
                        "role": user[2],
                        "permName": user[3],
                        "access_path":user[4],
                        "read": bool(user[5]),
                        "write": bool(user[6]),
                    }
                else:
                    server_logger.info(f"User '{username}' not found!")
                    return None
            except sql3.Error as e:
                server_logger.info(f"Error fetching user by username {username}: {e}")
                return None



    def get_userid_by_username(self, username: str) -> int:
        query ="""SELECT id FROM Users WHERE username = ?
        """
        with self.__getConnection() as con:
            if con is None:
                return None
            try:
                cur = con.execute(query, (username,))
                userid = cur.fetchone()
                if userid:
                    return int(userid[0])
                else:
                    server_logger.info(f"User username '{username}' not found!")
                    return None
            except sql3.Error as e:
                server_logger.info(f"Error fetching user by ID {username}: {e}")
                return None
    def get_user_by_id(self, user_id: int) -> dict:
        query = """SELECT u.username, u.role, u.permName,u.accessPath, p.read, p.write
                   FROM Users u
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE u.id = ?;"""
        with  self.__getConnection() as con:
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
                        "access_path":user[3],
                        "read": bool(user[4]),
                        "write": bool(user[5]),
                    }
                else:
                    server_logger.info(f"User ID '{user_id}' not found!")
                    return None
            except sql3.Error as e:
                server_logger.info(f"Error fetching user by ID {user_id}: {e}")
                return None

    def get_permission_by_name(self, name: str) -> dict:
        query = """SELECT * FROM Permission WHERE name = ?;"""
        with  self.__getConnection() as con:
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
                    server_logger.info(f"Permission '{name}' not found!")
                    return None
            except sql3.Error as e:
                server_logger.info(f"Error fetching permission by name {name}: {e}")
                return None

    def add_user_logged_in(self, user_id: int, auth_key: str):
        query = """INSERT INTO LoggedIn (userID, authKey,login_datetime) VALUES (?, ?,?);"""
        try:
            with  self.__getConnection() as con:
                if con is None:
                    return
                con.execute(query, (user_id, auth_key,str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                con.commit()
        except sql3.IntegrityError:
                con.close()
                self.remove_user_logged_in(user_id)
                self.add_user_logged_in(user_id, auth_key)
        except sql3.Error as e:
                server_logger.info(f"Error adding logged in user ID '{user_id}': {e}")

    def get_user_by_login_key(self, auth_key: str) -> dict:
        query = """SELECT u.username, u.role, u.permName,u.accessPath, p.read, p.write
                   FROM Users u
                   JOIN LoggedIn l ON l.userID = u.id
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE l.authKey = ?;"""
        with  self.__getConnection() as con:
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
                        "access_path":user[3],
                        "read": bool(user[4]),
                        "write": bool(user[5]),
                    }
                else:
                    server_logger.info(f"Auth key '{auth_key}' not valid!")
                    return None
            except sql3.Error as e:
                server_logger.info(f"Error fetching user by login key {auth_key}: {e}")
                return None

    def check_user_logged_in(self, user_id: int) -> bool:
        query = """SELECT login_datetime FROM LoggedIn WHERE userID = ?;"""
        with  self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (user_id,))
                check = cur.fetchone()
            except sql3.Error as e:
                server_logger.info(f"Error checking if user {user_id} is logged in: {e}")
                return False
        if check:
                login_time = datetime.datetime.fromisoformat(check[0])
                if datetime.datetime.now() - login_time <= datetime.timedelta(minutes=5):
                    return True
                else:
                    self.remove_user_logged_in(user_id)
        return False


    def remove_user_logged_in(self, user_id: int):
        query = """DELETE FROM LoggedIn WHERE userID = ?;"""
        with  self.__getConnection() as con:
            if con is None:
                return
            try:
                con.execute(query, (user_id,))
                con.commit()
                server_logger.info(f"User ID '{user_id}' logged out.")
                return
            except sql3.Error as e:
                server_logger.info(f"Error logging out user ID '{user_id}': {e}")
                return

    def check_user_login_by_auth_key(self, auth_key: str) -> bool:
        query = """SELECT u.id,l.login_datetime
                   FROM Users u
                   JOIN LoggedIn l ON l.userID = u.id
                   LEFT JOIN Permission p ON u.permName = p.name
                   WHERE l.authKey = ?;"""
        with self.__getConnection() as con:
            if con is None:
                return False
            try:
                cur = con.execute(query, (auth_key,))
                check = cur.fetchone()
            except sql3.Error as e:
                server_logger.info(f"Error checking login by auth key {auth_key}: {e}")
                return False
        if check:
            login_time = datetime.datetime.fromisoformat(check[1])
            if datetime.datetime.now() - login_time <= datetime.timedelta(minutes=15):
                return True
            else:
                self.remove_user_logged_in(int(check[0]))
        return False



def main():
    db = ServerDB()
    db.add_permission("restricted", True, False)
    db.add_user("ehsan", "123456", "user",access_path="/home/ehsan/Desktop")
    db.add_user("mohammad", "12345678", "admin",access_path="/home")

    # Example usage
    # db.add_user_logged_in(1, "auth_key_12345")
    # server_logger.info(db.get_user_by_username("ehsan"))
    # server_logger.info(db.get_user_by_username("mohammad"))
    # server_logger.info(db.get_user_by_id(1))
    # server_logger.info(db.validate_user("ehsan", "12345"))
    # server_logger.info(db.get_user_by_login_key("auth_key_12345"))
    # server_logger.info(db.check_user_logged_in(1))
    # server_logger.info(db.check_user_login_by_auth_key("auth_key_12345"))


if __name__ == "__main__":
    main()