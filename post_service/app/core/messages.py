class Messages:
    """
    Messages class to store all application messages.
    - Centralized location for all user-facing and internal messages.
    - Helps maintain consistency and reusability across the application.
    """
    DB_CONNECTION_SUCCESS = "Post service database connection established successfully"
    DB_CONNECTION_ERROR = "Database connection error"
    DB_CONNECTION_CLOSE = "Database connection closed successfully"
    DB_CONNECTION_CLOSE_ERROR = "Database connection close error"
    POST_CREATION_SUCCESS = "Post created successfully"
    POST_UPDATE_SUCCESS = "Post updated successfully"
    POST_DELETE_SUCCESS = "Post deleted successfully"
    POST_NOT_FOUND = "Post not found"
    POST_ALREADY_EXISTS = "Post already exists"
    POST_LIST_EMPTY = "Post list is empty"
    POST_LIST_SUCCESS = "Post list fetched successfully"
    POST_DETAILS_SUCCESS = "Post details fetched successfully"
    EMAIL_REQUIRED = "Email is required"
    PASSWORD_REQUIRED = "Password is required"
    POST_SIGN_IN_SUCCESS = "Post signed in successfully"
    INVALID_CREDENTIALS = "Invalid credentials"
    INVALID_TOKEN = "Auth token is invalid"
    TOKEN_REQUIRED = "Auth token is required"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "You are not allowed to access this resource"
    STATUS_DETAILS_SUCCESS = "Status details fetched successfully"
    STATUS_NOT_FOUND = "Status not found"
    INTERNAL_SERVER_ERROR = "Something went wrong, please try again later"
    NO_RECORDS = "No records found"

# Create a global instance of the Messages class
messages = Messages()