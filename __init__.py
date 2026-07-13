from __future__ import annotations

if __package__:
    from .hermes_xapi import register
else:
    from hermes_xapi import register

__all__ = ["register"]
