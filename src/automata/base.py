"""Base class for cellular automata"""

from abc import ABC, abstractmethod


class CellularAutomaton(ABC):
    """Base class for cellular automaton implementations."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.reset()

    @abstractmethod
    def reset(self) -> None:
        """Reset the automaton to its initial state."""

    @abstractmethod
    def step(self) -> None:
        """Advance the simulation by one generation."""

    @abstractmethod
    def get_grid(self):
        """Return the current grid state for rendering."""

    @abstractmethod
    def handle_click(self, x: int, y: int) -> None:
        """Handle mouse click at grid position ``(x, y)``."""
