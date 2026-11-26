# ============================================================
# XION CONVERSATION CONTEXT
# ============================================================

_context = {
    "last_intent": None,
    "last_parameters": {},
    "last_response": None,

    # M5.3
    "pending_action": None,
    "pending_parameters": {},
}


def update_context(
    intent=None,
    parameters=None,
    response=None
):
    if intent is not None:
        _context["last_intent"] = intent

    if isinstance(parameters, dict):
        _context["last_parameters"] = parameters.copy()

    if response is not None:
        _context["last_response"] = str(response)


def get_context():
    return {
        "last_intent": _context["last_intent"],
        "last_parameters": _context["last_parameters"].copy(),
        "last_response": _context["last_response"],
        "pending_action": _context["pending_action"],
        "pending_parameters": _context["pending_parameters"].copy(),
    }


def get_last_intent():
    return _context["last_intent"]


def get_last_parameters():
    return _context["last_parameters"].copy()


# ============================================================
# M5.3 — PENDING ACTION
# ============================================================

def set_pending_action(action, parameters=None):
    _context["pending_action"] = action

    if isinstance(parameters, dict):
        _context["pending_parameters"] = parameters.copy()
    else:
        _context["pending_parameters"] = {}


def get_pending_action():
    return _context["pending_action"]


def get_pending_parameters():
    return _context["pending_parameters"].copy()


def clear_pending_action():
    _context["pending_action"] = None
    _context["pending_parameters"] = {}


def clear_context():
    _context["last_intent"] = None
    _context["last_parameters"] = {}
    _context["last_response"] = None

    # M5.3
    clear_pending_action()