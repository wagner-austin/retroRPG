# File: curses_frontend/scene_layer_base.py
# version: 1.0
#
# Summary:
#   Provides the base class for scene layers (plugin objects that know how to draw).
#   Each layer has a name, a z_index, and a .draw(renderer, dt, context) method.

class SceneLayer:
    """
    Base class for 'layer plugins'. Each layer knows:
      - self.name: a string identifying the layer
      - self.z_index: an integer controlling draw order
      - a .draw(renderer, dt, context) method to perform drawing.
    """
    def __init__(self, name, z_index=0):
        self.name = name
        self.z_index = z_index

    def draw(self, renderer, dt, context):
        """
        Subclasses should override this method.
        :param renderer: instance of your renderer (e.g., CursesGameRenderer)
        :param dt: a time delta or frame count for animations
        :param context: a game model or dictionary of data
        """
        pass
