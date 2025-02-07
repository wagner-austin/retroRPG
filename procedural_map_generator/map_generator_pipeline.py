# FileName: map_generator_pipeline.py
# version: 1.0
#
# Summary: Single pipeline that generates a brand-new procedural map and
#          builds a fully layered model ready for play.
#
# Explanation:
#   This module provides a single helper function to generate a map (via
#   generator.py) and immediately convert it to a layered model with
#   build_model_common. This ensures there's one consistent place
#   to handle map generation + layering.

from procedural_map_generator.generator import generate_procedural_map
from map_model_builder import build_model_common

def create_procedural_model(width=100, height=100, mode_name="play"):
    """
    Generate a brand-new procedural map (flat data) and immediately build
    a fully-layered GameModel. Returns (model, context).
    """
    # 1) Generate flat map data
    raw_data = generate_procedural_map(width, height)

    # 2) Convert it to a layered model and context
    model, context = build_model_common(raw_data, is_generated=True, mode_name=mode_name)

    return model, context
