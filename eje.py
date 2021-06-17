"""Tornado and Systemd utilities."""


import ssl as _ssl

from asyncio import get_event_loop as _get_event_loop
from logging import getLogger as _get_logger  # noqa: N813

from socket import (  # noqa: N812
    gaierror as GAIError,
    socket as _Socket,
)

from typing import (
    Any,
    Optional,
)


from pkg_resources import resource_filename as _resource_filename
from tornado.concurrent import Future
from tornado.httpserver import HTTPServer as _HTTPServer
from tornado.tcpserver import TCPServer as _TCPServer

from tornado.web import (
    Application,
    RequestHandler as _RequestHandler,
)


_LOGGER = _get_logger(__name__)


def _bind_to_managed_port(server: _TCPServer):
    try:
        systemd_socket = _Socket(fileno=3)

    except OSError:
        server.listen(0)

    else:
        systemd_socket.setblocking(False)
        server.add_socket(systemd_socket)


def _listen_to(server: _TCPServer, port=None):
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
    app_name: str = "Server",
    port: Optional[int] = None,
    certificate_path=None,
    private_key_path=None,
):
    """Start a server to serve an app at the specified port.

    :param app: A :class:`tornado.web.Application` instance.
    :param app_name: The name of the application.
    :param port: The port where the application will be listening on.

    :param certificate_path:
        Path to the public TLS certificate of the application.

    :param private_key_path: Path to the application private TLS key.

    :raises GAIError:  # noqa: DAR402
        if there is a problem listening to the specified port.
    """
    ssl_context = _make_ssl_context(certificate_path, private_key_path)
    server = _HTTPServer(app, ssl_options=ssl_context)
    _listen_to(server, port)

    ports = [s.getsockname()[1] for s in server._sockets.values()]
    _LOGGER.info("Listening on %s", ports)

    try:
        loop = _get_event_loop()
        loop.call_soon(_LOGGER.info, "%s started!", app_name)
        loop.run_forever()

    except KeyboardInterrupt:
        _LOGGER.info("%s stopped.", app_name)


class RenderFromModuleHandler(_RequestHandler):
    """Provides a render method that picks up templates from modules."""

    def render_from_module(
        self, module_name, template_name: str, **kwargs: Any
    ) -> "Future[None]":
        """Render a template from a module.

        :param module_name:
            Name of the module from which to render the template.

        :param template_name: File name of the template to render.
        :param kwargs: Keyword arguments to be passed to the template.
        :return: ``None`` wrapped in a future.
        """
        template_path = _resource_filename(module_name, template_name)
        return self.render(template_path, **kwargs)
