import functools
from typing import Callable, ParamSpec, TypeVar

from sqlmodel import Session

from models.model_utils import session_scope

P = ParamSpec("P")
R = TypeVar("R")


def transactional(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that injects a database session into the decorated function.
    
    If a 'session' argument is already provided (and is not None), it is used.
    Otherwise, a new session is created using `session_scope()`.
    
    The decorated function must accept a 'session' keyword argument.
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if kwargs.get("session") is not None:
            return func(*args, **kwargs)
        
        # If session is not provided, create a new one
        with session_scope() as session:
            kwargs["session"] = session
            return func(*args, **kwargs)
            
    return wrapper
