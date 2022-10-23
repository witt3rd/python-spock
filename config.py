import logging
from rich.logging import RichHandler
#
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from vulkan import *
#

logging.basicConfig(
    level="NOTSET",
    format="[color violet]%(name)s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        rich_tracebacks=True,
        markup=True,
    )]
)
log = logging.getLogger("spock")

SPOCK_DEBUG = True
