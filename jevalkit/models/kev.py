"""KevModel adapter for the author's System One endpoint."""

from ._http import HttpDecisionModel


class KevModel(HttpDecisionModel):
    """Use the endpoint, media format and release declared in the model registry."""
