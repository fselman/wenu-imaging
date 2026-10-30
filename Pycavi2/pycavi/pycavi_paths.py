"""Explicit path bases shared by read-only inspection and future M3 adapters."""
from dataclasses import dataclass
from pathlib import Path


class PathResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class PathResolver:
    invocation_base: Path

    def __post_init__(self):
        base = Path(self.invocation_base)
        if not base.is_absolute():
            raise PathResolutionError("Invocation base must be absolute")
        object.__setattr__(self, "invocation_base", self.reference(base))

    @staticmethod
    def reference(value, *, base=None):
        """Resolve a declared reference; never borrow the process cwd as its base."""
        path = Path(value)
        if not path.is_absolute():
            if base is None or not Path(base).is_absolute():
                raise PathResolutionError("Relative reference has no recorded absolute base")
            path = Path(base) / path
        try:
            return path.resolve(strict=False)
        except (OSError, RuntimeError) as exc:
            raise PathResolutionError(f"Cannot resolve {path}: {exc}") from exc

    def argument(self, value):
        """Resolve a user argument once against the captured invocation directory."""
        return self.reference(value, base=self.invocation_base)
