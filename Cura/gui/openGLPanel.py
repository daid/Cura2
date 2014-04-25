import wx
import os
import sys

from wx import glcanvas
import OpenGL
#OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

"""
The OpenGLPanel is a tricky beast.

On Windows, most is fine and ok. We need to handle the EVT_ERASE_BACKGROUND to prevent flickering.

On Linux and MacOS we have the problem that we cannot draw normal widgets on top of a wx.GLCanvas.
    So we need to draw the OpenGL information to a background buffer, and render that buffer into a normal wxPanel.
"""


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
