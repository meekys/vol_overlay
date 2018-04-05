import os
import ctypes
import ctypes.util
from ctypes import cdll, byref, Structure

os.environ["PYOPENGL_PLATFORM"] = "egl"

# monkeypatch ctypes to pick the right libraries... sigh.
def find_library(name):
    if name in ("GLESv2", "EGL"):
        return "/opt/vc/lib/lib%s.so" % name
    elif name == "GL":
        raise Exception()
    else:
        print(name)
        return old_find_library(name)
old_find_library = ctypes.util.find_library
ctypes.util.find_library = find_library

# Raspberry Pi libs are missing dependencies, we need GLES before EGL...
cdll.LoadLibrary("/opt/vc/lib/libGLESv2.so")

from OpenGL.GLES2 import *
from OpenGL.EGL import *
from OpenGL import arrays

DISPMANX_PROTECTION_NONE = 0

class VC_RECT_T(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int)]

    def __init__(self, x, y, width, height):
        self.x = c_int(x)
        self.y = c_int(y)
        self.width = c_int(width)
        self.height = c_int(height)

class EGL_DISPMANX_WINDOW_T(Structure):
    _fields_ = [
        ("element", c_int),
        ("width", c_int),
        ("height", c_int)]

    def __init__(self, element, width, height):
        self.element = c_int(element)
        self.width = c_int(width)
        self.height = c_int(height)

libbcm_host = cdll.LoadLibrary("libbcm_host.so")

class Display(object):

    def __init__(self, layer = 0):
        """Opens up the OpenGL library and prepares a window for display"""
        bcm = libbcm_host.bcm_host_init()
        assert bcm == 0

        self.display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
        assert self.display

        #major, minor = ctypes.c_long(), ctypes.c_long()
        #eglInitialize(self.display, byref(major), byref(minor))
        eglInitialize(self.display, None, None)

        attribute_list = arrays.GLintArray.asArray([
            EGL_RED_SIZE, 8,
            EGL_GREEN_SIZE, 8,
            EGL_BLUE_SIZE, 8,
            EGL_ALPHA_SIZE, 8,
            EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
            EGL_NONE])

        config = EGLConfig()
        num_configs = ctypes.c_long()
        eglChooseConfig(self.display, attribute_list, byref(config), 1, byref(num_configs))

        contextAttributes = arrays.GLintArray.asArray([
            EGL_CONTEXT_CLIENT_VERSION, 2,
            EGL_NONE
        ])
        self.context = eglCreateContext(self.display, config, EGL_NO_CONTEXT, contextAttributes)
        assert self.context != EGL_NO_CONTEXT

        self.init_nativewindow(layer)

        self.surface = eglCreateWindowSurface(self.display, config, byref(self.nativeWindow), None)
        assert self.surface != EGL_NO_SURFACE

        #eglBindAPI(EGL_OPENGL_ES_API)

        assert eglMakeCurrent(self.display, self.surface, self.surface, self.context)

    def init_nativewindow(self, layer):
        width = c_int()
        height = c_int()
        success = libbcm_host.graphics_get_display_size(0, byref(width), byref(height))
        assert success >= 0
        self.width = width.value
        self.height = height.value

        dispman_display = libbcm_host.vc_dispmanx_display_open(0)
        assert dispman_display
        dispman_update = libbcm_host.vc_dispmanx_update_start(0)
        assert dispman_update

        dst_rect = VC_RECT_T(0, 0, self.width, self.height)
        src_rect = VC_RECT_T(0, 0, self.width << 16, self.height << 16)
        #dst_rect = eglints( (0, 0, self.width, self.height))
        #src_rect = eglints( (0, 0, self.width << 16, self.height << 16))

        dispman_element = libbcm_host.vc_dispmanx_element_add(
            dispman_update,
            dispman_display,
            layer,
            byref(dst_rect),
            0,
            byref(src_rect),
            DISPMANX_PROTECTION_NONE,
            0,
            0,
            0)

        libbcm_host.vc_dispmanx_update_submit_sync(dispman_update)

        #libbcm_host.vc_dispmanx_display_close(dispman_display)

        self.nativeWindow = EGL_DISPMANX_WINDOW_T(dispman_element, self.width, self.height)

    def swapBuffers(self):
        eglSwapBuffers(self.display, self.surface)