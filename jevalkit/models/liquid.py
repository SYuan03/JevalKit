"""Published liquid model adapter."""

from ._hf import HFSystemOne


class LiquidModel(HFSystemOne):
    """Use the released System One head and its registered input constraints."""
