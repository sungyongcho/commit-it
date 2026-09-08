#!/usr/bin/env python3
"""Reject the retired shared installer without touching product installations."""
import sys


def main(argv=None):
    """Direct callers to native installation instead of recreating shared links."""
    print('The shared installer is retired; no installation was performed. '
          'Use the product native skill installer and its default location. '
          'See README.md. Source Git maintenance is independent of installation.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
