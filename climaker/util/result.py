"""
Rust-like Result object implementation.

Original Result docs: https://doc.rust-lang.org/std/result/enum.Result.html#method.unwrap_err

"""

from __future__ import annotations

from typing import Generic, TypeVar, Callable, cast


T = TypeVar('T')
E = TypeVar('E')

U = TypeVar('U')
F = TypeVar('F')

TT = TypeVar('TT')
EE = TypeVar('EE')


class Result(Generic[T, E]):

    _ok: _Option[T]
    _err: _Option[E]

    __slots__ = ('_ok', '_err')

    @classmethod
    def Ok(cls, value: T) -> Result[T, E]:  # noqa
        return cls._new(_Some(value), _Null())

    @classmethod
    def Err(cls, error: E) -> Result[T, E]:  # noqa
        return cls._new(_Null(), _Some(error))

    def __init__(self) -> None:
        raise RuntimeError('Do not instantiate a Result directly. '
                           'Use Ok(value) or Err(error) instead.')

    @classmethod
    def _new(cls, ok: _Option[TT], err: _Option[EE]) -> Result[TT, EE]:
        assert ok.is_some() ^ err.is_some()
        instance: Result[TT, EE] = cls.__new__(cls)
        instance._ok = ok
        instance._err = err
        return instance

    def is_ok(self) -> bool:
        return self._ok.is_some()

    def is_err(self) -> bool:
        return self._err.is_some()

    def expect(self, message: str) -> T:
        if self._ok.is_some():
            return self._ok.unwrap()

        raise ExpectedResultOk(message)

    def expect_err(self, message: str) -> E:
        if self._err.is_some():
            return self._err.unwrap()

        raise ExpectedResultErr(message)

    def unwrap(self) -> T:
        if self._ok.is_some():
            return self._ok.unwrap()

        raise UnwrapOkFailed(self._err.unwrap())

    def unwrap_err(self) -> E:
        if self._err.is_some():
            return self._err.unwrap()

        raise UnwrapErrFailed(self._ok.unwrap())

    def unwrap_or(self, optb: T) -> T:
        if self._ok.is_some():
            return self._ok.unwrap()

        return optb

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        if self._ok.is_some():
            return self._ok.unwrap()

        return op(self._err.unwrap())

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        if self._ok.is_some():
            return self._new(
                _Some(op(self._ok.unwrap())),
                self._err,
            )

        return self._new(_Null(), self._err)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        if self._err.is_some():
            return self._new(
                self._ok,
                _Some(op(self._err.unwrap())),
            )

        return self._new(self._ok, _Null())

    def __repr__(self) -> str:
        if self.is_ok():
            return f'Ok({self._ok.unwrap()!r})'
        else:
            return f'Err({self._err.unwrap()!r})'


Ok = Result.Ok
Err = Result.Err


class ResultException(Exception):
    pass


class ExpectedResultOk(ResultException):
    pass


class ExpectedResultErr(ResultException):
    pass


class UnwrapOkFailed(ResultException):
    pass


class UnwrapErrFailed(ResultException):
    pass


class _Option(Generic[T]):

    _is_null: bool
    _value: T

    __slots__ = ('_is_null', '_value')

    def __init__(self) -> None:
        raise RuntimeError('Do not instantiate an Option directly.'
                           'Use Null() or Some(value) instead.')

    @classmethod
    def Null(cls) -> _Option[T]:  # noqa
        return cls._new(True, cast(T, None))

    @classmethod
    def Some(cls, value: T) -> _Option[T]:  # noqa
        return cls._new(False, value)

    @classmethod
    def _new(cls, is_null: bool, value: T) -> _Option[T]:
        instance: _Option[T] = cls.__new__(cls)
        instance._is_null = is_null
        instance._value = value
        return instance

    def is_null(self) -> bool:
        return self._is_null

    def is_some(self) -> bool:
        return not self._is_null

    def unwrap(self) -> T:
        if self.is_some():
            return self._value
        raise _UnwrapSomeFailed()

    def unwrap_null(self) -> None:
        if self.is_null():
            return
        raise _UnwrapNullFailed(self._value)


_Null = _Option.Null
_Some = _Option.Some


class _OptionException(Exception):
    pass


class _UnwrapSomeFailed(_OptionException):
    pass


class _UnwrapNullFailed(_OptionException):
    pass
