"""Step-0 hardware/software declaration and its cryptographic signature (Sec. 5.5)."""

from police_thief.shared.system_info import collect_step0_declaration, sign_declaration


def make_declaration():
    return collect_step0_declaration(
        code_version="0.1.0",
        github_commit="deadbeef",
        group_name="test-team",
        sub_game_number=1,
        llm_model="claude-haiku-4-5",
    )


def test_collect_step0_declaration_fills_required_fields():
    declaration = make_declaration()

    assert declaration.os_name  # non-empty on any real machine
    assert declaration.cpu_cores > 0
    assert declaration.llm_model == "claude-haiku-4-5"
    assert declaration.code_version == "0.1.0"
    assert declaration.github_commit == "deadbeef"
    assert declaration.group_name == "test-team"
    assert declaration.sub_game_number == 1


def test_cpu_freq_and_ram_are_non_negative():
    declaration = make_declaration()
    assert declaration.cpu_freq_mhz >= 0.0
    assert declaration.ram_gb >= 0.0


def test_gpu_absent_is_represented_as_none_not_a_crash():
    declaration = make_declaration()
    # No assumption about whether this test machine has a GPU -- just that
    # the field is well-typed either way (str or None), and vram_gb only
    # set when gpu is.
    assert declaration.gpu is None or isinstance(declaration.gpu, str)
    if declaration.gpu is None:
        assert declaration.vram_gb is None


def test_sign_declaration_is_deterministic_for_same_key():
    declaration = make_declaration()
    key = b"shared-secret-key"

    sig1 = sign_declaration(declaration, key)
    sig2 = sign_declaration(declaration, key)

    assert sig1 == sig2


def test_sign_declaration_differs_with_different_keys():
    declaration = make_declaration()
    sig_a = sign_declaration(declaration, b"key-a")
    sig_b = sign_declaration(declaration, b"key-b")
    assert sig_a != sig_b


def test_sign_declaration_detects_tampering():
    declaration = make_declaration()
    key = b"shared-secret-key"
    original_sig = sign_declaration(declaration, key)

    tampered = collect_step0_declaration(
        code_version="0.1.0",
        github_commit="forged-commit-hash",  # tampered field
        group_name="test-team",
        sub_game_number=1,
        llm_model="claude-haiku-4-5",
    )
    tampered_sig = sign_declaration(tampered, key)

    assert original_sig != tampered_sig
