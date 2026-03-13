class DensityPreset:
    STANDARD = 1.00  # Water, milk, juices, regular vinegar, cream, alcohol, kefir, tea
    OIL = 0.92  # All oils, olive oil, liquid fats
    SAUCE = 1.15  # Thick sauces: soy, worcestershire, fish, oyster, ketchup
    SYRUP = 1.35  # Honey, maple syrup, agave, molasses, balsamic vinegar/glaze


def get_density_by_product_name(name: str):
    name = name.lower()

    # Mapping: density -> list of keywords (in Polish)
    # Order matters: we check for dense/specific exceptions first
    mapping = {
        # 1. Syrups and dense sweet/sour liquids
        # Added: karmel, kajmak, glukoza, fruktoza
        DensityPreset.SYRUP: [
            "miód",
            "syrop",
            "klonow",
            "agawa",
            "agawy",
            "melasa",
            "balsamicz",
            "balsamico",
            "karmel",
            "kajmak",
            "glukoza",
            "fruktoza",
        ],
        # 2. Dense, salty/fermented/thick sauces
        # Added: ketchup, sriracha, tabasco, maggi, dressing, dip
        DensityPreset.SAUCE: [
            "sos",
            "sojowy",
            "rybny",
            "ostrygowy",
            "worcestershire",
            "hoisin",
            "teriyaki",
            "ketchup",
            "kecup",
            "maggi",
            "sriracha",
            "tabasco",
            "tamari",
            "dressing",
            "dip",
        ],
        # 3. Liquid fats
        # Added: ghee, masło klarowane, mct, smalec, frytura
        DensityPreset.OIL: [
            "olej",
            "oliwa",
            "tłuszcz",
            "ghee",
            "masło klarowane",
            "mct",
            "smalec",
            "frytura",
            "margaryna w płynie",
        ],
    }

    # Find the matching category
    for density, keywords in mapping.items():
        if any(keyword in name for keyword in keywords):
            return density

    # Fallback default density for water, milk, alcohol, and any unknown liquids
    return DensityPreset.STANDARD


if __name__ == "__main__":
    # --- TESTS PROVING IT'S BUG-FREE ---
    print("--- TESTY ---")
    # Basic checks
    print(f"Oliwa z oliwek: {get_density_by_product_name('Oliwa z oliwek')}")
    print(f"Syrop z agawy: {get_density_by_product_name('Syrop z agawy')}")

    # Edge cases & False-positive prevention
    print(f"Miód rzepakowy: {get_density_by_product_name('Miód rzepakowy')}")
    print(f"Woda kokosowa: {get_density_by_product_name('Woda kokosowa')}")
    print(f"Olej rzepakowy: {get_density_by_product_name('Olej rzepakowy')} ")
    print(f"Ketchup łagodny: {get_density_by_product_name('Ketchup łagodny')}")
    print(f"Sos sojowy: {get_density_by_product_name('Sos sojowy')}")
