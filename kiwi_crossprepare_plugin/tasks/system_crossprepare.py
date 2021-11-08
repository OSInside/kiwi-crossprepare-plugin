# Copyright (c) 2020 SUSE Software Solutions Germany GmbH.  All rights reserved.
#
# This file is part of kiwi-crossprepare-build.
#
# kiwi-crossprepare-build is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi-crossprepare-build is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi-crossprepare-build.  If not, see <http://www.gnu.org/licenses/>
#
"""
usage: kiwi-ng system crossprepare -h | --help
       kiwi-ng system crossprepare --target-arch=<arch> --init=<name> --target-dir=<directory>
           [--allow-existing-root]
       kiwi-ng system crossprepare help

commands:
    crossprepare
        prepare an image root tree for a cross architecture build process

options:
    --target-arch=<arch>
        name of image target architecture
    --init=<name>
        path to the image target architecture init program.
        The crossprepare plugin was created to support the qemu-binfmt
        concept to support calling cross-arch binaries. The preparation
        of an environment must be done by an independent host arch
        compatible binary which we call `init program` as it will be
        used as PID 1 program in the QEMU call from which binaries of
        the image architecture can be called. Neither kiwi nor this
        plugin are providers of the init sequence because this
        implements a custom initialization procedure which does not
        follow standards. From the plugin code the provided binary will
        be called and trusted to do the right thing.
    --target-dir=<directory>
        path to store the build results. The crossprepare command will
        initialize a new root directory at <directory>/build/image-root/
        which is compatible to how the kiwi build command does it.
        Therefore the specified --target-dir argument can also be
        used for a subsequent kiwi build command.
    --allow-existing-root
        allow to use an existing root directory from an earlier
        preparation attempt.
"""
import logging
import os
import shutil
from tempfile import TemporaryDirectory

from kiwi.command import Command
from kiwi.path import Path
from kiwi.tasks.base import CliTask
from kiwi.help import Help

from kiwi.exceptions import (
    KiwiFileNotFound,
    KiwiRootDirExists
)

log = logging.getLogger('kiwi')


class SystemCrossprepareTask(CliTask):
    def process(self) -> None:
        self.manual = Help()
        if self.command_args.get('help') is True:
            return self.manual.show('kiwi::system::crossprepare')

        init_binary = self.command_args.get('--init')
        if not os.path.isfile(init_binary):
            raise KiwiFileNotFound(
                f'init binary {init_binary!r} not found'
            )

        target_dir = self.command_args.get('--target-dir')
        if os.path.isdir(target_dir) \
           and not self.command_args.get('--allow-existing-root'):
            raise KiwiRootDirExists(
                f'image target dir {target_dir!r} already exists'
            )

        # Copy init binary with execution permissions to
        # python managed temporary directory
        init_dir = TemporaryDirectory(prefix='initvm_')
        shutil.copy(init_binary, init_dir.name)
        init_binary = os.sep.join(
            [init_dir.name, os.path.basename(init_binary)]
        )
        os.chmod(init_binary, 0o755)

        # Create new target image directory structure including
        # QEMU bin format handlers
        target_arch = self.command_args.get('--target-arch')
        target_bin_dir = os.sep.join(
            [target_dir, 'build', 'image-root', 'usr', 'bin']
        )
        target_image_dir = os.sep.join(
            [target_dir, 'build', 'image-root', 'image']
        )
        qemu_arch = target_arch
        if qemu_arch in [ 'armv6l', 'armv6hl', 'armv7l', 'armv7hl' ]:
            qemu_arch = 'arm'
        qemu_binaries = [
            '/usr/bin/qemu-binfmt',
            f'/usr/bin/qemu-{qemu_arch}-binfmt',
            f'/usr/bin/qemu-{qemu_arch}'
        ]
        if not os.path.isdir(target_dir):
            Path.create(target_bin_dir)
        if not os.path.isdir(target_image_dir):
            Path.create(target_image_dir)
        log.info(f'Copying QEMU binaries to: {target_bin_dir!r}')
        for qemu_binary in qemu_binaries:
            if not os.path.exists(qemu_binary):
                raise KiwiFileNotFound(
                    f'QEMU binary {qemu_binary!r} not found'
                )
            log.info(f'--> {qemu_binary}')
            shutil.copy(qemu_binary, target_bin_dir)

        # Call init binary
        if os.path.isfile('/.dockerenv.privileged'):
            log.warning('kiwi cross architecture setup is disabled in privileged docker. Ensure binfmtmisc handler got enabled external before')
            return

        log.info(f'Calling init binary {init_binary!r}')
        Command.run([init_binary])
