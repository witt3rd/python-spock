from config import *
#


def _debug_callback(*args):
    log.warn(f"Vulkan debug callback: {args}")
    return VK_FALSE


def create_callback(instance):

    log.info("Creating Vulkan debug report callback")

    create_info = VkDebugReportCallbackCreateInfoEXT(
        flags=VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT,
        pfnCallback=_debug_callback,
    )
    creation_fn = vkGetInstanceProcAddr(instance, "vkCreateDebugReportCallbackEXT")
    return creation_fn(instance, create_info, None)


def destroy_callback(instance, callback):
    log.info("Destroying Vulkan debug report callback")
    destroy_fn = vkGetInstanceProcAddr(instance, "vkDestroyDebugReportCallbackEXT")
    destroy_fn(instance, callback, None)
