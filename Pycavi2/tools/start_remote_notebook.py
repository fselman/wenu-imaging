#!/usr/bin/env python3
"""Start the existing chapman3 pilot notebook server for a Mac SSH tunnel."""

import argparse
import importlib.util
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys


def prepare_launch(root, port):
    """Validate the host, interpreter and registered kernel without writing files."""
    if (platform.system(), platform.node().split('.')[0]) != ('Linux', 'chapman3'):
        raise ValueError('Run this launcher on Linux chapman3 for wenu-imaging.')
    expected = (Path.home() / '.conda/envs/wenu-imaging').resolve()
    python = expected / 'bin/python'
    if Path(sys.prefix).resolve() != expected or Path(sys.executable).resolve() != python.resolve():
        raise ValueError('Use $HOME/.conda/envs/wenu-imaging/bin/python.')
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535.')
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError('Notebook workspace does not exist: {}'.format(root))
    if importlib.util.find_spec('notebook') is None:
        raise ValueError('Notebook is missing from the selected environment.')

    from jupyter_client.kernelspec import KernelSpecManager
    kernel = 'wenu-imaging-chapman3'
    spec = KernelSpecManager().get_kernel_spec(kernel)
    if not spec.argv or not Path(spec.argv[0]).is_absolute():
        raise ValueError('Kernel must use an absolute Python executable.')
    if Path(spec.argv[0]).resolve() != python.resolve():
        raise ValueError('Registered kernel points outside the wenu-imaging environment.')
    nice = shutil.which('nice')
    if nice is None:
        raise ValueError('Required nice command is unavailable.')
    command = [nice, '-n', '10', str(python), '-m', 'notebook',
               '--no-browser', '--ip=127.0.0.1', '--port={}'.format(port),
               '--ServerApp.port_retries=0', '--ServerApp.root_dir={}'.format(root),
               '--MappingKernelManager.default_kernel_name=' + kernel]
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                       MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    return command, environment


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8888)
    parser.add_argument('--root', type=Path, default=Path.home() /
                        'omegacam/workflows/wenu-imaging-test')
    parser.add_argument('--dry-run', action='store_true',
                        help='Validate and print commands without starting Jupyter.')
    args = parser.parse_args(argv)
    try:
        command, environment = prepare_launch(args.root, args.port)
    except Exception as exc:
        parser.exit(1, 'STOP: {}\n'.format(exc))
    print('Server command: ' + shlex.join(command), flush=True)
    print('In a separate Mac terminal, open the tunnel:', flush=True)
    print('ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 '
          '-L 127.0.0.1:{0}:127.0.0.1:{0} fselman@chapman3.sc.eso.org'
          .format(args.port), flush=True)
    print('Open the localhost token URL printed by Jupyter in Mac Firefox. '
          'Keep both terminals open; use Ctrl-C to stop.', flush=True)
    if not args.dry_run:
        os.execve(command[0], command, environment)
    return 0


if __name__ == '__main__':
    sys.exit(main())
