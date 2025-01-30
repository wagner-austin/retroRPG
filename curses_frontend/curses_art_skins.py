# FileName: curses_art_skins.py
#
# version: 1.2
#
# Summary: Stores ASCII art or special graphics needed for titles, load screens, or decorative UI elements.
#
# Tags: art, ui

HEADER_ART = [
    "=== HEADER ART PLACEHOLDER ===",
    "You can replace this with your own artwork."
]

LOADING_ART = [
    "--- LOADING ART PLACEHOLDER ---",
    "You can replace this with your own artwork."
]

HOMESCREEN_ART = [
    "::: HOMESCREEN ART PLACEHOLDER :::",
    "You can replace this with your own artwork."
]

DECORATION = [
    "... DECORATION PLACEHOLDER ...",
    "You can replace this with your own artwork."
]

BANNER = [
    "~~~ BANNER PLACEHOLDER ~~~"
]

BORDERS = [
    "+++ BORDERS PLACEHOLDER +++"
]

MAIN_MENU_ART = [
    "     .       +  ':.  .      *              '            *  '",
    "                  '::._                                      ",
    "                    '._)                 * +              ' ",
    "                          .              .        |         ",
    "           .      o.               +            - o -.      ",
    " o'          '    .    /  .         o             |         ",
    "    .  *   '          /                         +           ",
    "   .                 *          '                      .    ",
    "                 .             .             .  .           ",
    "   *         .   .       .                   | '.           ",
    "  +          '+                .           - o -            ",
    "          .                                . |              ",
    "            '  '     ..                   +  .  . +.        ",
    "  .                              |          .-.             ",
    " '                 .'  * '     - o -         ) )            ",
    " +        '   .                   |          '-´         '  ",
    "                       +      .'                   '.       ",
    " .           .           o      .       . .      .          ",
    "                       '       . +~~                       .",
]

CROCODILE = [
    "                _ ___                /^^\ /^\  /^^\*",
    "    _          *@)@) \            ,,/ '`~`'~~ ', `\\.",
    "  _/o\\_ _ _ _/~`.`...'~\\        ./~~..,'`','',.,' '  ~:",
    " / `','.~,~.~  .   , . , ~|,   ,/ .,' , ,. .. ,,.   `,  ~\\*",
    "( ' *' _ '*`_  '  .    ,`\\*/ .' ..' '  `  `   `..  `,   \\*",
    "  V~ V~ V~ ~\\ `   ' .  '    , ' .,.,''`.,.''`.,.``. ',   \\_",
    "  _/\\ /\\ /\\ /\\_/, . ' ,   `*/\\_ `. `. '.,  \\*",
    "< ~ ~ '~`'~'`, .,  .   `_: ::: \\_ '      `*/ ::: \\_ `.,' . ',  \\_",
    "  \\ ' `_  '`_    _    ',/ _::_::_ \\ _    _/ _::_::_ \\   `.,'.,`., \\-,-,-,_,_,",
    "   `'~~ `'~~ `'~~ `'~~  \\_)(_)(_)/  `~~' \\_)(*)(*)/ ~'`\\*..*,.*,'*;*;*;*;*;"
]

# You can add more ASCII sets (like DRAGON_ART_1, etc.) here if you want them.
# For now, we keep this as the "skins" or "art data" file.

# Example of a dictionary-based "skin" approach:
DEFAULT_SKIN = {
    "main_menu_art": MAIN_MENU_ART,
    "border_color":  "UI_CYAN",
    "title_color":   "UI_WHITE_ON_BLUE",
}

CURRENT_SKIN = DEFAULT_SKIN  # Could be swapped out for e.g. WINTER_SKIN, HALLOWEEN_SKIN, etc.
