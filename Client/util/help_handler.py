import os


def show_help():
    os.getcwd()
    with open(os.path.join(os.getcwd(), "util", "assets", "help.txt"), "r") as f:
        help_content = f.read()
        print(help_content)
