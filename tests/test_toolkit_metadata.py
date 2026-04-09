"""Tests for the _azure_functions_toolkit_metadata convention on with_context."""

from __future__ import annotations

from azure_functions_logging import get_logging_metadata, with_context


class TestWithContextMetadata:
    """Verify that with_context sets toolkit metadata correctly."""

    def test_sync_handler_sets_metadata(self) -> None:
        """Sync handler decorated with @with_context gets logging metadata."""

        @with_context
        def handler(req: object, context: object) -> None:
            pass

        metadata = getattr(handler, "_azure_functions_toolkit_metadata")
        assert metadata is not None
        assert "logging" in metadata
        meta = metadata["logging"]
        assert meta["version"] == 1
        assert meta["context_param"] == "context"

    def test_async_handler_sets_metadata(self) -> None:
        """Async handler decorated with @with_context gets logging metadata."""

        @with_context
        async def handler(req: object, context: object) -> None:
            pass

        metadata = getattr(handler, "_azure_functions_toolkit_metadata")
        assert metadata is not None
        meta = metadata["logging"]
        assert meta["version"] == 1
        assert meta["context_param"] == "context"

    def test_custom_param_name_in_metadata(self) -> None:
        """Custom param name is reflected in metadata."""

        @with_context(param="ctx")
        def handler(req: object, ctx: object) -> None:
            pass

        metadata = getattr(handler, "_azure_functions_toolkit_metadata")
        meta = metadata["logging"]
        assert meta["version"] == 1
        assert meta["context_param"] == "ctx"

    def test_custom_param_async(self) -> None:
        """Async handler with custom param gets correct metadata."""

        @with_context(param="my_context")
        async def handler(req: object, my_context: object) -> None:
            pass

        metadata = getattr(handler, "_azure_functions_toolkit_metadata")
        meta = metadata["logging"]
        assert meta["version"] == 1
        assert meta["context_param"] == "my_context"


class TestGetLoggingMetadata:
    """Verify the get_logging_metadata getter function."""

    def test_returns_metadata_for_decorated_function(self) -> None:
        @with_context
        def handler(req: object, context: object) -> None:
            pass

        result = get_logging_metadata(handler)
        assert result is not None
        assert result["version"] == 1
        assert result["context_param"] == "context"

    def test_returns_none_for_undecorated_function(self) -> None:
        def handler() -> None:
            pass

        result = get_logging_metadata(handler)
        assert result is None

    def test_returns_none_for_non_dict_metadata(self) -> None:
        def handler() -> None:
            pass

        setattr(handler, "_azure_functions_toolkit_metadata", "not-a-dict")
        result = get_logging_metadata(handler)
        assert result is None

    def test_returns_none_for_missing_namespace(self) -> None:
        def handler() -> None:
            pass

        setattr(handler, "_azure_functions_toolkit_metadata", {"other": {}})
        result = get_logging_metadata(handler)
        assert result is None


class TestMetadataNamespacePreservation:
    """Verify that logging metadata preserves other toolkit namespaces."""

    def test_preserves_existing_namespaces(self) -> None:
        """Decorating with @with_context preserves other namespace metadata."""

        def handler(req: object, context: object) -> None:
            pass

        # Manually set metadata for another namespace
        setattr(
            handler,
            "_azure_functions_toolkit_metadata",
            {"db": {"version": 1, "bindings": []}},
        )

        decorated = with_context(handler)

        metadata = getattr(decorated, "_azure_functions_toolkit_metadata")
        assert "db" in metadata
        assert "logging" in metadata
        assert metadata["db"] == {"version": 1, "bindings": []}
        assert metadata["logging"]["version"] == 1
        assert metadata["logging"]["context_param"] == "context"

    def test_preserves_existing_namespaces_async(self) -> None:
        """Async handler preserves other namespace metadata."""

        async def handler(req: object, context: object) -> None:
            pass

        setattr(
            handler,
            "_azure_functions_toolkit_metadata",
            {"validation": {"version": 1, "rules": []}},
        )

        decorated = with_context(handler)

        metadata = getattr(decorated, "_azure_functions_toolkit_metadata")
        assert "validation" in metadata
        assert "logging" in metadata
        assert metadata["validation"] == {"version": 1, "rules": []}
