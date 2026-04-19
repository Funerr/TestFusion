from __future__ import annotations

import os
from pathlib import Path

import pytest

from core.executor.runner import Runner


@pytest.fixture()
def artifact_root(tmp_path: Path) -> Path:
    root = tmp_path / "artifacts"
    os.environ["TESTAUTO_ARTIFACT_ROOT"] = str(root)
    return root


@pytest.fixture()
def runner(artifact_root: Path) -> Runner:
    return Runner(artifact_root=artifact_root, backend="mock")
