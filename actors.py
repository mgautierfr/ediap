
class Actor:
    """Represent a actor"""
    def __init__(self, context):
        self.helper = None
        self.context = context

    def show_helper(self, index, namespace):
        pass

    def hide_helper(self):
        if self.helper is not None:
            self.context['canvas'].delete(self.helper[1])
        self.helper = None

    def update(self, namespace):
        pass

class Rectangle(Actor):
    def __init__(self, context, x, y, w, h):
        Actor.__init__(self, context)
        self.x, self.y, self.w, self.h = x, y, w, h

    def update(self, namespace):
        self.context['canvas'].coords(self.shape, *self.get_bounding_rect(state))
        if self.helper:
            index, helper = self.helper
            if index == 0:
                coords = self.get_x_helper_coords(namespace)
            if index == 1:
                coords = self.get_y_helper_coords(namespace)
            if index == 2:
                coords = self.get_w_helper_coords(namespace)
            if index == 3:
                coords = self.get_h_helper_coords(namespace)
            self.context['canvas'].coords(helper, *coords)
