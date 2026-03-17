def normalize_ean(ean: str):
    return "".join(ean.split())


def is_ean_valid(value: str):
    # remove blanks
    value = normalize_ean(value)

    if not value.isdigit() or len(value) != 13:
        return False

    digits = [int(d) for d in value]
    checksum = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits[:-1]))
    check_digit = (10 - (checksum % 10)) % 10

    if check_digit != digits[-1]:
        return False

    return True
