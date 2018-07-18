#! /usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from urllib import request
from transparentwindow import TransparentWindow
from weatherforcasts import Weather


class WeatherBox(Gtk.Box):
    """
    weatherBox对象。data表示某一天的天气对象。
    """
    def __init__(self, weather_data):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.weather_data = weather_data
        self.weather_items = {}
        self.create_items()
        self.update_items()
        self.initUI()

    def initUI(self):
        for item in self.weather_items.values():
            self.pack_start(item, True, True, 0)

    def create_items(self):
        """
        生成天气基本结构
        """
        for key in self.weather_data.keys():
            if key == "wicon":
                self.weather_items[key] = Gtk.Image()
            else:
                self.weather_items[key] = Gtk.Label()

    def update_items(self):
        """
        更新天气内容
        """
        for key, value in self.weather_data.items():
            if key == "wicon":
                try:
                    with request.urlopen(value, timeout=20) as f:
                        img_data = f.read()
                except Exception as e:
                    raise e
                else:
                    img_loader = GdkPixbuf.PixbufLoader()
                    if img_loader.write(img_data):
                        img_loader.close()
                        pixbuf = img_loader.get_pixbuf()
                        if pixbuf is not None:
                            self.weather_items[key].set_from_pixbuf(pixbuf)
                    else:
                        img_loader.close()
            else:
                self.weather_items[key].set_label(value)


class MyWeatherApp(TransparentWindow):
    """
    继承透明窗口类
    """
    def __init__(self, title, weather):
        TransparentWindow.__init__(self)
        self.set_title(title)
        self.set_keep_below(True)

        self.mainbox = Gtk.Box(spacing=10)
        self.menu = Gtk.Menu()

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.enable_drag = 1

        self.weather = weather
        self.weatherboxs = []

        self.initUI()
        self.connect("destroy", Gtk.main_quit)

    def initUI(self):
        """
        生成界面
        """
        for forecast in self.weather.forecasts:
            self.weatherboxs.append(WeatherBox(forecast))
        for box in self.weatherboxs:
            self.mainbox.pack_start(box, True, True, 0)
        self.add(self.mainbox)

        self.init_menu()
        self.init_style()

        self.connect("button-press-event", self.on_button_press)

    def on_button_press(self, widget, event, userdata=None):
        '''
        实现窗口移动及右键菜单
        '''
        if event.button == 3:
            self.menu.popup_at_pointer(event)
            self.menu.show_all()

        if self.enable_drag == 1 and event.button == 1:
            self.get_toplevel().begin_move_drag(
                event.button,
                event.x_root,
                event.y_root,
                event.time)
        return True

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

    def init_menu(self):
        """
        初始化菜单
        """
        menu_item_lock = Gtk.MenuItem.new_with_label("Lock")
        menu_item_quit = Gtk.MenuItem.new_with_label("Quit")
        submenu_change_theme = Gtk.MenuItem.new_with_label("Change theme")

        menu_item_quit.connect("activate", self.window_quit)
        menu_item_lock.connect("activate", self.toggle_lock)

        """
        生成主题选择子菜单
        """
        submenu = Gtk.Menu()
        submenu_item_theme01 = Gtk.MenuItem.new_with_label("theme01")
        submenu_item_theme02 = Gtk.MenuItem.new_with_label("theme02")
        submenu_item_theme03 = Gtk.MenuItem.new_with_label("theme03")

        submenu.add(submenu_item_theme01)
        submenu.add(submenu_item_theme02)
        submenu.add(submenu_item_theme03)

        submenu_change_theme.set_submenu(submenu)

        self.menu.add(menu_item_lock)
        self.menu.add(submenu_change_theme)
        self.menu.add(menu_item_quit)

    def init_style(self):
        """
        设置CSS样式
        """
        self.default_style = b"""
            window label {
              color: #ffffff;
            }
            menu label{
              color: #000000;
            }
            """
        my_style_provider = Gtk.CssProvider()
        my_style_provider.load_from_data(self.default_style)
        """
        add_provider()只能改变当前widget的style，而且不能也改变其子元素的style
        所以只能用全局有效的add_provider_for_screen()
        """
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            my_style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def change_theme(self, widget, userdata=None):
        pass

    def update_weatherbox(self, userdata=None):
        try:
            self.weather.update_forecasts()
            for box in self.weatherboxs:
                box.update_items()
            print("Update successfully!!")
        except Exception as e:
            print("Update failed, wait for next update!!")
        finally:
            return True

    def window_quit(self, widget, userdata=None):
        Gtk.main_quit()


if __name__ == '__main__':
    try:
        weather = Weather("ASX", "yuncheng2.html")
        win = MyWeatherApp("weathers", weather)
    except Exception as e:
        print("Connection failed!!")
        exit(-1)
    else:
        timeoutid = GLib.timeout_add_seconds(60, win.update_weatherbox, None)
        win.show_all()
        Gtk.main()
