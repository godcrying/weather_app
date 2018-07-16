import gi
import cairo
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf


class TransparentWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_border_width(0)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.stick()

        self.enable_drag = 1
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drag_handle = self.connect("button-press-event", self.start_drag)

        self.is_support_alpha = self.support_alpha()
        self.connect("draw", self.expose_draw)

    def support_alpha(self):
        '''
        是否支持透明
        '''
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is None:
            return False
        else:
            self.set_visual(visual)
            return True

    def expose_draw(self, wdiget, event, userdata=None):
        '''
        绘制透明窗口
        '''
        cr = Gdk.cairo_create(self.get_window())
        if self.is_support_alpha:
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
        else:
            cr.set_source_rgba(1.0, 1.0, 1.0)

        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        # 这里return False是为了阻止其他handler对信号的捕捉
        return False

    def start_drag(self, widget, event, userdata=None):
        '''
        实现窗口移动
        '''
        if self.enable_drag == 1 and event.button == 1:
            self.begin_move_drag(event.button,
                                 event.x_root, event.y_root,
                                 event.time)

    def toggle_lock(self, widget):
        '''
        控制是否可以拖拽
        '''
        if self.enable_drag:
            self.enable_drag = 0
            widget.set_label("Unlock")
        else:
            self.enable_drag = 1
            widget.set_label("Lock")
