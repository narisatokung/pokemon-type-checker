"""
Pokemon Type Effectiveness Checker (Generation 6+)
===================================================
วิธีใช้งาน:
    python pokemon_type_checker.py

    หลังจากรันโปรแกรม ระบบจะถามธาตุที่ 1 และ 2 (ไม่บังคับ)
    โปรแกรมจะแสดงผลว่าธาตุไหนโจมตีแล้วได้ผลคูณเท่าใด

ตัวอย่าง:
    ธาตุที่ 1: Water
    ธาตุที่ 2: Flying     (หรือกด Enter เพื่อข้าม)

    ผลลัพธ์ที่ได้รับ:
        4× → Electric
        2× → Rock
        ...
"""

# ---------------------------------------------------------------------------
# ข้อมูลความสัมพันธ์ของธาตุ (Generation 6+)
# โครงสร้าง: CHART[attacking_type][defending_type] = multiplier
# หากไม่มีค่า → multiplier = 1 (ปกติ)
# ---------------------------------------------------------------------------
CHART: dict[str, dict[str, float]] = {
    "Normal":   {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2,
                 "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water":    {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2,
                 "Rock": 2, "Dragon": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0,
                 "Flying": 2, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5,
                 "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2,
                 "Dragon": 0.5, "Steel": 0.5},
    "Ice":      {"Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2,
                 "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5,
                 "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0,
                 "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison":   {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5,
                 "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground":   {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2,
                 "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying":   {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2,
                 "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2, "Poison": 2, "Psychic": 0.5,
                 "Dark": 0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Flying": 0.5,
                 "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5,
                 "Fairy": 0.5},
    "Rock":     {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5,
                 "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost":    {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon":   {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2, "Ghost": 2,
                 "Dark": 0.5, "Fairy": 0.5},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2,
                 "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy":    {"Fire": 0.5, "Fighting": 2, "Poison": 0.5,
                 "Dragon": 2, "Dark": 2, "Steel": 0.5},
}

ALL_TYPES: list[str] = sorted(CHART.keys())


# ---------------------------------------------------------------------------
# ฟังก์ชันหลัก
# ---------------------------------------------------------------------------

def get_multiplier(attacking: str, defending: str) -> float:
    """คืนค่าตัวคูณเมื่อ attacking_type โจมตี defending_type"""
    return CHART.get(attacking, {}).get(defending, 1.0)


def calc_effectiveness(type1: str, type2: str | None = None) -> dict[float, list[str]]:
    """
    คำนวณค่าตัวคูณของทุกธาตุที่โจมตีโปเกม่อนซึ่งมีธาตุ type1 (และ type2)

    Returns:
        dict ที่ key คือตัวคูณ (4, 2, 1, 0.5, 0.25, 0) และ value คือ list ของธาตุ
    """
    buckets: dict[float, list[str]] = {4.0: [], 2.0: [], 1.0: [], 0.5: [], 0.25: [], 0.0: []}

    for attacking in ALL_TYPES:
        mult = get_multiplier(attacking, type1)
        if type2:
            mult *= get_multiplier(attacking, type2)

        # ปัดเศษเพื่อหลีกเลี่ยง floating-point error
        mult = round(mult, 4)

        if mult not in buckets:
            buckets[mult] = []
        buckets[mult].append(attacking)

    return buckets


def normalize_type(raw: str) -> str | None:
    """แปลง input ให้ตรงกับชื่อธาตุมาตรฐาน (case-insensitive)"""
    raw = raw.strip().capitalize()
    return raw if raw in CHART else None


def print_results(type1: str, type2: str | None, buckets: dict[float, list[str]]) -> None:
    """แสดงผลลัพธ์อย่างสวยงาม"""
    type_label = f"{type1}/{type2}" if type2 else type1
    print(f"\n{'=' * 50}")
    print(f"  Pokemon Type: {type_label}")
    print(f"{'=' * 50}")

    display_order = [
        (4.0,  "4×   อ่อนแอมาก  (Super effective x2)"),
        (2.0,  "2×   อ่อนแอ     (Super effective)"),
        (0.0,  "0×   ภูมิคุ้มกัน (Immune)"),
        (0.5,  "½×   ทนทาน      (Not very effective)"),
        (0.25, "¼×   ทนทานมาก  (Not very effective x2)"),
    ]

    for mult, header in display_order:
        types = buckets.get(mult, [])
        if types:
            print(f"\n  {header}")
            print(f"  └─ {', '.join(types)}")

    normal_types = buckets.get(1.0, [])
    if normal_types:
        print(f"\n  1×   ปกติ      (Normal)")
        print(f"  └─ {', '.join(normal_types)}")

    print()


def list_all_types() -> None:
    """แสดงรายการธาตุทั้งหมดที่รองรับ"""
    print("\nธาตุที่รองรับทั้งหมด (18 ธาตุ):")
    for i, t in enumerate(ALL_TYPES, 1):
        print(f"  {i:2}. {t}")
    print()


def main() -> None:
    print("=" * 50)
    print("  Pokemon Type Effectiveness Checker")
    print("  Generation 6+ (18 types)")
    print("=" * 50)
    print("\nพิมพ์ 'list' เพื่อดูธาตุทั้งหมด หรือ 'quit' เพื่อออก")

    while True:
        print()
        raw1 = input("ธาตุที่ 1: ").strip()

        if raw1.lower() == "quit":
            print("ออกจากโปรแกรม")
            break
        if raw1.lower() == "list":
            list_all_types()
            continue

        type1 = normalize_type(raw1)
        if not type1:
            print(f"  [!] ไม่พบธาตุ '{raw1}' กรุณาลองใหม่ หรือพิมพ์ 'list' เพื่อดูรายการ")
            continue

        raw2 = input("ธาตุที่ 2 (กด Enter เพื่อข้าม): ").strip()
        type2 = None
        if raw2:
            type2 = normalize_type(raw2)
            if not type2:
                print(f"  [!] ไม่พบธาตุ '{raw2}' จะใช้แค่ธาตุเดียว")
            elif type2 == type1:
                print("  [!] ธาตุที่ 2 ซ้ำกับธาตุที่ 1 จะใช้แค่ธาตุเดียว")
                type2 = None

        buckets = calc_effectiveness(type1, type2)
        print_results(type1, type2, buckets)

        again = input("เช็คธาตุอื่นอีกไหม? (y/n): ").strip().lower()
        if again != "y":
            print("ออกจากโปรแกรม")
            break


if __name__ == "__main__":
    main()
