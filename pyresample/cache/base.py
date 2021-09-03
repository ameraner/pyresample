#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Pyresample developers
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Parent cache classes and utilities for Resampler classes."""

from abc import ABC, abstractmethod
from typing import Hashable, Any


class ResampleCache(ABC):
    """Base class for all BaseResampler cache classes."""

    @abstractmethod
    def store(self, key: Hashable, value: Any) -> None:
        ...

    @abstractmethod
    def load(self, key: Hashable) -> Any:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    def remove(self, key: Hashable) -> None:
        """Remove an item from the cache's internal storage."""
        self.pop(key)

    @abstractmethod
    def pop(self, key: Hashable) -> Any:
        ...

    @abstractmethod
    def __repr__(self):
        ...
