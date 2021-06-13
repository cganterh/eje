"""Tornado and Systemd utilities."""


import ssl as _ssl

from logging import getLogger as _get_logger  # noqa: N813

from socket import (  # noqa: N812
    gaierror as GAIError,
    socket as _Socket,
)

from typing import Optional


from tornado.httpserver import HTTPServer as _HTTPServer
from tornado.tcpserver import TCPServer
from tornado.web import Application


_LOGGER = _get_logger(__name__)


def _bind_to_managed_port(server: TCPServer):
    try:
        systemd_socket = _Socket(fileno=3)

    except OSError:
        server.listen(0)

    else:
        systemd_socket.setblocking(False)
        server.add_socket(systemd_socket)


def _listen_to(server: TCPServer, port=None):
    try:
        server.listen(port)

    except GAIError:
        if port is None:  # noqa: SIM106
            _bind_to_managed_port(server)

        else:
            raise


def _make_ssl_context(certificate_path, private_key_path):
    if certificate_path is None or private_key_path is None:
        return None

    else:
        ssl_context = _ssl.create_default_context(_ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certificate_path, private_key_path)
        return ssl_context


def start_server(
    app: Application,
    port: Optional[int] = None,
    certificate_path=None,
    private_key_path=None,
):
    """Start a server to serve an app at the specified port.

    :param app: A :class:`tornado.web.Application` instance.

    :param port:
        A port number where the server will listen for connections.

    :raises GAIError:  # noqa: DAR402
        if there is a problem listening to the specified port.
    """
    ssl_context = _make_ssl_context(certificate_path, private_key_path)
    server = _HTTPServer(app, ssl_options=ssl_context)
    _listen_to(server, port)

    ports = [s.getsockname()[1] for s in server._sockets.values()]
    _LOGGER.info("Listening on %s", ports)
