import sys
import gtk
import time
import webkit

import pango

class OutputView(webkit.WebView):
    '''a class that represents the output widget of a conversation
    '''

    def __init__(self):
        webkit.WebView.__init__(self)


class Window(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_default_size(1024, 768)
        self.scroll = gtk.ScrolledWindow()
        self.output = OutputView()
        self.scroll.add(self.output)
        self.add(self.scroll)
        self.scroll.show_all()
        self.connect("key-press-event", self.on_key_press)
        self.connect('delete-event', gtk.main_quit)
        self.is_fullscreen = False

    def load(self, url):
        self.output.load_uri(url)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            window.fullscreen()
            self.is_fullscreen = False
        else:
            window.unfullscreen()
            self.is_fullscreen = True

    def on_key_press(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()
        elif event.keyval == gtk.keysyms.F11:
            self.toggle_fullscreen()
        elif event.keyval == ord('s') and event.state == gtk.gdk.CONTROL_MASK:
            self.take_screenshot()
        elif event.keyval == ord('p') and event.state == gtk.gdk.CONTROL_MASK:
            self.export_to_pdf()

    def _get_view_image(self):
        root = self.output.get_parent_window()
        rect = self.output.get_allocation()

        x = rect.x
        y = rect.y
        width = rect.width
        height = rect.height

        #width, height = self.output.size_request()

        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        pixbuf.get_from_drawable(root, root.get_colormap(), x, y, x, y, width, height)
        return pixbuf

    def take_screenshot(self, path=None):
        if path is None:
            path = time.strftime("%m%d%y-%H%M%S.png")

        pixbuf = self._get_view_image()
        pixbuf.save(path, "png", {})

    def export_to_pdf(self, path=None):
        if path is None:
            path = time.strftime("%m%d%y-%H%M%S.pdf")

        operation = gtk.PrintOperation()
        operation.set_export_filename(path)
        operation.connect("begin-print", self.__begin_print_cb)
        operation.connect("draw-page", self.__draw_page_cb)
        operation.run(gtk.PRINT_OPERATION_ACTION_EXPORT, self)

    def __begin_print_cb(self, operation, context, data=None):
        settings = operation.get_print_settings()
        pixbuf = self._get_view_image()
        rect = self.output.get_allocation()
        paper_size = gtk.paper_size_new_custom("custom", "custom",
             pixel_to_mm(rect.width),
             pixel_to_mm(rect.height), gtk.UNIT_MM)
        settings.set_paper_size(paper_size)

        page_setup = gtk.PageSetup()

        page_setup.set_top_margin(0, gtk.UNIT_POINTS)
        page_setup.set_bottom_margin(0, gtk.UNIT_POINTS)
        page_setup.set_left_margin(0, gtk.UNIT_POINTS)
        page_setup.set_right_margin(0, gtk.UNIT_POINTS)

        operation.set_default_page_setup(page_setup)
        settings.set_orientation
        operation.set_n_pages(1)

    def __draw_page_cb(self, operation, context, page_nr):
        cr = context.get_cairo_context()
        layout = context.create_pango_layout()
        pango_context = layout.get_context()

        pixbuf = self._get_view_image()
        cr.set_source_pixbuf(pixbuf,0,0)
        cr.paint()
        cr.show_layout(layout)

def pixel_to_mm(pixels, dpi=600):
    # empirically obtained :P
    return pixels / 2.9


window = Window()
window.load(sys.argv[1])
window.show()
gtk.main()
