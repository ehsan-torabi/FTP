from cmd import Cmd

from Server.db_manage import ServerDB


class ServerManage(Cmd):
    def __init__(self):
        super(ServerManage, self).__init__()
        self.prompt = 'db-manage> '
        self.dbConnection = ServerDB(config_path="config.json")

    def do_add_user(self, args):
        """
        Add a new user to the database.

        Usage: add_user <username> <password> <access_path>

        Arguments:
        <username>   The username of the new user.
        <password>   The password for the new user.
        <access_path> The access path associated with the new user.

        If the number of arguments is incorrect, an error message will be displayed.
        """
        parsed_arg = args.split()
        if len(parsed_arg) != 3:
            print("Wrong number of arguments")
            print("Usage: add_user <username> <password> <access_path>")
            return
        self.dbConnection.add_user(parsed_arg[0], parsed_arg[1], "user", parsed_arg[2])
        print("User added.")

    def do_get_user(self, args):
        """
        Retrieve user information by username.

        Usage: get_user <username>

        Arguments:
        <username>   The username of the user to retrieve.

        If the number of arguments is incorrect, an error message will be displayed.
        """
        parsed_arg = args.split(" ")
        if len(parsed_arg) != 1:
            print("Wrong number of arguments")
            print("Usage: get_user <username>")
            return
        print(self.dbConnection.get_user_by_username(parsed_arg[0]))

    def do_remove_user(self, args):
        """
        Remove a user from the database.

        Usage: remove_user <username>

        Arguments:
        <username>   The username of the user to remove.

        If the number of arguments is incorrect, an error message will be displayed.
        The user will be prompted for confirmation before removal.
        """
        parsed_arg = args.split()
        if len(parsed_arg) != 1:
            print("Wrong number of arguments")
            print("Usage: remove_user <username>")
            return
        print(f"Are you sure you want to remove the user {parsed_arg[0]}?[y/n]")
        if input().lower() != "n":
            self.dbConnection.remove_user(parsed_arg[0])
            print("User removed.")

    def do_get_all_user(self, args):
        """
        Retrieve all users from the database.

        Usage: get_all_user [<limit>]

        Arguments:
        <limit>   (Optional) The maximum number of users to retrieve. Defaults to 20 if not provided.

        If no users are found, a message will be displayed.
        """
        parsed_arg = args.split()
        users = []
        if len(parsed_arg) != 1:
            users = self.dbConnection.get_all_user(20)
        else:
            users = self.dbConnection.get_all_user(int(parsed_arg[0]))
        if users:
            for user in users:
                print(user)
        else:
            print("No users found.")

    def do_close(self):
        """Exit the command loop."""
        exit(0)

    def do_quit(self):
        """Exit the command loop."""
        exit(0)


if __name__ == '__main__':
    server = ServerManage()
    server.cmdloop()
