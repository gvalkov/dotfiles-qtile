from libqtile.command import lazy


def window_to_prev_group():
    @lazy.function
    def __inner(qtile):
        i = qtile.groups.index(qtile.currentGroup)
        if qtile.currentWindow and i != 0:
            group = qtile.groups[i - 1].name
            qtile.currentWindow.togroup(group)
    return __inner


def window_to_next_group():
    @lazy.function
    def __inner(qtile):
        i = qtile.groups.index(qtile.currentGroup)
        if qtile.currentWindow and i != len(qtile.groups):
            group = qtile.groups[i + 1].name
            qtile.currentWindow.togroup(group)
    return __inner
