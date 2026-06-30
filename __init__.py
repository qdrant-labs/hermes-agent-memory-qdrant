if not __package__:
    import importlib
    import sys
    from pathlib import Path

    package_name = "hermes_agent_memory_qdrant"
    package = sys.modules.setdefault(package_name, sys.modules[__name__])
    package.__path__ = [str(Path(__file__).parent)]
    QdrantMemoryProvider = importlib.import_module(
        f"{package_name}.src.qdrant"
    ).QdrantMemoryProvider
else:
    from .src.qdrant import QdrantMemoryProvider


def register(ctx) -> None:
    ctx.register_memory_provider(QdrantMemoryProvider())


__all__ = ["QdrantMemoryProvider", "register"]
