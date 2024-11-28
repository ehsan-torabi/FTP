from asyncio import Lock
import asyncio
import os
import sqlite3 as sql3


class ServerDB:
    def __init__(self) -> None:
        self.DBPATH = "./db.sqlite"
        self.lock = Lock()
        query = """
        PRAGMA foreign_keys = ON;

        CREATE TABLE Permission(
        name VARCHAR(15) PRIMARY KEY,
        read BOOLEAN DEFAULT "0",
        write BOOLEAN DEFAULT "0"
        );


        CREATE TABLE Users(id INTEGER PRIMARY KEY NOT NULL,
        username VARCHAR(64) UNIQUE NOT NULL,
        password VARCHAR(128) NOT NULL,
        role    VARCHAR(8) DEFAULT "user",
        permName VARCHAR(15) DEFAULT "restricted",
        FOREIGN KEY (permName) REFERENCES Permission (name)
        ON DELETE SET DEFAULT
        ON UPDATE CASCADE
        );"""
        
        if not os.path.exists(self.DBPATH):
                print("DB Not found!\nI'v create new.")
                dbConnection = sql3.connect(self.DBPATH)
                cursur = dbConnection.cursor()
                for  q in query.split(";"):
                    if len(q) > 1:
                        cursur.execute(q)
                        print("Executeed: ",q.strip())
                print("DB Created and connected.")
                dbConnection.close()

        else:
                dbConnection = sql3.connect(self.DBPATH)
                dbConnection.close()
                print("DB Connected.")
        

    def __getConnection(self):
        return sql3.connect(self.DBPATH)
    

    async def validate_user(self,username:str,password:str) -> bool:
        query = """SELECT 1
                FROM Users u 
                WHERE u.username=? AND u.password=?;
                """
        
        async with self.lock:
            try:
                con = self.__getConnection()
                cur = con.execute(query, (username,password))
                user = cur.fetchone()
                if user:
                    return True
                else:
                    
                    return False

            except sql3.Error as e :
                print(f"validate_user {username} : {e}")
                return False
            
    async def add_permission(self, name: str, read: bool, write: bool):
        query = """
                INSERT INTO Permission (name,read,write) 
                VALUES (?,?,?);
                """
        
        async with self.lock:
            con = self.__getConnection()
            try:
                con.execute(query, (name, read, write))
                con.commit()
            except sql3.IntegrityError as e:
                print(f"add_permission{name, read, write,} : This field is exists!")
            finally:
                con.close()

    async def add_user(self, username, password, role, perm_name="restricted"):
        query = """
                INSERT INTO users (username,password,role,permName) 
                VALUES (?,?,?,?);
                """
        
        async with self.lock:
            con = self.__getConnection()
            try:
                con.execute(query, (username, password, role, perm_name))
                con.commit()
            except sql3.IntegrityError as e:
                print(f"add_user{username,password} : This field is exists!")

            finally:
                con.close()

    async def get_user_by_username(self, username) -> dict:
        query = """SELECT username , role , permName , read , write
                FROM Users u  RIGHT JOIN Permission p ON u.permName=p.name 
                WHERE u.username=?;
                """
        
        async with self.lock:
            try:
                con = self.__getConnection()
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
                    print(f"User ({username}) not valid!")
                    return None

            except sql3.Error as e :
                print(f"get_user_by_username {username} : {e}")
                return None
            
    async def get_user_by_id(self, id) -> dict:
        query = """
                SELECT username , role , permName , read , write
                FROM Users u  RIGHT JOIN Permission p ON u.permName=p.name 
                WHERE u.id=?;
                """
        
        async with self.lock:
            con = self.__getConnection()
            try:
                id = str(id)
                cur = con.execute(query, id)
                user = cur.fetchone()
                if user:
                    return {
                        "username": user[0],
                        "role": user[1],
                        "permName": user[2],
                        "read": bool(user[3]),
                        "write": bool(user[4]),
                    }
                else :
                    print(f"ID ({id}) not valid!")
                    return None

            except sql3.Error as e:
                print(f"get_user_by_id {id} : {e}")
                return None


async def main():
    db = ServerDB()
    await db.add_permission("restricted", True, False)
    await db.add_user("ehsan", "123456", "user")
    await db.add_user("mohammad", "12345678", "admin")
    print(await db.get_user_by_username("ehsan"))
    print(await db.get_user_by_id(1))
    print(await db.validate_user("ehsan","1234"))

if __name__ == "__main__":
    asyncio.run(main())
