from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    NoReturn,
    Optional,
    Tuple,
    Union,
)

from .meta import cname
from .types import E, T


class _ResultMixin(ABC, Generic[T, E]):
    def __bool__(self) -> NoReturn:
        raise ValueError(
            f"{cname(self)} object cannot be evaluated as a boolean. This is"
            " probably a bug in your code. Make sure you are either"
            " explicitly checking for Err results or using one of the"
            f" `Result.unwrap*()` methods:  {self!r}"
        )

    @abstractmethod
    def err(self) -> Optional[E]:
        pass

    @abstractmethod
    def unwrap(self) -> T:
        pass

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        pass

    @abstractmethod
    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        pass


@dataclass(frozen=True)
class Ok(_ResultMixin[T, E]):
    _value: T

    @staticmethod
    def err() -> None:
        return None

    def ok(self) -> T:
        return self._value

    def unwrap(self) -> T:
        return self.ok()

    def unwrap_or(self, default: T) -> T:
        return self.ok()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.ok()


@dataclass(frozen=True)
class Err(_ResultMixin[T, E]):
    _error: E

    def err(self) -> E:
        return self._error

    def unwrap(self) -> NoReturn:
        raise self.err()

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self.err())


# The 'Result' return type is used to implement an error-handling model heavily
# influenced by that used by the Rust programming language
# (see https://doc.rust-lang.org/book/ch09-00-error-handling.html).
Result = Union[Ok[T, E], Err[T, E]]


def return_lazy_result(
    func: Callable[..., Result[T, E]]
) -> Callable[..., "_LazyResult[T, E]"]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> _LazyResult[T, E]:
        return _LazyResult(func, *args, **kwargs)

    return wrapper


class _LazyResult(_ResultMixin[T, E]):
    def __init__(
        self, func: Callable[..., Result[T, E]], *args: Any, **kwargs: Any
    ) -> None:
        self._func = func
        self._args: Tuple[Any, ...] = args
        self._kwargs: Dict[str, Any] = kwargs

        self._result: Optional[Result[T, E]] = None

    def result(self) -> Result[T, E]:
        if self._result is None:
            self._result = self._func(*self._args, **self._kwargs)
        return self._result

    def err(self) -> Optional[E]:
        return self.result().err()

    def unwrap(self) -> T:
        return self.result().unwrap()

    def unwrap_or(self, default: T) -> T:
        return self.result().unwrap_or(default)

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.result().unwrap_or_else(op)
