import re

from distress_core.escalation.base import EscalationTrigger, TriggerContext

_NEGATION_WORDS = (
    "not",
    "no",
    "never",
    "nothing",
    "nobody",
    "nowhere",
    "none",
    "neither",
    "nor",
    "cannot",
    "dont",
    "doesnt",
    "didnt",
    "cant",
    "couldnt",
    "wont",
    "wouldnt",
    "shouldnt",
    "isnt",
    "arent",
    "wasnt",
    "werent",
    "havent",
    "hasnt",
    "hadnt",
    "aint",
)

NEGATION_PATTERN = re.compile(
    r"\b(?:"
    + "|".join(_NEGATION_WORDS)
    + r")\b"  # whole words, incl. contractions typed without an apostrophe
    r"|\b\w+n['’]t\b",  # any contraction with an apostrophe: don't, can’t
    re.IGNORECASE,
)


class NegationTrigger(EscalationTrigger):
    """Escalates when the raw text contains a negation.

    The fast model is a bag of words: it sees "not" and "okay", but not that
    one modifies the other.
    """

    name = "negation"

    def should_escalate(self, ctx: TriggerContext) -> bool:
        return NEGATION_PATTERN.search(ctx.raw_text) is not None
