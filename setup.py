import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

OPTIONS = {
    'build_exe': {       
        'includes' : [
            'modules'
        ],
        'path' : sys.path + ['playbook'],
        'include_files' : [
            'playbook/img'
        ]

    }
}

EXECUTABLES = [
    Executable('playbook/main.py', base=base)
]

setup(
    name="playbook",
    version="0.2",
    options = OPTIONS,
    executables = EXECUTABLES,

)
