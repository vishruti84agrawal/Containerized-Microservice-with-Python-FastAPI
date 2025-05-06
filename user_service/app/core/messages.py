
class Messages:

    """
    Messages class to store all application messages.
    - Centralized location for all user-facing and internal messages.
    - Helps maintain consistency and reusability across the application.
    """
    DB_CONNECTION_SUCCESS = "User service database connection established successfully"
    DB_CONNECTION_ERROR = "Database connection error"
    DB_CONNECTION_CLOSE = "Database connection closed successfully"
    DB_CONNECTION_CLOSE_ERROR = "Database connection close error"
    USER_CREATION_SUCCESS = "User created successfully"
    USER_UPDATE_SUCCESS = "User updated successfully"
    USER_DELETE_SUCCESS = "User deleted successfully"
    USER_NOT_FOUND = "User not found"
    USER_ALREADY_EXISTS = "User email already exists"
    USER_LIST_EMPTY = "User list is empty"
    USER_LIST_SUCCESS = "User list fetched successfully"
    USER_DETAILS_SUCCESS = "User details fetched successfully"
    USER_ID_EMAIL_REQUIRED = "Either user ID or email is required"
    EMAIL_REQUIRED = "Email is required"
    PASSWORD_REQUIRED = "Password is required"
    USER_SIGN_IN_SUCCESS = "User signed in successfully"
    INVALID_CREDENTIALS = "Invalid credentials, either email or password is incorrect"
    INVALID_TOKEN = "Auth token is invalid"
    TOKEN_REQUIRED= "Auth token is required"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "You are unauthorized to access this resource"
    STATUS_DETAILS_SUCCESS = "Status details fetched successfully"
    STATUS_NOT_FOUND = "Status not found"
    INTERNAL_SERVER_ERROR = "Something went wrong, please try again later"
    NO_RECORDS = "No records found"

# Create a global instance of the Messages class
messages = Messages()