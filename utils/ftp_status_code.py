class FTPStatusCode:
    RESTART_MARKER_REPLY = 100
    SERVICE_READY_IN_MINUTES = 120
    DATA_CONNECTION_OPEN = 125
    FILE_STATUS_OK = 150
    COMMAND_OK = 200
    SYSTEM_STATUS = 211
    DIRECTORY_STATUS = 212
    FILE_STATUS = 213
    HELP_MESSAGE = 214
    NAME_SYSTEM_TYPE = 215
    SERVICE_READY_FOR_NEW_USER = 220
    SERVICE_CLOSING_CONTROL_CONNECTION = 221
    DATA_CONNECTION_OPEN_NO_TRANSFER = 225
    CLOSING_DATA_CONNECTION = 226
    ENTERING_PASSIVE_MODE = 227
    USER_LOGGED_IN = 230
    REQUESTED_FILE_ACTION_OK = 250
    PATHNAME_CREATED = 257
    USER_NAME_OK_NEED_PASSWORD = 331
    NEED_ACCOUNT_FOR_LOGIN = 332
    REQUESTED_FILE_ACTION_PENDING = 350
    SERVICE_NOT_AVAILABLE = 421
    CANT_OPEN_DATA_CONNECTION = 425
    CONNECTION_CLOSED_TRANSFER_ABORTED = 426
    FILE_UNAVAILABLE = 450
    LOCAL_ERROR_IN_PROCESSING = 451
    INSUFFICIENT_STORAGE_SPACE = 452
    FILE_EXISTS_ERROR = 453
    PERMISSION_DENIED = 454
    SYNTAX_ERROR_COMMAND_UNRECOGNIZED = 500
    SYNTAX_ERROR_IN_PARAMETERS = 501
    COMMAND_NOT_IMPLEMENTED = 502
    BAD_SEQUENCE_OF_COMMANDS = 503
    COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER = 504
    NOT_LOGGED_IN = 530
    NEED_ACCOUNT_FOR_STORING_FILES = 532
    REQUESTED_ACTION_NOT_TAKEN_FILE_UNAVAILABLE = 550
    REQUESTED_ACTION_ABORTED_PAGE_TYPE_UNKNOWN = 551
    REQUESTED_FILE_ACTION_ABORTED_EXCEEDED_STORAGE = 552
    REQUESTED_ACTION_NOT_TAKEN_FILE_NAME_NOT_ALLOWED = 553
    PATH_NOT_DIRECTORY = 720
    CHANGE_DIRECTORY_ACCEPTED = 721


def get_ftp_status_message(code):
    """Return the FTP status message for a given code."""
    status_messages = {
        FTPStatusCode.RESTART_MARKER_REPLY: "Restart marker.",
        FTPStatusCode.SERVICE_READY_IN_MINUTES: "Service ready in min.",
        FTPStatusCode.DATA_CONNECTION_OPEN: "Data conn. open.",
        FTPStatusCode.FILE_STATUS_OK: "File status OK.",
        FTPStatusCode.COMMAND_OK: "Command OK.",
        FTPStatusCode.COMMAND_NOT_IMPLEMENTED: "Command not implemented.",
        FTPStatusCode.SYSTEM_STATUS: "Sys status.",
        FTPStatusCode.DIRECTORY_STATUS: "Dir status.",
        FTPStatusCode.FILE_STATUS: "File status.",
        FTPStatusCode.HELP_MESSAGE: "Help msg.",
        FTPStatusCode.NAME_SYSTEM_TYPE: "Sys type.",
        FTPStatusCode.SERVICE_READY_FOR_NEW_USER: "Ready for new user.",
        FTPStatusCode.SERVICE_CLOSING_CONTROL_CONNECTION: "Closing ctrl conn.",
        FTPStatusCode.DATA_CONNECTION_OPEN_NO_TRANSFER: "Data conn. open, no transfer.",
        FTPStatusCode.CLOSING_DATA_CONNECTION: "Closing data conn.",
        FTPStatusCode.ENTERING_PASSIVE_MODE: "Entering passive mode.",
        FTPStatusCode.USER_LOGGED_IN: "User logged in.",
        FTPStatusCode.REQUESTED_FILE_ACTION_OK: "File action OK.",
        FTPStatusCode.PATHNAME_CREATED: "Pathname created.",
        FTPStatusCode.USER_NAME_OK_NEED_PASSWORD: "Username OK, need password.",
        FTPStatusCode.NEED_ACCOUNT_FOR_LOGIN: "Need account for login.",
        FTPStatusCode.REQUESTED_FILE_ACTION_PENDING: "Action pending.",
        FTPStatusCode.SERVICE_NOT_AVAILABLE: "Service not available.",
        FTPStatusCode.CANT_OPEN_DATA_CONNECTION: "Can't open data conn.",
        FTPStatusCode.CONNECTION_CLOSED_TRANSFER_ABORTED: "Conn closed.",
        FTPStatusCode.FILE_UNAVAILABLE: "File unavailable.",
        FTPStatusCode.LOCAL_ERROR_IN_PROCESSING: "Local error.",
        FTPStatusCode.INSUFFICIENT_STORAGE_SPACE: "Insufficient storage.",
        FTPStatusCode.SYNTAX_ERROR_COMMAND_UNRECOGNIZED: "Syntax error.",
        FTPStatusCode.SYNTAX_ERROR_IN_PARAMETERS: "Syntax error in params.",
        FTPStatusCode.BAD_SEQUENCE_OF_COMMANDS: "Bad cmd sequence.",
        FTPStatusCode.COMMAND_NOT_IMPLEMENTED_FOR_PARAMETER: "Command not implemented for param.",
        FTPStatusCode.NOT_LOGGED_IN: "Not logged in.",
        FTPStatusCode.NEED_ACCOUNT_FOR_STORING_FILES: "Need account for storing files",
        FTPStatusCode.REQUESTED_ACTION_NOT_TAKEN_FILE_UNAVAILABLE: "Action not taken, file unavailable.",
        FTPStatusCode.REQUESTED_ACTION_ABORTED_PAGE_TYPE_UNKNOWN: "Action aborted, unknown page type.",
        FTPStatusCode.REQUESTED_FILE_ACTION_ABORTED_EXCEEDED_STORAGE: "Action aborted, exceeded storage.",
        FTPStatusCode.REQUESTED_ACTION_NOT_TAKEN_FILE_NAME_NOT_ALLOWED: "Action not taken, name not allowed.",
        FTPStatusCode.PATH_NOT_DIRECTORY: "Path not directory.",
        FTPStatusCode.CHANGE_DIRECTORY_ACCEPTED: "Change directory accepted.",
        FTPStatusCode.FILE_EXISTS_ERROR: "File already exists.",
        FTPStatusCode.PERMISSION_DENIED: "Permission denied.",

    }
    return status_messages.get(code, "Unknown status code.")
