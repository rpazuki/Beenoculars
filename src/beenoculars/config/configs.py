"""Configuartion/setting module.

   Notes:
   ------
       1- Configurations are readonly, and are stored in 'resource' folder.
       2- Setting are writable and are stored in users' data folder,
          dependening on the os.
"""
from __future__ import annotations

import os
import platform
import tomllib
from enum import Enum
from pathlib import Path

from addict import Dict as DefaultDict


class GUIFramework(str, Enum):
    TOGA = "TOGA"
    KIVY = "KIVY"
    UKNOWN = "UKNOWN"


class Dict(DefaultDict):
    def __missing__(self, key) -> None:
        # raise KeyError(key)
        # calling dict.unassinged properties return None
        return None


class _Dict(DefaultDict):
    def __missing__(self, key):
        raise KeyError(key)


class _Config(_Dict):

    @property
    def gui_framework(self) -> GUIFramework:
        if "framework" not in self or "framework.name" in self:
            return GUIFramework.UKNOWN

        return GUIFramework[self.framework.name.upper()]


config_file_path = os.path.join(os.path.dirname(__file__), 'config.toml')
with open(config_file_path, "rb") as f:
    __config = tomllib.load(f)
CONFIGS = _Config(**__config)

# Check the correct UI framework
if 'framework' not in CONFIGS:
    raise ValueError("The 'framework' entry is not defined in config.toml.")
if 'name' not in CONFIGS.framework:
    raise ValueError(
        "The 'name' entry is not defined in 'framework' config.toml.")
if CONFIGS.framework.name.upper() == "KIVY":
    try:
        import kivy  # noqa
    except ImportError:
        raise ValueError("The config.toml files set to 'kivy'.")
elif CONFIGS.framework.name.upper() == "TOGA":
    try:
        import toga  # noqa
    except ImportError:
        raise ValueError("The config.toml files set to 'toga'.")


class Settings(DefaultDict):
    __instance = None
    __is_changed = False
    __loading_path = ""

    def __init__(__self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def load(data_path) -> Settings:
        if Settings.__instance is None:
            try:

                with open(data_path / "beencocular_settings.toml", "rb") as f:
                    __setting = tomllib.load(f)
                    Settings.__loading_path = str(
                        data_path / "beencocular_settings.toml")

                    # Todo:Update thye default setting if new version
                    # has new entry.

                    Settings.__instance = Settings(**__setting)
                    Settings.__is_changed = False
            except FileNotFoundError:
                Path(data_path).mkdir(parents=True, exist_ok=True)
                from .tomllib_w import dumps

                ###################################
                # Define the default settings here
                default_conf = {'OverlayComponent':
                                {'is_gray': False,
                                 'is_bw': False,
                                 'contours_thickness': 4,
                                 'has_contour': False,
                                 'percentages': [90, 100],
                                 'threshold': 127}
                                }
                with open(data_path / "beencocular_settings.toml", "w") as f:
                    f.write(dumps(default_conf))
                    Settings.__loading_path = str(
                        data_path / "beencocular_settings.toml")
                Settings.__instance = Settings(**default_conf)
                Settings.__is_changed = False

        return Settings.__instance

    def __setitem__(self, name, value):
        Settings.__is_changed = True
        return super().__setitem__(name, value)

    def on_end(self):
        if Settings.__is_changed:
            with open(Settings.__loading_path, "w") as f:
                from .tomllib_w import dumps
                f.write(dumps(self))


# config_file_path = os.path.join(os.path.dirname(__file__), 'settings.toml')
# with open(config_file_path, "rb") as f:
#     __config = tomllib.load(f)
# SETTINGS = _Setting(**__config)


class Configurable:
    def on_common_config(self):
        pass

    def on_linux_config(self):
        pass

    def on_darwin_config(self):
        pass

    def on_ios_config(self):
        pass

    def on_ipados_config(self):
        pass

    def on_windows_config(self):
        pass

    def on_others_config(self):
        raise NotImplementedError()

    def _set_config(self):
        """Layout related config (e.g. bindings).
        """
        self.on_common_config()
        os = platform.system().lower()
        match os:
            case "linux":
                self.on_linux_config()
            case "darwin":
                self.on_darwin_config()
            case "ios":
                self.on_ios_config()
            case "ipados":
                self.on_ipados_config()
            case "windows":
                self.on_windows_config()
            case _:
                self.on_others_config()
