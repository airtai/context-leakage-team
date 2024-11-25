from .context_leakage_black_box.context_leakage_black_box_config import (
    get_prompt as get_context_leakage_black_box_prompt,
)
from .context_leakage_classifier.context_leakage_classifier_config import (
    get_prompt as get_context_leakage_classifier_prompt,
)

__all__ = [
    "get_context_leakage_classifier_prompt",
    "get_context_leakage_black_box_prompt",
]
