from distutils import extension
from xmlrpc.client import Boolean
from config import *

VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR = 0x00000001


def _supported(extensions, layers) -> bool:

    supported_extensions = set([extension.extensionName for extension in vkEnumerateInstanceExtensionProperties(None)])
    log.info(f"Supported Vulkan extensions: {supported_extensions}")
    sext = set(extensions)
    if not sext.issubset(supported_extensions):
        log.error(f"Unsupported extensions: {sext - supported_extensions}")
        return False

    supported_layers = set([layer.layerName for layer in vkEnumerateInstanceLayerProperties()])
    log.info(f"Supported Vulkan layers: {supported_layers}")
    slay = set(layers)
    if not slay.issubset(supported_layers):
        log.error(f"Unsupported layers: {slay - supported_layers}")
        return False

    return True


def make_instance(application_name):
    log.info(f"Creating Vulkan instance for \"{application_name}\"")

    version = vkEnumerateInstanceVersion()
    log.info(f"Vulkan variant {version >> 29} version: {VK_VERSION_MAJOR(version)}.{VK_VERSION_MINOR(version)}.{VK_VERSION_PATCH(version)}")

    # version = VK_MAKE_VERSION(1, 0, 0)
    application_info = VkApplicationInfo(
        pApplicationName=application_name,
        applicationVersion=version,
        pEngineName="Doing it the hard way",
        engineVersion=version,
        apiVersion=version,
    )

    flags = 0

    #
    # Extensions
    #
    extensions = glfw.get_required_instance_extensions()
    log.info(f"Required Vulkan GLFW extensions: {extensions}")

    if sys.platform == "darwin":
        # https://stackoverflow.com/questions/72789012/why-does-vkcreateinstance-return-vk-error-incompatible-driver-on-macos-despite
        flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR
        mac_extensions = [
            "VK_KHR_portability_enumeration",
            "VK_KHR_get_physical_device_properties2",
        ]
        log.info(f"Required Vulkan macOs extensions: {mac_extensions}")
        extensions += mac_extensions

    if SPOCK_DEBUG:
        extensions += [
            "VK_EXT_debug_report",
        ]

    #
    # Layers
    #
    layers = []

    if SPOCK_DEBUG:
        layers += ["VK_LAYER_KHRONOS_validation"]

    if not _supported(extensions, layers):
        return None

    log.info(f"Creating Vulkan instance: extensions={extensions}, layers={layers}, flags={flags}")

    create_info = VkInstanceCreateInfo(
        flags=flags,
        pApplicationInfo=application_info,
        enabledLayerCount=len(layers), ppEnabledLayerNames=layers,
        enabledExtensionCount=len(extensions), ppEnabledExtensionNames=extensions,
    )
    return vkCreateInstance(create_info, None)
