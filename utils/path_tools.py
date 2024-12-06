import os
import pathlib


def process_path(input_path,current_user_dir):
    """
    Process and normalize file paths from various input formats.

    Args:
        input_path (str): The input file path to process
        current_user_dir (str): The current user's directory path

    Returns:
        str: A fully expanded, absolute path
    """
    # Handle empty or None input
    if not input_path:
        return None

    # Remove any surrounding quotes
    input_path = input_path.strip('\'"').strip()

    try:
        # Check if input_path is a file name
        if input_path == os.path.basename(input_path) and input_path not in ["~","..",".",current_user_dir,"-","/"]:
            input_path = os.path.join(os.path.abspath(current_user_dir), input_path)

        # Expand user home directory (~)
        expanded_path = os.path.expanduser(input_path)

        # Convert to absolute path
        abs_path = os.path.abspath(expanded_path)

        # Resolve any symbolic links and normalize path
        normalized_path = os.path.realpath(abs_path)

        return normalized_path

    except Exception as e:
        print(f"Error processing path: {e}")
        return None


def validate_path(processed_path, dir_check=False, file_check=False,check_exists=False):
    """
    Validate the processed path.

    Args:
        processed_path (str): The processed path to validate
        check_exists (bool): Whether to check if the path actually exists
        dir_check (bool): Whether to check if the path is a directory
        file_check (bool): Whether to check if the path is a file
    Returns:
        bool: Whether the path is valid
    """
    if not processed_path:
        return False

    # Basic path validation
    try:
        # Check if path is a valid string
        path = pathlib.Path(processed_path)

        # Optionally check if path exists
        if check_exists:
            return path.exists()

        if dir_check:
            return path.is_dir()

        if file_check:
            return path.is_file()
        return True
    except Exception:
        return False


class PathAccessController:
    def __init__(self,
                 public_base_dir='/Public',
                 admin_bypass=False,
                 user_role='normal'):
        """
        Initialize path access controller.

        Args:
            public_base_dir (str): Base directory for public access
            admin_bypass (bool): Whether admin can bypass restrictions
            user_role (str): User role ('normal' or 'admin')
        """
        # Normalize and expand the public base directory
        self.public_base_dir = os.path.abspath(os.path.expanduser(public_base_dir))
        self.admin_bypass = admin_bypass
        self.user_role = user_role.lower()

    def process_path(self, input_path):
        """
        Process and validate path based on user role.

        Args:
            input_path (str): The input file path to process

        Returns:
            str: A fully expanded, absolute path if access is allowed
            None: If path access is denied
        """
        # Handle empty or None input
        if not input_path:
            return None

        # Remove any surrounding quotes and strip whitespace
        input_path = input_path.strip('\'"').strip()

        try:
            # Expand user home directory (~)
            expanded_path = os.path.expanduser(input_path)

            # Convert to absolute path
            abs_path = os.path.abspath(expanded_path)

            # Resolve any symbolic links and normalize path
            normalized_path = os.path.realpath(abs_path)

            # Check access based on user role
            if self.check_path_access(normalized_path):
                return normalized_path
            else:
                print(f"Access denied to path: {normalized_path}")
                return None

        except Exception as e:
            print(f"Error processing path: {e}")
            return None

    def check_path_access(self, path):
        """
        Check if the user has access to the specified path.

        Args:
            path (str): Absolute path to check

        Returns:
            bool: True if access is allowed, False otherwise
        """
        # Admin bypass if enabled
        if self.user_role == 'admin' and self.admin_bypass:
            return True

        # Normal user restrictions
        if self.user_role == 'normal':
            # Check if path is within public directory
            try:
                # Use os.path.commonpath to safely check if path is under public base
                common_path = os.path.commonpath([self.public_base_dir, path])
                return common_path == self.public_base_dir
            except ValueError:
                # If paths are on different drives or cannot be compared
                return False

        # Default to restrictive access
        return False

    def list_allowed_paths(self):
        """
        List all paths allowed for the current user role.

        Returns:
            list: Allowed paths
        """
        if self.user_role == 'admin' and self.admin_bypass:
            return ['All paths accessible']

        if self.user_role == 'normal':
            return [self.public_base_dir]

        return []


def main():
    # Test various path formats
    test_paths = [
        '~/Downloads/file.txt',  # Home directory path
        '../documents/file.txt',  # Relative path with parent directory
        'file.txt',  # Current directory file
        '/home/user/documents/file',  # Absolute path
        '"file with spaces.txt"',  # Path with quotes
        '  ~/file.txt  '  # Path with extra whitespace
    ]

    for path in test_paths:
        processed = process_path(path,".")
        print(f"Original: {path}")
        print(f"Processed: {processed}")
        print(f"Valid: {validate_path(processed)}\n")


if __name__ == '__main__':
    main()