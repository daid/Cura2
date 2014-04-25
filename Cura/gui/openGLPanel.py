import wx
import os
import sys
import numpy

from wx import glcanvas
import OpenGL
#OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *

"""
The OpenGLPanel is a tricky beast.

On Windows, most is fine and ok. We need to handle the EVT_ERASE_BACKGROUND to prevent flickering.

On Linux and MacOS we have the problem that we cannot draw normal widgets on top of a wx.GLCanvas.
    So we need to draw the OpenGL information to a background buffer, and render that buffer into a normal wxPanel.
"""

if False:
    class OpenGLPanelBase(glcanvas.GLCanvas):
        def __init__(self, parent):
            attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8, 0)
            glcanvas.GLCanvas.__init__(self, parent, style=wx.WANTS_CHARS|wx.CLIP_CHILDREN, attribList = attribList)
            self._context = glcanvas.GLContext(self)

            wx.EVT_PAINT(self, self.__onPaint)
            wx.EVT_ERASE_BACKGROUND(self, self.__onEraseBackground)

        def __onEraseBackground(self, e):
            pass

        def __onPaint(self, e):
            wx.PaintDC(self) # Make a PaintDC, else the paint event will be called again.
            self.SetCurrent(self._context)
            self._onRender()
            glFlush()
            self.SwapBuffers()

        def _onRender(self):
            pass

        def _refresh(self):
            self.Refresh()
else:
    class RenderGLPanel(glcanvas.GLCanvas):
        def __init__(self, parent):
            self._parent = parent
            attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8, 0)
            glcanvas.GLCanvas.__init__(self, parent.GetParent(), style=wx.WANTS_CHARS|wx.CLIP_CHILDREN, attribList = attribList)
            self.SetSize((1, 1))
            self._context = glcanvas.GLContext(self)
            self._color_texture = None
            self._bitmap = None

            wx.EVT_PAINT(self, self.__onPaint)
            wx.EVT_ERASE_BACKGROUND(self, self.__onEraseBackground)

        def __onEraseBackground(self, e):
            pass

        def __onPaint(self, e):
            wx.PaintDC(self) # Make a PaintDC, else the paint event will be called again.

            self.SetCurrent(self._context)
            size = self._parent.GetSizeTuple()
            if self._color_texture is None:
                self._color_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self._color_texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
                glBindTexture(GL_TEXTURE_2D, 0)

                self._depth_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self._depth_texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, size[0], size[1], 0, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None)
                glBindTexture(GL_TEXTURE_2D, 0)

                self._fbo = glGenFramebuffers(1)
                glBindFramebuffer(GL_FRAMEBUFFER, self._fbo)
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._color_texture, 0)
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._depth_texture, 0)
                glBindFramebuffer(GL_FRAMEBUFFER, 0)
                self._fboSize = size

            if self._fboSize != size:
                glBindTexture(GL_TEXTURE_2D, self._color_texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
                glBindTexture(GL_TEXTURE_2D, 0)

                glBindTexture(GL_TEXTURE_2D, self._depth_texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, size[0], size[1], 0, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None)
                glBindTexture(GL_TEXTURE_2D, 0)

            glBindFramebuffer(GL_FRAMEBUFFER, self._fbo)
            self._parent._onRender()
            glFlush()
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glBindTexture(GL_TEXTURE_2D, self._color_texture)
            data = glGetTexImageub(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
            self._bitmap = wx.BitmapFromBufferRGBA(size[0], size[1], data)
            glBindTexture(GL_TEXTURE_2D, 0)
            self.SwapBuffers()
            self._parent.Refresh()

    class OpenGLPanelBase(wx.Panel):
        def __init__(self, parent):
            super(OpenGLPanelBase, self).__init__(parent, style=wx.WANTS_CHARS|wx.CLIP_CHILDREN)
            self._renderPanel = RenderGLPanel(self)

            wx.EVT_PAINT(self, self.__onPaint)
            wx.EVT_ERASE_BACKGROUND(self, self.__onEraseBackground)

        def __onEraseBackground(self, e):
            pass

        def __onPaint(self, e):
            dc = wx.BufferedPaintDC(self)
            if self._renderPanel._bitmap is not None:
                dc.DrawBitmap(self._renderPanel._bitmap, 0, 0)
                self._renderPanel._bitmap = None

        def _onRender(self):
            pass

        def _refresh(self):
            self._renderPanel.Refresh()

class OpenGLPanel(OpenGLPanelBase):
    def __init__(self, parent):
        super(OpenGLPanel, self).__init__(parent)
        self._refreshQueued = False
        self._idleCalled = False
        self._shownError = False

        wx.EVT_SIZE(self, self._onSize)
        wx.EVT_IDLE(self, self._onIdle)

    def _onSize(self, e):
        self.Layout()
        self._refresh()

    def _onIdle(self, e):
        self._idleCalled = True
        if self._refreshQueued:
            self._refreshQueued = False
            self._refresh()

    def queueRefresh(self):
        wx.CallAfter(self._queueRefresh)

    def _queueRefresh(self):
        if self._idleCalled:
            wx.CallAfter(self._refresh)
        else:
            self._refreshQueued = True

    def _onRender(self):
        self._idleCalled = False
        try:
            self.onRender()
        except:
            # When an exception happens, catch it and show a message box. If the exception is not caught the draw function bugs out.
            # Only show this exception once so we do not overload the user with popups.
            if not self._shownError:
                import traceback
                errStr = _("An error has occurred during the 3D view drawing.")
                tb = traceback.extract_tb(sys.exc_info()[2])
                errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]))
                for n in xrange(len(tb)-1, -1, -1):
                    locationInfo = tb[n]
                    errStr += "\n @ %s:%s:%d" % (os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
                traceback.print_exc()
                wx.CallAfter(wx.MessageBox, errStr, _("3D window error"), wx.OK | wx.ICON_EXCLAMATION)
                self._shownError = True

    def onRender(self):
        glClearColor(0.8, 0.8, 0.8, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
