from split_settings.tools import include


base_settings = [
    "base.py",
    "drf.py",
]


include(*base_settings)
