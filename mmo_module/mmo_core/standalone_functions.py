def get_display_bar(value_name: str, current_value: float, max_value: float, adjustment: int = 0,
                    suffix: str = "") -> str:
    string_value = str(round(current_value, 1))
    if max_value > 0:
        value_offset = int(10 * current_value / max_value)
    else:
        value_offset = 0
    output = f"{value_name}: {' ' * adjustment}{string_value}{' ' * (4 - len(string_value))} " \
             f"╓{'▄' * value_offset}{'─' * (10 - value_offset)}╖ {round(max_value, 1)}{suffix}"
    return output  # "Health: 24.3 ╓▄▄────────╖ 100, at 10/m"
