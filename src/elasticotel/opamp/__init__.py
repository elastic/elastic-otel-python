from .version import __version__

_OTLP_HTTP_HEADERS = {
    "Content-Type": "application/x-protobuf",
    "User-Agent": "OTel-Opamp-Python/" + __version__,
}
