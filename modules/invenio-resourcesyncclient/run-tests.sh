#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 National Institute of Informatics.
#
# INVENIO-ResourceSyncClient is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

pydocstyle invenio_resourcesyncclient tests docs && \
isort -rc -c -df && \
check-manifest --ignore ".travis-*" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
