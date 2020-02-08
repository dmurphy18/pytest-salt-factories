# -*- coding: utf-8 -*-
"""
saltfactories.utils.compat
~~~~~~~~~~~~~~~~~~~~~~~~~~

Imports compatability layer
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# pragma: no cover
# pylint: disable=unused-import,invalid-name

try:
    # Salt > 2017.1.1
    import salt.utils.files

    fopen = salt.utils.files.fopen
except AttributeError:
    # Salt <= 2017.1.1
    fopen = salt.utils.fopen

try:
    # Salt >= 2018.3.0
    from salt.utils.path import which
except ImportError:
    # Salt < 2018.3.0
    from salt.utils import which

try:
    from unittest import mock
except ImportError:
    import mock
# pylint: enable=unused-import,invalid-name