# FileName: layer_manager.py
# version: 1.1
# Summary: A simple manager for layer info (name, z-order, visibility).
# Tags: layers, manager

from layer_defs import (
    FLOOR_LAYER, ITEMS_LAYER, OBJECTS_LAYER, ENTITIES_LAYER,
    UI_HUD_LAYER, UI_MENU_LAYER
)

class LayerInfo:
    def __init__(self, name, z_order, visible=True):
        self.name = name
        self.z = z_order
        self.visible = visible

    def __repr__(self):
        return f"LayerInfo(name={self.name}, z={self.z}, visible={self.visible})"


class LayerManager:
    def __init__(self):
        self.layers = []

    def add_layer(self, name, z_order=0, visible=True):
        """
        Add or update a layer with the specified name, z-order, and visibility.
        """
        for layer in self.layers:
            if layer.name == name:
                layer.z = z_order
                layer.visible = visible
                return
        self.layers.append(LayerInfo(name, z_order, visible))

    def get_layers_in_order(self):
        """
        Return the layers sorted by their z-order (lowest z first).
        """
        return sorted(self.layers, key=lambda l: l.z)

    def set_visibility(self, layer_name, visible):
        """
        Toggle visibility of a given layer by name.
        """
        for layer in self.layers:
            if layer.name == layer_name:
                layer.visible = visible
                break

    def set_z_order(self, layer_name, new_z):
        """
        Change the z-order of a given layer by name.
        """
        for layer in self.layers:
            if layer.name == layer_name:
                layer.z = new_z
                break


# Create a global instance of LayerManager and define the layers.
layer_manager = LayerManager()

# Game layers with z=10..13
layer_manager.add_layer(FLOOR_LAYER,    z_order=10, visible=True)
layer_manager.add_layer(ITEMS_LAYER,    z_order=11, visible=True)
layer_manager.add_layer(OBJECTS_LAYER,  z_order=12, visible=True)
layer_manager.add_layer(ENTITIES_LAYER, z_order=13, visible=True)

# UI layers with z=100..101
layer_manager.add_layer(UI_HUD_LAYER,   z_order=100, visible=True)
layer_manager.add_layer(UI_MENU_LAYER,  z_order=101, visible=False)