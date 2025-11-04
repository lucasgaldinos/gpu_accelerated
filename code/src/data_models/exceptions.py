"""
Custom exception hierarchy for problem loading errors.

This module defines domain-specific exceptions that provide clear error
messages and enable precise error handling throughout the problem loader
implementation.

Exception Hierarchy:
    Exception (built-in)
    └── ProblemLoaderError (base for all problem loader errors)
        ├── InstanceNotFoundError (instance doesn't exist in database)
        ├── InvalidEdgeTypeError (unsupported edge_weight_type)
        └── MissingCoordinatesError (coordinates required but NULL)

Design Philosophy:
- Explicit error types enable targeted exception handling
- Custom __init__ methods provide context-rich error messages
- All errors inherit from ProblemLoaderError for catch-all handling
- Error messages guide users toward solutions

Example Usage:
    >>> try:
    ...     with DatabaseLoader() as loader:
    ...         problem = loader.load('nonexistent')
    ... except InstanceNotFoundError as e:
    ...     print(f"Instance not found: {e.instance_name}")
    ... except ProblemLoaderError as e:
    ...     print(f"General loader error: {e}")
"""


class ProblemLoaderError(Exception):
    """
    Base exception for all problem loading errors.

    This base class allows catching all problem loader errors with a
    single except clause while still enabling specific error handling
    for derived exception types.

    Example:
        >>> try:
        ...     problem = load_problem('instance')
        ... except ProblemLoaderError:
        ...     # Catches all loader-related errors
        ...     print("Failed to load problem")
    """

    pass


class InstanceNotFoundError(ProblemLoaderError):
    """
    Raised when requested instance doesn't exist in database.

    This error indicates the instance name provided doesn't match any
    record in the problems table. Common causes:
    - Typo in instance name
    - Instance not yet imported into database
    - Case sensitivity mismatch

    Attributes:
        instance_name: The name that was not found

    Example:
        >>> raise InstanceNotFoundError('burma14')
        InstanceNotFoundError: Instance 'burma14' not found in database
    """

    def __init__(self, instance_name: str):
        self.instance_name = instance_name
        super().__init__(
            f"Instance '{instance_name}' not found in database. "
            f"Check instance name for typos or verify it's been imported."
        )


class InvalidEdgeTypeError(ProblemLoaderError):
    """
    Raised when edge_weight_type is not supported.

    This error occurs when the problem specifies an edge_weight_type that
    the distance computation module doesn't handle. Supported types are:
    - 'EUC_2D': Euclidean distance in 2D plane
    - 'GEO': Geographic distance (haversine)
    - 'ATT': Pseudo-Euclidean distance
    - 'EXPLICIT': Pre-computed distance matrix

    Attributes:
        edge_type: The unsupported edge type

    Example:
        >>> raise InvalidEdgeTypeError('CEIL_2D')
        InvalidEdgeTypeError: Unsupported edge_type: 'CEIL_2D'.
        Valid types: EUC_2D, GEO, ATT, EXPLICIT
    """

    def __init__(self, edge_type: str):
        self.edge_type = edge_type
        super().__init__(
            f"Unsupported edge_type: '{edge_type}'. "
            f"Valid types: EUC_2D, GEO, ATT, EXPLICIT"
        )


class MissingCoordinatesError(ProblemLoaderError):
    """
    Raised when coordinates are required but NULL in database.

    This error occurs when:
    - edge_weight_type requires coordinates (EUC_2D, GEO, ATT)
    - BUT coordinates in database are NULL

    This typically indicates a data integrity issue - the problem should
    either have coordinates OR use EXPLICIT edge_weight_type.

    Attributes:
        instance_name: Name of the problem instance
        edge_type: The edge type that requires coordinates

    Example:
        >>> raise MissingCoordinatesError('instance', 'EUC_2D')
        MissingCoordinatesError: Instance 'instance' has edge_type 'EUC_2D'
        but coordinates are NULL in database
    """

    def __init__(self, instance_name: str, edge_type: str):
        self.instance_name = instance_name
        self.edge_type = edge_type
        super().__init__(
            f"Instance '{instance_name}' has edge_type '{edge_type}' but "
            f"coordinates are NULL in database. This indicates a data integrity "
            f"issue - problem should either have coordinates or use EXPLICIT edge_type."
        )


class DatabaseConnectionError(ProblemLoaderError):
    """
    Raised when database connection fails.

    This error occurs when:
    - Database file doesn't exist
    - Database file is corrupted
    - Insufficient permissions to read database

    Attributes:
        db_path: Path to the database file that failed to connect
        original_error: The underlying exception that caused the failure

    Example:
        >>> raise DatabaseConnectionError('/path/to/db.duckdb', FileNotFoundError())
        DatabaseConnectionError: Failed to connect to database at '/path/to/db.duckdb'
    """

    def __init__(self, db_path: str, original_error: Exception):
        self.db_path = db_path
        self.original_error = original_error
        super().__init__(
            f"Failed to connect to database at '{db_path}': {original_error}"
        )


class InvalidProblemDataError(ProblemLoaderError):
    """
    Raised when database contains invalid or inconsistent problem data.

    This error occurs when data integrity checks fail:
    - Dimension doesn't match number of nodes
    - CVRP missing capacity or demands
    - Coordinates have wrong shape
    - ATSP missing distance matrix

    Attributes:
        instance_name: Name of the problem instance
        reason: Description of what's invalid

    Example:
        >>> raise InvalidProblemDataError('instance', 'dimension=52 but only 50 nodes found')
        InvalidProblemDataError: Invalid data for instance 'instance':
        dimension=52 but only 50 nodes found
    """

    def __init__(self, instance_name: str, reason: str):
        self.instance_name = instance_name
        self.reason = reason
        super().__init__(f"Invalid data for instance '{instance_name}': {reason}")
