from config import *
import instance
import debug
import device
#


class Engine:

    def __init__(self) -> None:
        log.info("Initializing Engine")

        self.window_width = 800
        self.window_height = 600
        self.title = "Spock Engine"

        self.build_glfw_window()
        self.make_instance()
        self.make_device()

        log.info("Fully initialized Engine")

        # glfw.make_context_current(self.window)

        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):
            # Render here, e.g. using pyOpenGL

            # Swap front and back buffers
            # glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

        self.close()

    def build_glfw_window(self) -> None:
        log.info("Building GLFW Window")

        if not glfw.init():
            log.error("GLFW initialization failed")
            return

        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)

        self.window = glfw.create_window(self.window_width, self.window_height, self.title, None, None)
        if not self.window:
            log.error("GLFW window creation failed")
            glfw.terminate()
            return

        log.info(f"GLFW {self.window_width}x{self.window_height} window \"{self.title}\" created")

    def make_instance(self):
        log.info("Creating Vulkan instance and surface")

        self.instance = instance.make_instance(self.title)
        if SPOCK_DEBUG:
            self.debug_report_callback = debug.create_callback(self.instance)
        c_style_surface = ffi.new("VkSurfaceKHR *")
        if glfw.create_window_surface(self.instance, self.window, None, c_style_surface) != VK_SUCCESS:
            raise RuntimeError("Failed to create window surface")
        self.surface = c_style_surface[0]

    def make_device(self):
        log.info("Creating Vulkan physical and logical devices with graphics queue")

        self.physical_device = device.choose_physical_device(self.instance)
        self.logical_device = device.create_logical_device(self.physical_device, self.instance, self.surface)
        [self.graphics_queue, self.present_queue] = device.get_queues(self.physical_device, self.logical_device, self.instance, self.surface)

    def close(self):
        log.info("Closing GLFW Window and cleaning up Vulkan")

        vkDestroyDevice(self.logical_device, None)
        destroy_surface_fn = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")
        destroy_surface_fn(self.instance, self.surface, None)
        if SPOCK_DEBUG:
            debug.destroy_callback(self.instance, self.debug_report_callback)
        vkDestroyInstance(self.instance, None)
        glfw.destroy_window(self.window)
        glfw.terminate()


if __name__ == "__main__":
    engine = Engine()
