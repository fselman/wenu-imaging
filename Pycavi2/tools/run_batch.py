#!/usr/bin/env python3
"""Execute one batch command at niceness >=10, leaving its caller unchanged."""
import argparse
import os
import shlex
import sys

from start_remote_notebook import validate_runtime


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('command', nargs=argparse.REMAINDER,
                        help='Command and arguments, normally after --.')
    args = parser.parse_args(argv)
    command = args.command
    if command[:1] == ['--']:
        command = command[1:]
    if not command:
        parser.error('Supply a batch command after --.')
    try:
        validate_runtime()
        priority = max(10, os.getpriority(os.PRIO_PROCESS, 0))
        environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                           MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
        print('Batch niceness: {} | {}'.format(priority, shlex.join(command)), flush=True)
        if args.dry_run:
            return 0
        # This helper is a separate process; only it and its descendants change.
        os.setpriority(os.PRIO_PROCESS, 0, priority)
        os.execvpe(command[0], command, environment)
    except (ValueError, OSError) as exc:
        parser.exit(1, 'STOP: {}\n'.format(exc))


if __name__ == '__main__':
    sys.exit(main())
