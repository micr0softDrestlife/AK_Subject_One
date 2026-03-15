#  Author: micr0softDrestlife


def normalize_hotkey(hotkey, default="<shift>+l"):
    """将配置热键转为 pynput 可识别格式。"""
    if not hotkey:
        return default

    mapping = {
        "ctrl": "<ctrl>",
        "control": "<ctrl>",
        "alt": "<alt>",
        "shift": "<shift>",
        "cmd": "<cmd>",
        "win": "<cmd>",
        "super": "<cmd>",
    }
    tokens = [
        token.strip().lower() for token in str(hotkey).split("+") if token.strip()
    ]
    if not tokens:
        return default

    mapped = [mapping.get(token, token) for token in tokens]
    return "+".join(mapped)


def build_hotkey_map(
    solve_hotkey,
    simplify_hotkey,
    border_hotkey,
    reselect_hotkey,
    legacy_reselect_hotkey,
    callbacks,
    warn=print,
):
    """
    生成 GlobalHotKeys 映射，统一处理重复键告警和旧键兼容。

    callbacks:
      - solve
      - simplify
      - border
      - reselect
    """
    solve_hotkey_expr = normalize_hotkey(solve_hotkey)
    simplify_hotkey_expr = normalize_hotkey(simplify_hotkey)
    border_hotkey_expr = normalize_hotkey(border_hotkey)
    reselect_hotkey_expr = normalize_hotkey(reselect_hotkey)

    hotkey_map = {
        solve_hotkey_expr: callbacks["solve"],
    }
    if simplify_hotkey_expr not in hotkey_map:
        hotkey_map[simplify_hotkey_expr] = callbacks["simplify"]
    else:
        warn(f"警告: 解题与简化快捷键重复({solve_hotkey})，已忽略简化快捷键注册")

    if border_hotkey_expr not in hotkey_map:
        hotkey_map[border_hotkey_expr] = callbacks["border"]
    else:
        warn(f"警告: 边框切换快捷键重复({border_hotkey})，已忽略边框快捷键注册")

    if reselect_hotkey_expr not in hotkey_map:
        hotkey_map[reselect_hotkey_expr] = callbacks["reselect"]
    else:
        warn(f"警告: 重选区域快捷键重复({reselect_hotkey})，已忽略重选快捷键注册")

    # 向后兼容旧热键，避免历史习惯失效。
    legacy_reselect_expr = normalize_hotkey(legacy_reselect_hotkey)
    if legacy_reselect_expr not in hotkey_map:
        hotkey_map[legacy_reselect_expr] = callbacks["reselect"]

    return hotkey_map
