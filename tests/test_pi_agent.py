from __future__ import annotations

import stat
from pathlib import Path

import pytest

from ultron.config import AppConfig, DiscordConfig, LLMProviderSpec, LoggingConfig, PiConfig, ReportsConfig
from ultron.ollama_reachability import ollama_openai_base_url, ollama_root_url
from ultron.pi_resolve import (
    build_pi_run_settings,
    pi_availability_message,
    resolve_ollama_endpoint,
    resolve_pi_bin,
)


def _minimal_app(*, llm_chain: tuple[LLMProviderSpec, ...] | None = None, pi: PiConfig | None = None) -> AppConfig:
    return AppConfig(
        timezone="UTC",
        discord=DiscordConfig(),
        reports=ReportsConfig(),
        report_schedule=(),
        logging=LoggingConfig(),
        llm_chain=llm_chain,
        pi=pi or PiConfig(),
    )


def _ollama_spec() -> LLMProviderSpec:
    return LLMProviderSpec(
        base_url="http://127.0.0.1:11434/v1",
        models=("llama3.2",),
        api_key_env="LLM_API_KEY",
        timeout_seconds=120.0,
        max_retries=0,
        name="local-ollama",
        enabled=True,
    )


def _cloud_spec() -> LLMProviderSpec:
    return LLMProviderSpec(
        base_url="https://api.openai.com/v1",
        models=("gpt-4o-mini",),
        api_key_env="OPENAI_API_KEY",
        timeout_seconds=60.0,
        max_retries=0,
        name="cloud-openai",
        enabled=True,
    )


def _make_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_ollama_url_helpers() -> None:
    assert ollama_root_url("http://127.0.0.1:11434/v1") == "http://127.0.0.1:11434"
    assert ollama_openai_base_url("http://127.0.0.1:11434") == "http://127.0.0.1:11434/v1"


def test_pi_unavailable_without_chain(tmp_path: Path) -> None:
    msg = pi_availability_message(_minimal_app(), repo_root=tmp_path)
    assert msg is not None
    assert "llm_chain" in msg


def test_pi_unavailable_without_npm(tmp_path: Path) -> None:
    app = _minimal_app(llm_chain=(_ollama_spec(),))
    msg = pi_availability_message(app, repo_root=tmp_path)
    assert msg is not None
    assert "pi binary" in msg or "npm install" in msg


def test_resolve_pi_bin_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="pi binary not found"):
        resolve_pi_bin(repo_root=tmp_path, bin_path_cfg="")


def test_pi_disabled_explicitly(tmp_path: Path) -> None:
    app = _minimal_app(llm_chain=(_ollama_spec(),), pi=PiConfig(enabled=False))
    msg = pi_availability_message(app, repo_root=tmp_path)
    assert msg is not None
    assert "disabled" in msg.lower()


def test_pi_unavailable_cloud_only_chain(tmp_path: Path) -> None:
    app = _minimal_app(llm_chain=(_cloud_spec(),))
    msg = pi_availability_message(app, repo_root=tmp_path)
    assert msg is not None
    assert "Ollama-like" in msg or "ollama" in msg.lower()


def test_resolve_pi_bin_prefers_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_bin = _make_executable(tmp_path / "env-pi")
    cfg_bin = _make_executable(tmp_path / "cfg-pi")
    local = _make_executable(tmp_path / "node_modules" / ".bin" / "pi")
    monkeypatch.setenv("ULTRON_PI_BIN", str(env_bin))

    got = resolve_pi_bin(repo_root=tmp_path, bin_path_cfg=str(cfg_bin))
    assert got == env_bin.resolve()
    assert got != cfg_bin.resolve()
    assert got != local.resolve()


def test_resolve_pi_bin_raises_on_non_executable_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = tmp_path / "not-exec"
    bad.write_text("x", encoding="utf-8")
    bad.chmod(stat.S_IRUSR | stat.S_IWUSR)
    monkeypatch.setenv("ULTRON_PI_BIN", str(bad))

    with pytest.raises(RuntimeError, match="ULTRON_PI_BIN is not executable"):
        resolve_pi_bin(repo_root=tmp_path, bin_path_cfg="")


