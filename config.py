import os
import subprocess

from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook

from libqtile.config import EzKey as Key
from libqtile.config import EzClick as Click, EzDrag as Drag
from libqtile.log_utils import logger

from qtile_utils import *


# Global settings
EDITOR = os.environ.get('EDITOR', 'emacsclient')
TERMINAL = 'gnome-terminal'

class Theme:
    colors = [
        "#007fcf",  # blue
        "#444444",  # grey
        "#333333",  # darker grey
        "#ee75df"   # pink
    ]

    bar = {
        'size': 26,
        'background': colors[2],
    }

    widget = {
        'font': 'DejaVu',
        'fontsize': 12,
        'background': bar['background'],
        'foreground': 'EEEEEE'
    }

    graph = {
        'background': bar['background'],
        'border_width': 0,
        'line_width': 2,
        'margin_x': 5,
        'margin_y': 5,
        'width': 50
    }

    groupbox = dict(widget)
    groupbox.update({
        'padding': 2,
        'borderwidth': 3,
        'inactive': '999999'
    })

    sep = {
        'background': bar['background'],
        'foreground': '444444',
        'height_percent': 75
    }

    systray = dict(widget)
    systray.update({
        'icon_size': 16,
        'padding': 3
    })


mod = 'mod4'

keys = [
    # Switch between windows in current stack pane
    Key('M-j', lazy.layout.down()),
    Key('M-k', lazy.layout.up()),

    # Move windows up or down in current stack
    Key('M-S-j', lazy.layout.shuffle_down()),
    Key('M-S-k', lazy.layout.shuffle_up()),

    # Switch window focus to other pane(s) of stack
    Key('M-<Tab>', lazy.layout.next()),

    # Swap panes of split stack
    # Key('M-S-<space>', lazy.layout.rotate()),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key('M-S-<Return>', lazy.layout.toggle_split()),

    # Window management and navigation
    Key('M-<grave>', lazy.screen.toggle_group()),
    Key('M-c',       lazy.window.kill()),
    Key('M-<Left>',  lazy.screen.prev_group(skip_managed=True)),
    Key('M-<Right>', lazy.screen.next_group(skip_managed=True)),

    Key('M-S-<Left>',  window_to_prev_group()),
    Key('M-S-<Right>', window_to_next_group()),

    Key('M-C-<space>', lazy.window.toggle_floating()),
    Key('M-s', lazy.window.toggle_fullscreen()),

    # Programs
    Key('M-a', lazy.spawn(TERMINAL)),
    Key('M-f', lazy.spawn('firefox')),
    Key('M-t', lazy.spawn('nautilus --no-desktop')),
    Key('M-e', lazy.spawn('emacsclient -c')),

    # Layouts
    Key('M-<space>',   lazy.next_layout()),
    Key('M-S-<space>', lazy.prev_layout()),
    Key('M-h', lazy.layout.decrease_ratio()),
    Key('M-l', lazy.layout.increase_ratio()),

    # Qtile
    Key('M-C-r',   lazy.restart()),
    Key('M-C-q',   lazy.shutdown()),
    Key('M-r',     lazy.spawn('rofi -show run')),
]

groups = [Group(i) for i in '1234567890']

for i in groups:
    keys += [
        Key('M-%s' % i.name, lazy.group[i.name].toscreen()),
        Key('M-S-%s' % i.name, lazy.window.togroup(i.name)),
    ]


layouts = [
    layout.MonadTall(name='xmonad'),
    layout.Max(name='full'),
    layout.Tile(name='tile'),
    layout.Stack(num_stacks=2),
]

widget_defaults = dict(
    font='DejaVu',
    fontsize=12,
    padding=2,
    background=Theme.colors[2]
)

widgets = [
    widget.GroupBox(disable_drag=True, highlight_method='block', **Theme.groupbox),
    widget.Sep(**Theme.sep),
    widget.CurrentLayout(**Theme.widget),
    widget.Sep(**Theme.sep),
    widget.Prompt(),
    widget.WindowName(**Theme.widget),
    widget.Systray(),
    widget.Clock(format='%a %d %b %H:%M', **Theme.widget),
    widget.TextBox(text=" ↯", foreground=Theme.colors[0], fontsize=14),
    widget.Battery(update_delay=15, **Theme.widget),
]

screens = [
    Screen(top=bar.Bar(widgets, **Theme.bar)),
]

# Drag floating layouts.
mouse = [
    Drag('M-<Button1>', lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag('M-<Button3>', lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click('M-<Button2>', lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating()
auto_fullscreen = True
focus_on_window_activation = 'smart'

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, github issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = 'LG3D'


# Hooks

class _is_floating:
    by_type = {'notification', 'toolbar', 'splash', 'dialog'}
    by_role = {'EventDialog', 'Msgcompose', 'Preferences'}
    by_name = set()

    def __call__(self, window):
        return (
            window.get_wm_transient_for()
            or window.get_wm_type() in self.by_type
            or window.get_wm_window_role() in self.by_role
            or window.get_name() in self.by_name
        )

is_floating = _is_floating()


@hook.subscribe.client_new
def set_floating(window):
    if is_floating(window.window):
        logger.error('Floating window')
        window.floating = True
        # screen = window.qtile.find_closest_screen(window.x, window.y)

        screen = window.qtile.currentScreen
        group = window.qtile.currentGroup

        window.togroup(group.name)
        width, height = window.getsize()

        dx = max(0, screen.width // 2 - width // 2)
        dy = max(0, screen.height // 2 - height // 2)
        window.tweak_float(x=screen.x, y=screen.y, dx=dx, dy=dy)


@hook.subscribe.startup_once
def startup_once():
    subprocess.Popen(['systemctl', '--user', 'restart', 'emacs', 'qxkb', 'redshift-gtk', 'ssh-agent'])
    subprocess.Popen(['xsetroot', '-solid', '#2980B9'])
    subprocess.Popen(['xmodmap', '~/.Xmodmap'])
