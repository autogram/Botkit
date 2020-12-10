"""
This type stub file was generated by pyright.
"""

import asyncio
from . import mock

"""
Module ``selector``
-------------------

Mock of :mod:`selectors` and compatible objects performing asynchronous IO.

This module provides classes to mock objects performing IO (files, sockets,
etc). These mocks are compatible with :class:`~asynctest.TestSelector`, which
can simulate the behavior of a selector on the mock objects, or forward actual
work to a real selector.
"""
class FileDescriptor(int):
    """
    A subclass of int which allows to identify the virtual file-descriptor of a
    :class:`~asynctest.FileMock`.

    If :class:`~asynctest.FileDescriptor()` without argument, its value will be
    the value of :data:`~FileDescriptor.next_fd`.

    When an object is created, :data:`~FileDescriptor.next_fd` is set to the
    highest value for a :class:`~asynctest.FileDescriptor` object + 1.
    """
    next_fd = ...
    def __new__(cls, *args, **kwargs):
        ...
    
    def __hash__(self) -> int:
        ...
    


def fd(fileobj):
    """
    Return the :class:`~asynctest.FileDescriptor` value of ``fileobj``.

    If ``fileobj`` is a :class:`~asynctest.FileDescriptor`, ``fileobj`` is
    returned, else ``fileobj.fileno()``  is returned instead.

    Note that if fileobj is an int, :exc:`ValueError` is raised.

    :raise ValueError: if ``fileobj`` is not a :class:`~asynctest.FileMock`,
                       a file-like object or
                       a :class:`~asynctest.FileDescriptor`.
    """
    ...

def isfilemock(obj):
    """
    Return ``True`` if the ``obj`` or ``obj.fileno()`` is
    a :class:`asynctest.FileDescriptor`.
    """
    ...

class FileMock(mock.Mock):
    """
    Mock a file-like object.

    A FileMock is an intelligent mock which can work with TestSelector to
    simulate IO events during tests.

    .. method:: fileno()

        Return a :class:`~asynctest.FileDescriptor` object.
    """
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class SocketMock(FileMock):
    """
    Mock a socket.

    See :class:`~asynctest.FileMock`.
    """
    def __init__(self, side_effect=..., return_value=..., wraps=..., name=..., spec_set=..., parent=..., **kwargs) -> None:
        ...
    


if ssl:
    class SSLSocketMock(SocketMock):
        """
        Mock a socket wrapped by the :mod:`ssl` module.

        See :class:`~asynctest.FileMock`.

        .. versionadded:: 0.5
        """
        def __init__(self, side_effect=..., return_value=..., wraps=..., name=..., spec_set=..., parent=..., **kwargs) -> None:
            ...
        
    
    
def set_read_ready(fileobj, loop):
    """
    Schedule callbacks registered on ``loop`` as if the selector notified that
    data is ready to be read on ``fileobj``.

    :param fileobj: file object or :class:`~asynctest.FileMock` on which the
                    event is mocked.

    :param loop: :class:`asyncio.SelectorEventLoop` watching for events on
                 ``fileobj``.

    ::

        mock = asynctest.SocketMock()
        mock.recv.return_value = b"Data"

        def read_ready(sock):
            print("received:", sock.recv(1024))

        loop.add_reader(mock, read_ready, mock)

        set_read_ready(mock, loop)

        loop.run_forever() # prints received: b"Data"

    .. versionadded:: 0.4
    """
    ...

def set_write_ready(fileobj, loop):
    """
    Schedule callbacks registered on ``loop`` as if the selector notified that
    data can be written to ``fileobj``.

    :param fileobj: file object or  :class:`~asynctest.FileMock` on which th
        event is mocked.
    :param loop: :class:`asyncio.SelectorEventLoop` watching for events on
        ``fileobj``.

    .. versionadded:: 0.4
    """
    ...

class TestSelector(selectors._BaseSelectorImpl):
    """
    A selector which supports IOMock objects.

    It can wrap an actual implementation of a selector, so the selector will
    work both with mocks and real file-like objects.

    A common use case is to patch the selector loop::

        loop._selector = asynctest.TestSelector(loop._selector)

    :param selector: optional, if provided, this selector will be used to work
                     with real file-like objects.
    """
    def __init__(self, selector=...) -> None:
        ...
    
    def register(self, fileobj, events, data=...):
        """
        Register a file object or a :class:`~asynctest.FileMock`.

        If a real selector object has been supplied to the
        :class:`~asynctest.TestSelector` object and ``fileobj`` is not
        a :class:`~asynctest.FileMock` or a :class:`~asynctest.FileDescriptor`
        returned by :meth:`FileMock.fileno()`, the object will be registered to
        the real selector.

        See :meth:`selectors.BaseSelector.register`.
        """
        ...
    
    def unregister(self, fileobj):
        """
        Unregister a file object or a :class:`~asynctest.FileMock`.

        See :meth:`selectors.BaseSelector.unregister`.
        """
        ...
    
    def modify(self, fileobj, events, data=...):
        """
        Shortcut when calling :meth:`TestSelector.unregister` then
        :meth:`TestSelector.register` to update the registration of a an object
        to the selector.

        See :meth:`selectors.BaseSelector.modify`.
        """
        ...
    
    def select(self, timeout=...):
        """
        Perform the selection.

        This method is a no-op if no actual selector has been supplied.

        See :meth:`selectors.BaseSelector.select`.
        """
        ...
    
    def close(self):
        """
        Close the selector.

        Close the actual selector if supplied, unregister all mocks.

        See :meth:`selectors.BaseSelector.close`.
        """
        ...
    


def get_registered_events(selector):
    ...

if hasattr(asyncio, "format_helpers"):
    ...
else:
    ...
def fail_on_before_test_active_selector_callbacks(case):
    ...

def fail_on_active_selector_callbacks(case):
    ...
