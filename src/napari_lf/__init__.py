
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

try:
    from ._widgetLF import LFQWidget
except Exception:
    LFQWidget = None
