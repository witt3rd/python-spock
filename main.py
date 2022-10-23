from config import *
import instance
import debug
#


class Engine:

    def __init__(self) -> None:

        log.info("Initializing Engine")

        self.window_width = 800
        self.window_height = 600
        self.title = "Spock Engine"

        self.build_glfw_window()
        self.make_instance()
        self.make_debug_report_callback()

        log.info("Fully initialized Engine")
        self.close()

    def build_glfw_window(self) -> None:

        log.info("Building GLFW Window")

        if not glfw.init():
            log.error("GLFW initialization failed")
            return

        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)

        self._window = glfw.create_window(self.window_width, self.window_height, self.title, None, None)
        if not self._window:
            log.error("GLFW window creation failed")
            glfw.terminate()
            return
        log.info(f"GLFW {self.window_width}x{self.window_height} window \"{self.title}\" created")

    def make_instance(self):
        self.instance = instance.make_instance(self.title)

    def make_debug_report_callback(self):
        if SPOCK_DEBUG:
            self.debug_report_callback = debug.create_callback(self.instance)

    def close(self):
        log.info("Closing GLFW Window")
        if SPOCK_DEBUG:
            debug.destroy_callback(self.instance, self.debug_report_callback)
        vkDestroyInstance(self.instance, None)
        glfw.destroy_window(self._window)
        glfw.terminate()


if __name__ == "__main__":
    engine = Engine()