def test_resolve_pi_bin_prefers_bin_path_cfg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_bin = _make_executable(tmp_path / "cfg-pi")
    _make_executable(tmp_path / "node_modules" / ".bin" / "pi")
    monkeypatch.delenv("ULTRON_PI_BIN", raising=False)

    got = resolve_pi_bin(repo_root=tmp_path, bin_path_cfg=str(cfg_bin))
    assert got == cfg_bin.resolve()


def test_resolve_pi_bin_relative_bin_path_under_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rel = Path("tools") / "pi"
    cfg_bin = _make_executable(tmp_path / rel)
    monkeypatch.delenv("ULTRON_PI_BIN", raising=False)

    got = resolve_pi_bin(repo_root=tmp_path, bin_path_cfg=str(rel))
    assert got == cfg_bin.resolve()


def test_resolve_pi_bin_raises_on_non_executable_bin_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = tmp_path / "cfg-not-exec"
    bad.write_text("x", encoding="utf-8")
    bad.chmod(stat.S_IRUSR | stat.S_IWUSR)
    monkeypatch.delenv("ULTRON_PI_BIN", raising=False)

    with pytest.raises(RuntimeError, match="pi.bin_path is not executable"):
        resolve_pi_bin(repo_root=tmp_path, bin_path_cfg=str(bad))


def test_resolve_pi_bin_falls_through_to_node_modules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = _make_executable(tmp_path / "node_modules" / ".bin" / "pi")
    monkeypatch.delenv("ULTRON_PI_BIN", raising=False)

    got = resolve_pi_bin(repo_root=tmp_path, bin_path_cfg="")
    assert got == local.resolve()


def test_resolve_ollama_endpoint_uses_chain_when_pi_empty() -> None:
    app = _minimal_app(llm_chain=(_ollama_spec(),), pi=PiConfig())
    assert resolve_ollama_endpoint(app) == ("http://127.0.0.1:11434/v1", "llama3.2")


def test_resolve_ollama_endpoint_prefers_pi_overrides() -> None:
    app = _minimal_app(
        llm_chain=(_ollama_spec(),),
        pi=PiConfig(ollama_base_url="http://10.0.0.5:11434/v1", model="custom-model"),
    )
    assert resolve_ollama_endpoint(app) == ("http://10.0.0.5:11434/v1", "custom-model")


def test_resolve_ollama_endpoint_none_without_ollama_like() -> None:
    assert resolve_ollama_endpoint(_minimal_app(llm_chain=(_cloud_spec(),))) is None
    assert resolve_ollama_endpoint(_minimal_app()) is None


def test_build_pi_run_settings_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pi_bin = _make_executable(tmp_path / "node_modules" / ".bin" / "pi")
    monkeypatch.delenv("ULTRON_PI_BIN", raising=False)
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    settings = build_pi_run_settings(
        _minimal_app(llm_chain=(_ollama_spec(),)),
        state_dir=state_dir,
        repo_root=tmp_path,
    )

    assert settings.repo_root == tmp_path.resolve()
    assert settings.workspace == tmp_path.resolve()
    assert settings.config_dir == (tmp_path / ".pi" / "agent").resolve()
    assert settings.state_dir == state_dir.resolve()
    assert settings.bin_path == pi_bin.resolve()
    assert settings.ollama_base_url == "http://127.0.0.1:11434/v1"
    assert settings.model == "llama3.2"
    assert settings.provider == "ollama"
    assert settings.prompt_path is None


def test_build_pi_run_settings_rejects_when_unavailable(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="pi binary|npm install|llm_chain|Ollama"):
        build_pi_run_settings(
            _minimal_app(llm_chain=(_ollama_spec(),)),
            state_dir=tmp_path / "state",
            repo_root=tmp_path,
        )
