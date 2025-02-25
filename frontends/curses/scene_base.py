# File: curses_frontend/scene_base.py
# version: 1.1 (updated to include global effect layers)
#
# Summary:
#   Provides a base class for Scene objects that manage multiple SceneLayer plugins.
#   The get_layers() method now returns the scene's own layers plus any globally enabled effect layers.
from .global_effects_manager import get_effect_layers

class Scene:
    """
    A Scene manages one or more SceneLayer objects.
    """
    def __init__(self):
        self.layers = []  # Scene-specific layers

    def get_layers(self):
        """
        Return the list of SceneLayer objects that should be drawn.
        This includes the scene's own layers plus any global effect layers.
        """
        return self.layers + get_effect_layers()

    def handle_input(self, key):
        """
        Optional: Scenes can process input themselves.
        Return a new state, a choice, or None.
        """
        pass