from typing import Union

from automatarr.core.drm.clearkey import ClearKey
from automatarr.core.drm.playready import PlayReady
from automatarr.core.drm.widevine import Widevine

DRM_T = Union[ClearKey, Widevine, PlayReady]


__all__ = ("ClearKey", "Widevine", "PlayReady", "DRM_T")
