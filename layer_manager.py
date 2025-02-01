# FileName: layer_manager.py
# Summary: A simple manager for layer info (name, z-order, visibility).

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
        Add or update a layer.
        """
        for layer in self.layers:
            if layer.name == name:
                layer.z = z_order
                layer.visible = visible
                return
        self.layers.append(LayerInfo(name, z_order, visible))

    def get_layers_in_order(self):
        """
        Return the layers sorted by their z-order.
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
