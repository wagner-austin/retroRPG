# FileName: play_runner.py
# version: 3.3
#
# Summary: Provides functions to load or build a GameModel & GameContext
#          for "play" or "editor" mode. Delegates the common logic to
#          map_model_builder.py so we don't duplicate code.
#
# Tags: play, runner, map

from map_model_builder import build_model_common

def build_model_for_play(filename_or_data, is_generated=False):
    """
    Loads map data (from filename or a provided dict) and returns
    (model, context) with context.mode_name = 'play'.
    
    :param filename_or_data: str (file in 'maps' dir) or dict
    :param is_generated: bool, center player if True
    :return: (GameModel, GameContext) or (None, None) on failure
    """
    return build_model_common(filename_or_data, is_generated, mode_name="play")

#def build_model_for_editor(filename_or_data, is_generated=False):
    """
    Loads map data (from filename or a provided dict) and returns
    (model, context) with context.mode_name = 'editor'.
    
    :param filename_or_data: str (file in 'maps' dir) or dict
    :param is_generated: bool, center player if True
    :return: (GameModel, GameContext) or (None, None) on failure
    """
 #   return build_model_common(filename_or_data, is_generated, mode_name="editor")