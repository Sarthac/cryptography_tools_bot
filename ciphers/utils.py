def omit_blank_spaces(s: str):
    return "".join(s.split())


def omit_all_except_alpha(s: str):
    result = ""
    for c in s:
        if c.isalpha():
            result += c
    return result
