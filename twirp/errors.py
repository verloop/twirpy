from enum import Enum

class Errors(Enum):
    Canceled = "canceled"
    Unknown = "unknown"
    InvalidArgument = "invalid_argument"
    DeadlineExceeded = "deadline_exceeded"
    NotFound = "not_found"
    BadRoute = "bad_route"
    AlreadyExists = "already_exists"
    PermissionDenied = "permission_denied"
    Unauthenticated = "unauthenticated"
    ResourceExhausted = "resource_exhausted"
    FailedPrecondition = "failed_precondition"
    Aborted = "aborted"
    OutOfRange = "out_of_range"
    Unimplemented = "unimplemented"
    Internal = "internal"
    Unavailable = "unavailable"
    DataLoss = "data_loss"
    Malformed = "malformed"
    NoError = ""

    @staticmethod
    def get_status_code(code):
        return {
            Errors.Canceled: 408,
            Errors.Unknown: 500,
            Errors.InvalidArgument: 400,
            Errors.Malformed: 400,
            Errors.DeadlineExceeded: 408,
            Errors.NotFound: 404,
            Errors.BadRoute: 404,
            Errors.AlreadyExists: 409,
            Errors.PermissionDenied: 403,
            Errors.Unauthenticated: 401,
            Errors.ResourceExhausted: 429,
            Errors.FailedPrecondition: 412,
            Errors.Aborted: 409,
            Errors.OutOfRange: 400,
            Errors.Unimplemented: 501,
            Errors.Internal: 500,
            Errors.Unavailable: 503,
            Errors.DataLoss: 500,
            Errors.NoError: 200,
        }.get(code, 500)

