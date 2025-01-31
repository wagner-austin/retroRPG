# FileName: engine_interfaces.py
# version: 1.1 (updated)
#
# Summary: Provides abstract interfaces for game rendering & input systems.
# Tags: interface, design

class IGameRenderer:
    def render(self, model):
        """
        Render the current state of the game model.
        Called after the game logic updates each frame.
        """
        pass

    def get_visible_size(self):
        """
        Return (visible_cols, visible_rows).
        For example, curses might say (max_w, max_h - top_offset).
        """
        return (80, 25)  # fallback or placeholder


class IGameInput:
    def get_actions(self):
        """
        Return a list of high-level action strings, e.g. ["MOVE_UP", "EDITOR_TOGGLE", "QUIT"].
        If no input is available, returns an empty list.
        """
        return []