# File: global_effects_manager.py
# version: 1.0
#
# Summary:
#   Manages global effect layers by aggregating them into one list.
#   You can add or remove effect layers here and then import the aggregated list
#   in your scene base class so every scene automatically draws these effects.
#
# Usage:
#   from global_effects_manager import add_effect_layer, get_effect_layers
#
#   # In your initialization code:
#   add_effect_layer(SnowEffectLayer(num_flakes=80, color_name="white_on_black"))
#   add_effect_layer(RainEffectLayer(num_drops=60, color_name="blue_on_black", direction="down"))

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