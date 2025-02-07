# File: transitions_factory.py
# version: 1.0
#
# Summary:
#   Provides a factory function to create transition scenes.
#   This allows you to easily swap transitions, add new ones, or use themed transitions.
#
# Tags: transition, factory, plugin, scene

# Import your transition scene classes.
from .curses_scene_transition import CrossFadeTransitionScene
# If you create additional transitions, import them here.
# from .curses_scene_transition_alternate import AlternateTransitionScene

# A registry mapping keys (transition names) to transition scene classes.
TRANSITION_REGISTRY = {
    "crossfade": CrossFadeTransitionScene,
    # "alternate": AlternateTransitionScene,  # example for a future transition
}

def create_transition(transition_name, current_scene, next_scene, phase_duration=(1000, 1000), **kwargs):
    """
    Returns an instance of a transition scene based on the transition_name.
    If transition_name is not found in the registry, defaults to CrossFadeTransitionScene.
    
    Parameters:
        transition_name (str): The key identifying the transition.
        current_scene: The scene to transition from (e.g. HomeScene).
        next_scene: The scene to transition to (e.g. LoadScene).
        phase_duration (tuple): A tuple (phase1_duration, phase2_duration) defining the lengths
                                of the two phases of the transition.
        **kwargs: Any additional keyword arguments to pass to the transition's constructor.
        
    Returns:
        An instance of a transition scene.
    """
    transition_cls = TRANSITION_REGISTRY.get(transition_name, CrossFadeTransitionScene)
    return transition_cls(current_scene, next_scene, phase_duration=phase_duration, **kwargs)
