from evdev import UInput, ecodes
import time

ui = UInput(
    {
        ecodes.EV_KEY: list(range(ecodes.KEY_ESC, ecodes.KEY_MICMUTE + 1))
    },
    name="Dictatr Keyboard",
)

SHIFT = ecodes.KEY_LEFTSHIFT

_LETTER_CODES = {
    'a': ecodes.KEY_A, 'b': ecodes.KEY_B, 'c': ecodes.KEY_C,
    'd': ecodes.KEY_D, 'e': ecodes.KEY_E, 'f': ecodes.KEY_F,
    'g': ecodes.KEY_G, 'h': ecodes.KEY_H, 'i': ecodes.KEY_I,
    'j': ecodes.KEY_J, 'k': ecodes.KEY_K, 'l': ecodes.KEY_L,
    'm': ecodes.KEY_M, 'n': ecodes.KEY_N, 'o': ecodes.KEY_O,
    'p': ecodes.KEY_P, 'q': ecodes.KEY_Q, 'r': ecodes.KEY_R,
    's': ecodes.KEY_S, 't': ecodes.KEY_T, 'u': ecodes.KEY_U,
    'v': ecodes.KEY_V, 'w': ecodes.KEY_W, 'x': ecodes.KEY_X,
    'y': ecodes.KEY_Y, 'z': ecodes.KEY_Z,
}

CHAR_MAP = {}

for ch, code in _LETTER_CODES.items():
    CHAR_MAP[ch] = (code, False)
    CHAR_MAP[ch.upper()] = (code, True)

CHAR_MAP.update({
    "1": (ecodes.KEY_1, False),
    "2": (ecodes.KEY_2, False),
    "3": (ecodes.KEY_3, False),
    "4": (ecodes.KEY_4, False),
    "5": (ecodes.KEY_5, False),
    "6": (ecodes.KEY_6, False),
    "7": (ecodes.KEY_7, False),
    "8": (ecodes.KEY_8, False),
    "9": (ecodes.KEY_9, False),
    "0": (ecodes.KEY_0, False),

    "!": (ecodes.KEY_1, True),
    "@": (ecodes.KEY_2, True),
    "#": (ecodes.KEY_3, True),
    "$": (ecodes.KEY_4, True),
    "%": (ecodes.KEY_5, True),
    "^": (ecodes.KEY_6, True),
    "&": (ecodes.KEY_7, True),
    "*": (ecodes.KEY_8, True),
    "(": (ecodes.KEY_9, True),
    ")": (ecodes.KEY_0, True),

    " ": (ecodes.KEY_SPACE, False),
    "\n": (ecodes.KEY_ENTER, False),
    "\t": (ecodes.KEY_TAB, False),

    ".": (ecodes.KEY_DOT, False),
    ",": (ecodes.KEY_COMMA, False),
    "?": (ecodes.KEY_SLASH, True),
    "/": (ecodes.KEY_SLASH, False),

    ";": (ecodes.KEY_SEMICOLON, False),
    ":": (ecodes.KEY_SEMICOLON, True),

    "'": (ecodes.KEY_APOSTROPHE, False),
    "\"": (ecodes.KEY_APOSTROPHE, True),

    "-": (ecodes.KEY_MINUS, False),
    "_": (ecodes.KEY_MINUS, True),

    "=": (ecodes.KEY_EQUAL, False),
    "+": (ecodes.KEY_EQUAL, True),

    "[": (ecodes.KEY_LEFTBRACE, False),
    "{": (ecodes.KEY_LEFTBRACE, True),

    "]": (ecodes.KEY_RIGHTBRACE, False),
    "}": (ecodes.KEY_RIGHTBRACE, True),

    "\\": (ecodes.KEY_BACKSLASH, False),
    "|": (ecodes.KEY_BACKSLASH, True),

    "<": (ecodes.KEY_COMMA, True),
    ">": (ecodes.KEY_DOT, True),

    "`": (ecodes.KEY_GRAVE, False),
    "~": (ecodes.KEY_GRAVE, True),
})


def tap(key):
    ui.write(ecodes.EV_KEY, key, 1)
    ui.syn()
    ui.write(ecodes.EV_KEY, key, 0)
    ui.syn()


def type_text(text):
    shifted = False

    def set_shift(need):
        nonlocal shifted
        if need == shifted:
            return
        ui.write(ecodes.EV_KEY, SHIFT, 1 if need else 0)
        ui.syn()
        shifted = need

    time.sleep(0.01)

    for ch in text:
        if ch not in CHAR_MAP:
            continue

        key, need_shift = CHAR_MAP[ch]

        set_shift(need_shift)
        ui.write(ecodes.EV_KEY, key, 1)
        ui.syn()
        ui.write(ecodes.EV_KEY, key, 0)
        ui.syn()
        time.sleep(0.005)

    if shifted:
        ui.write(ecodes.EV_KEY, SHIFT, 0)
        ui.syn()