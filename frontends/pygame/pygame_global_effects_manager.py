# FileName: pygame_global_effects_manager.py
# version: 1.0
# Summary: Manages global effect layers (e.g., weather) in Pygame. 
# Tags: effect, manager, pygame

# A global list of effect layers, e.g. SnowEffectLayer, RainEffectLayer
global_effect_layers = []

def add_effect_layer(layer):
    """Add an effect layer instance to the global list."""
    global_effect_layers.append(layer)

def remove_effect_layer(layer):
    """Remove an effect layer from the global list."""
    if layer in global_effect_layers:
        global_effect_layers.remove(layer)

def clear_effect_layers():
    """Clear all global effect layers."""
    global_effect_layers.clear()

def get_effect_layers():
    """Return the aggregated list of global effect layers."""
    return global_effect_layers
