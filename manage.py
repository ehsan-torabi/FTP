from Server.db_manage import ServerDB

db = ServerDB()
db.add_permission("restricted", True, False)
db.add_user("ehsan", "123456", "user", access_path="/home/ehsan/Desktop")
db.add_user("mohammad", "12345678", "admin", access_path="/home")