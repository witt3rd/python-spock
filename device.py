from config import *


class QueueFamilyIndices:

    def __init__(self):
        self.graphics_family = None
        self.present_family = None

    def is_complete(self):
        return self.graphics_family is not None and self.present_family is not None


def _device_type_str(device_type):
    if device_type == VK_PHYSICAL_DEVICE_TYPE_OTHER:
        return "Other"
    elif device_type == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU:
        return "Integrated GPU"
    elif device_type == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
        return "Discrete GPU"
    elif device_type == VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU:
        return "Virtual GPU"
    elif device_type == VK_PHYSICAL_DEVICE_TYPE_CPU:
        return "CPU"
    else:
        return "Unknown"


def _log_device_properties(device):

    properties = vkGetPhysicalDeviceProperties(device)

    props = {}
    props["api_version"] = properties.apiVersion
    props["driver_version"] = properties.driverVersion
    props["vendor_id"] = properties.vendorID
    props["device_id"] = properties.deviceID
    props["device_type"] = _device_type_str(properties.deviceType)
    props["device_name"] = properties.deviceName
    props["pipeline_cache_uuid"] = properties.pipelineCacheUUID

    log.info(f"Vulkan device properties: {props}")


def _check_device_extension_support(device, extensions) -> bool:

    available_extensions = vkEnumerateDeviceExtensionProperties(device, None)

    available_extension_names = set([extension.extensionName for extension in available_extensions])
    log.info(f"Available Vulkan device extensions: {available_extension_names}")

    exts = set(extensions)
    if not exts.issubset(available_extension_names):
        log.error(f"Unsupported Vulkan device extensions: {exts - available_extension_names}")
        return False

    return True


def _is_suitable(device) -> bool:

    requested_extensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME,
    ]
    log.info(f"Required Vulkan device extensions: {requested_extensions}")
    return _check_device_extension_support(device, requested_extensions)


def choose_physical_device(instance):

    log.info("Choosing Vulkan physical device")

    physical_devices = vkEnumeratePhysicalDevices(instance)

    if len(physical_devices) == 0:
        raise RuntimeError("Failed to find GPUs with Vulkan support")

    for device in physical_devices:
        if SPOCK_DEBUG:
            _log_device_properties(device)
        if _is_suitable(device):
            return device

    raise RuntimeError("Failed to find a suitable Vulkan GPU")


def find_queue_families(device, instance, surface):

    log.info("Finding Vulkan queue families")

    indices = QueueFamilyIndices()

    surface_support_fn = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")

    queue_families = vkGetPhysicalDeviceQueueFamilyProperties(device)
    for i, queue_family in enumerate(queue_families):
        if not queue_family.queueCount > 0:
            continue

        if queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT:
            indices.graphics_family = i
            log.info(f"Found suitable Vulkan graphics queue family: {i}")

        if surface_support_fn(device, i, surface):
            indices.present_family = i
            log.info(f"Found suitable Vulkan present queue family: {i}")

        if indices.is_complete():
            return indices

    raise RuntimeError("Failed to find suitable Vulkan queue family")


def create_logical_device(physical_device, instance, surface):

    log.info("Creating Vulkan logical device")

    indices = find_queue_families(physical_device, instance, surface)

    uniq_indices = set([indices.graphics_family, indices.present_family])

    queue_create_infos = [
        VkDeviceQueueCreateInfo(
            queueFamilyIndex=queue_family,
            queueCount=1,
            pQueuePriorities=[1.0, ],
        ) for queue_family in uniq_indices
    ]

    device_features = VkPhysicalDeviceFeatures()

    enaabled_layers = []
    if SPOCK_DEBUG:
        enaabled_layers.append("VK_LAYER_KHRONOS_validation")

    enabled_extensions = []
    if sys.platform == 'darwin':
        enabled_extensions.append("VK_KHR_portability_subset")

    create_info = VkDeviceCreateInfo(
        queueCreateInfoCount=len(queue_create_infos),
        pQueueCreateInfos=queue_create_infos,
        pEnabledFeatures=[device_features, ],
        enabledExtensionCount=len(enabled_extensions),
        ppEnabledExtensionNames=enabled_extensions,
        enabledLayerCount=len(enaabled_layers),
        ppEnabledLayerNames=enaabled_layers,
    )

    device = vkCreateDevice(physical_device, create_info, None)
    if device is None:
        raise RuntimeError("Failed to create Vulkan logical device")

    return device


def get_queues(physical_device, logical_device, instance, surface):

    log.info("Getting Vulkan queue")

    indices = find_queue_families(physical_device, instance, surface)

    return [
        vkGetDeviceQueue(logical_device, indices.graphics_family, 0),
        vkGetDeviceQueue(logical_device, indices.present_family, 0),
    ]
