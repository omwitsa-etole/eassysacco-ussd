from cx_Freeze import setup, Executable
import os

# Define the base (None for a console application, "Win32GUI" for a GUI application)
base = None

# List of files to include
include_files = [
    ('controllers.py', ''),
    ('modules.py', ''),
    ('models.py', ''),
    ('db.py', ''),
    ('daraja.py', ''),
    ('payment.py', ''),
    ('text.py', '')
]

# Define the setup parameters
setup(
    name="EasyUssd",
    version="0.1",
    description="Easy USSD",
    options={"build_exe": {"include_files": include_files}},
    executables=[Executable("main.py", base=base)]
)
