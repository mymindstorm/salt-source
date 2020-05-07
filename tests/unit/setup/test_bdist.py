# -*- coding: utf-8 -*-
"""
tests.integration.setup.test_bdist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import re

import salt.utils.path
import salt.utils.platform
from salt.modules.virtualenv_mod import KNOWN_BINARY_NAMES
from tests.support.helpers import VirtualEnv, slowTest, with_tempdir
from tests.support.runtests import RUNTIME_VARS
from tests.support.unit import TestCase, skipIf


@skipIf(
    salt.utils.path.which_bin(KNOWN_BINARY_NAMES) is None, "virtualenv not installed"
)
class BdistSetupTest(TestCase):
    """
    Tests for building and installing bdist_wheel packages
    """

    @slowTest
    @with_tempdir()
    def test_wheel_build(self, tempdir):
        """
        test building a bdist_wheel package
        """
        # Let's create the testing virtualenv
        with VirtualEnv() as venv:
            venv.run(venv.venv_python, "setup.py", "clean", cwd=RUNTIME_VARS.CODE_DIR)
            venv.run(
                venv.venv_python,
                "setup.py",
                "bdist_wheel",
                "--dist-dir",
                tempdir,
                cwd=RUNTIME_VARS.CODE_DIR,
            )
            for _file in os.listdir(tempdir):
                if _file.endswith("whl"):
                    whl = os.path.join(tempdir, _file)
                    break

            venv.install("--ignore-installed", whl)
            # Let's ensure the version is correct
            cmd = venv.run(venv.venv_python, "-m", "pip", "freeze")
            for line in cmd.stdout.splitlines():
                if line.startswith("salt"):
                    pip_ver = line.split("=")[-1]
                    break
            else:
                self.fail("Salt was not found installed")
            whl_ver = [
                x for x in whl.split("/")[-1:][0].split("-") if re.search(r"^\d.\d*", x)
            ][0]
            assert pip_ver == whl_ver.replace("_", "-")
