"""
Pokemon Type Effectiveness Checker v2 — With Ability Interactions (Gen 6+)
===========================================================================
วิธีใช้งาน:
    python pokemon_type_checker_v2.py

    ระบบจะถามธาตุ 1-2 ธาตุ, Ability ฝ่ายรับ และ Ability ฝ่ายรุก (ไม่บังคับทั้งคู่)
    โปรแกรมจะแสดงผลตัวคูณพร้อมระบุว่า Ability ใดส่งผลต่อการคำนวณ

ตัวอย่าง:
    ธาตุที่ 1  : Water
    ธาตุที่ 2  : Flying
    Ability รับ: Volt Absorb
    Ability รุก: (Enter เพื่อข้าม)

คำสั่งพิเศษใน prompt:
    list       → แสดงธาตุทั้งหมด
    abilities  → แสดง Ability ทั้งหมดพร้อมคำอธิบาย
    quit       → ออกจากโปรแกรม
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


# ===========================================================================
# SECTION 1: Type Chart (Generation 6+)
# โครงสร้าง: CHART[attacking_type][defending_type] = multiplier
# หากไม่มี key → multiplier = 1.0 (ปกติ)
# ===========================================================================

CHART: dict[str, dict[str, float]] = {
    "Normal":   {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0,
                 "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water":    {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0,
                 "Rock": 2.0, "Dragon": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0,
                 "Flying": 2.0, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5,
                 "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0,
                 "Dragon": 0.5, "Steel": 0.5},
    "Ice":      {"Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0,
                 "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5,
                 "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0,
                 "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison":   {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5,
                 "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground":   {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0,
                 "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying":   {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0,
                 "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5,
                 "Dark": 0.0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Flying": 0.5,
                 "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5,
                 "Fairy": 0.5},
    "Rock":     {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5,
                 "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost":    {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon":   {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0,
                 "Dark": 0.5, "Fairy": 0.5},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0,
                 "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy":    {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5,
                 "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5},
}

ALL_TYPES: list[str] = sorted(CHART.keys())


# ===========================================================================
# SECTION 2: Ability System
#
# แต่ละ Ability ถูก encode ด้วย AbilityDef dataclass ซึ่งแยก logic
# ออกเป็น 2 กลุ่มชัดเจน:
#
#   DEFENDER_ABILITIES  — Ability ฝ่ายรับ: ปรับตัวคูณของธาตุที่ตีเข้ามา
#   ATTACKER_ABILITIES  — Ability ฝ่ายรุก: เพิ่ม / ยกเลิก immunity ของฝ่ายรับ
#
# วิธีเพิ่ม Ability ใหม่:
#   1. กำหนด handler function ตามลายเซ็น AbilityHandler
#   2. เพิ่ม AbilityDef เข้า DEFENDER_ABILITIES หรือ ATTACKER_ABILITIES
# ===========================================================================

# ลายเซ็นของ handler
#   attacking_type : ธาตุของท่าโจมตี
#   def_type1/2    : ธาตุของโปเกม่อนฝ่ายรับ
#   base_mult      : ตัวคูณปัจจุบัน (ก่อน Ability นี้จะทำงาน)
#   คืนค่า         : ตัวคูณใหม่
AbilityHandler = Callable[[str, str, str | None, float], float]


@dataclass
class AbilityDef:
    """นิยาม Ability หนึ่งตัว"""
    name: str
    description: str
    # handler รับ (attacking_type, def_type1, def_type2, current_mult) → new_mult
    handler: AbilityHandler
    # กลุ่มของ Ability — ใช้ในการแสดงผลเท่านั้น
    group: str = "defender"


# ---------------------------------------------------------------------------
# Handler helpers — ฟังก์ชันสั้นๆ ที่ใช้สร้าง handler แบบทั่วไป
# ---------------------------------------------------------------------------

def _immune_to(immune_type: str) -> AbilityHandler:
    """สร้าง handler ที่ทำให้ธาตุ immune_type มีผล 0×"""
    def handler(atk: str, dt1: str, dt2: str | None, mult: float) -> float:
        return 0.0 if atk == immune_type else mult
    return handler


def _boost_incoming(boost_type: str, factor: float) -> AbilityHandler:
    """สร้าง handler ที่คูณเพิ่มตัวคูณเมื่อโดนธาตุ boost_type"""
    def handler(atk: str, dt1: str, dt2: str | None, mult: float) -> float:
        return mult * factor if atk == boost_type else mult
    return handler


# ---------------------------------------------------------------------------
# Defender Abilities — ปรับตัวคูณเมื่อโดนโจมตี
# ---------------------------------------------------------------------------

DEFENDER_ABILITIES: dict[str, AbilityDef] = {
    # --- Immunity Abilities (0×) ---
    "Levitate": AbilityDef(
        name="Levitate",
        description="ทำให้ท่าธาตุ Ground ไม่ส่งผล (0×)",
        handler=_immune_to("Ground"),
    ),
    "Water Absorb": AbilityDef(
        name="Water Absorb",
        description="ทำให้ท่าธาตุ Water ไม่ส่งผล (0×) และฟื้น HP",
        handler=_immune_to("Water"),
    ),
    "Storm Drain": AbilityDef(
        name="Storm Drain",
        description="ดูดซับท่าธาตุ Water ทั้งหมด (0×) และเพิ่ม Sp.Atk",
        handler=_immune_to("Water"),
    ),
    "Flash Fire": AbilityDef(
        name="Flash Fire",
        description="ดูดซับท่าธาตุ Fire (0×) และบูสต์ท่า Fire ของตัวเอง",
        handler=_immune_to("Fire"),
    ),
    "Sap Sipper": AbilityDef(
        name="Sap Sipper",
        description="ดูดซับท่าธาตุ Grass (0×) และเพิ่ม Atk",
        handler=_immune_to("Grass"),
    ),
    "Volt Absorb": AbilityDef(
        name="Volt Absorb",
        description="ดูดซับท่าธาตุ Electric (0×) และฟื้น HP",
        handler=_immune_to("Electric"),
    ),
    "Lightning Rod": AbilityDef(
        name="Lightning Rod",
        description="ดูดซับท่าธาตุ Electric ทั้งหมด (0×) และเพิ่ม Sp.Atk",
        handler=_immune_to("Electric"),
    ),
    "Motor Drive": AbilityDef(
        name="Motor Drive",
        description="ดูดซับท่าธาตุ Electric (0×) และเพิ่ม Speed",
        handler=_immune_to("Electric"),
    ),
    "Dry Skin": AbilityDef(
        name="Dry Skin",
        description="ดูดซับท่าธาตุ Water (0×), รับดาเมจ Fire เพิ่มขึ้น (1.25×)",
        handler=lambda atk, dt1, dt2, mult: (
            0.0 if atk == "Water"
            else mult * 1.25 if atk == "Fire"
            else mult
        ),
    ),
    "Earth Eater": AbilityDef(
        name="Earth Eater",
        description="ดูดซับท่าธาตุ Ground (0×) และฟื้น HP",
        handler=_immune_to("Ground"),
    ),
    "Well-Baked Body": AbilityDef(
        name="Well-Baked Body",
        description="ดูดซับท่าธาตุ Fire (0×) และเพิ่ม Def มาก",
        handler=_immune_to("Fire"),
    ),
    "Wind Rider": AbilityDef(
        name="Wind Rider",
        description="ภูมิคุ้มกันต่อท่า Flying (0×) บางกรณี",
        handler=_immune_to("Flying"),
    ),
    # --- Damage Modifier Abilities ---
    "Thick Fat": AbilityDef(
        name="Thick Fat",
        description="ลดดาเมจจากท่าธาตุ Fire และ Ice ลงครึ่งหนึ่ง (0.5×)",
        handler=lambda atk, dt1, dt2, mult: (
            mult * 0.5 if atk in ("Fire", "Ice") else mult
        ),
    ),
    "Heatproof": AbilityDef(
        name="Heatproof",
        description="ลดดาเมจจากท่าธาตุ Fire ลงครึ่งหนึ่ง (0.5×)",
        handler=_boost_incoming("Fire", 0.5),
    ),
    "Fluffy": AbilityDef(
        name="Fluffy",
        description="ลดดาเมจจากท่า Contact (0.5×) แต่รับ Fire เพิ่มขึ้น (2×)",
        handler=_boost_incoming("Fire", 2.0),
    ),
    "Wonder Guard": AbilityDef(
        name="Wonder Guard",
        description="รับดาเมจจากท่าที่ super effective (>1×) เท่านั้น ท่าอื่นไม่ส่งผล",
        handler=lambda atk, dt1, dt2, mult: mult if mult > 1.0 else 0.0,
    ),
    "Purifying Salt": AbilityDef(
        name="Purifying Salt",
        description="ภูมิคุ้มกันต่อสถานะ และลดดาเมจ Ghost (0.5×)",
        handler=_boost_incoming("Ghost", 0.5),
    ),
}

# ---------------------------------------------------------------------------
# Attacker Abilities — ปรับตัวคูณจากฝั่งผู้โจมตี
# ---------------------------------------------------------------------------

@dataclass
class AttackerAbilityDef:
    """นิยาม Ability ฝั่งรุก"""
    name: str
    description: str
    # handler รับ (attacking_type, def_type1, def_type2, current_mult) → new_mult
    # ทำงานหลัง type chart แต่ก่อน defender ability (ยกเว้น Mold Breaker)
    handler: AbilityHandler
    # True = Ability นี้ bypass Defender Abilities ทั้งหมด
    breaks_mold: bool = False
    group: str = "attacker"


def _scrappy_handler(atk: str, dt1: str, dt2: str | None, mult: float) -> float:
    """Normal / Fighting ตี Ghost ได้ (0 → 1×)"""
    if atk in ("Normal", "Fighting"):
        if dt1 == "Ghost" or dt2 == "Ghost":
            return 1.0 if mult == 0.0 else mult
    return mult


def _tinted_lens_handler(atk: str, dt1: str, dt2: str | None, mult: float) -> float:
    """ท่าที่ not very effective จะได้ตัวคูณ ×2"""
    return mult * 2.0 if mult < 1.0 else mult


def _filter_handler(atk: str, dt1: str, dt2: str | None, mult: float) -> float:
    """ลดดาเมจจากท่า super effective ลง (×0.75)"""
    return mult * 0.75 if mult > 1.0 else mult


ATTACKER_ABILITIES: dict[str, AttackerAbilityDef] = {
    "Mold Breaker": AttackerAbilityDef(
        name="Mold Breaker",
        description="ทะลุ Ability ป้องกันของศัตรูทั้งหมด (เช่น Levitate, Volt Absorb)",
        handler=lambda atk, dt1, dt2, mult: mult,  # logic จัดการใน calc_effectiveness
        breaks_mold=True,
    ),
    "Teravolt": AttackerAbilityDef(
        name="Teravolt",
        description="เหมือน Mold Breaker — ทะลุ Ability ป้องกันของศัตรู",
        handler=lambda atk, dt1, dt2, mult: mult,
        breaks_mold=True,
    ),
    "Turboblaze": AttackerAbilityDef(
        name="Turboblaze",
        description="เหมือน Mold Breaker — ทะลุ Ability ป้องกันของศัตรู",
        handler=lambda atk, dt1, dt2, mult: mult,
        breaks_mold=True,
    ),
    "Scrappy": AttackerAbilityDef(
        name="Scrappy",
        description="ท่าธาตุ Normal และ Fighting ตีโปเกม่อนธาตุ Ghost ได้ (0→1×)",
        handler=_scrappy_handler,
    ),
    "Tinted Lens": AttackerAbilityDef(
        name="Tinted Lens",
        description="ท่าที่ not very effective (<1×) จะได้ตัวคูณเพิ่มเป็น 2 เท่า",
        handler=_tinted_lens_handler,
    ),
    "Filter": AttackerAbilityDef(
        name="Filter",
        description="(ฝ่ายรับ) ลดดาเมจ super effective ลง 25% — ใส่เป็น attacker perspective",
        handler=_filter_handler,
    ),
    "Solid Rock": AttackerAbilityDef(
        name="Solid Rock",
        description="(ฝ่ายรับ) ลดดาเมจ super effective ลง 25% เหมือน Filter",
        handler=_filter_handler,
    ),
}

# ตัวอย่าง Ability ที่ยังไม่ implement (stub สำหรับอนาคต)
# "Neutralizing Gas" : ยกเลิก Ability ของ Pokemon ทุกตัวในสนาม
# "Prism Armor"      : ลด super effective เหมือน Filter แต่ทะลุด้วย Mold Breaker ไม่ได้


# ===========================================================================
# SECTION 3: Core Calculation Logic
# ===========================================================================

@dataclass
class EffectivenessResult:
    """ผลลัพธ์ของการคำนวณ"""
    buckets: dict[float, list[str]] = field(default_factory=dict)
    # ability_log[attacking_type] = รายชื่อ Ability ที่ส่งผล
    ability_log: dict[str, list[str]] = field(default_factory=dict)


def get_base_multiplier(attacking: str, defending: str) -> float:
    return CHART.get(attacking, {}).get(defending, 1.0)


def calc_effectiveness(
    type1: str,
    type2: str | None = None,
    defender_ability: AbilityDef | None = None,
    attacker_ability: AttackerAbilityDef | None = None,
) -> EffectivenessResult:
    """
    คำนวณ Type Effectiveness พร้อม Ability Interactions

    ลำดับการคำนวณสำหรับแต่ละธาตุที่โจมตี:
        1. Type chart base multiplier (type1 × type2)
        2. Attacker Ability (เช่น Scrappy ปลดล็อค Ghost immunity)
        3. Defender Ability — ข้ามถ้า attacker มี Mold Breaker
    """
    result = EffectivenessResult()
    breaks_mold = attacker_ability is not None and attacker_ability.breaks_mold

    for attacking in ALL_TYPES:
        triggered: list[str] = []

        # Step 1: Base type chart
        mult = get_base_multiplier(attacking, type1)
        if type2:
            mult *= get_base_multiplier(attacking, type2)
        mult = round(mult, 4)

        # Step 2: Attacker Ability (ทำงานก่อน defender)
        if attacker_ability and not attacker_ability.breaks_mold:
            new_mult = attacker_ability.handler(attacking, type1, type2, mult)
            if new_mult != mult:
                triggered.append(attacker_ability.name)
            mult = round(new_mult, 4)

        # Step 3: Defender Ability (ข้ามถ้า Mold Breaker)
        if defender_ability and not breaks_mold:
            new_mult = defender_ability.handler(attacking, type1, type2, mult)
            if new_mult != mult:
                triggered.append(defender_ability.name)
            mult = round(new_mult, 4)
        elif defender_ability and breaks_mold:
            triggered.append(f"[Mold Breaker] ทะลุ {defender_ability.name}")

        if mult not in result.buckets:
            result.buckets[mult] = []
        result.buckets[mult].append(attacking)
        if triggered:
            result.ability_log[attacking] = triggered

    return result


# ===========================================================================
# SECTION 4: Display Helpers
# ===========================================================================

DISPLAY_ORDER: list[tuple[float, str]] = [
    (4.0,  "4×   อ่อนแอมาก  (Super effective ×2)"),
    (2.0,  "2×   อ่อนแอ     (Super effective)"),
    (0.0,  "0×   ภูมิคุ้มกัน (Immune)"),
    (0.5,  "½×   ทนทาน      (Not very effective)"),
    (0.25, "¼×   ทนทานมาก  (Not very effective ×2)"),
    (1.0,  "1×   ปกติ       (Normal)"),
]


def print_results(
    type1: str,
    type2: str | None,
    result: EffectivenessResult,
    defender_ability: AbilityDef | None,
    attacker_ability: AttackerAbilityDef | None,
) -> None:
    type_label = f"{type1}/{type2}" if type2 else type1
    sep = "=" * 54

    print(f"\n{sep}")
    print(f"  Pokemon  : {type_label}")
    if defender_ability:
        print(f"  Ability  : {defender_ability.name}  ({defender_ability.description})")
    if attacker_ability:
        print(f"  Atk Abil : {attacker_ability.name}  ({attacker_ability.description})")
    print(sep)

    for mult, header in DISPLAY_ORDER:
        types = result.buckets.get(mult, [])
        if not types:
            continue
        print(f"\n  {header}")
        lines: list[str] = []
        for t in types:
            log = result.ability_log.get(t)
            suffix = f"  ← {', '.join(log)}" if log else ""
            lines.append(f"    • {t}{suffix}")
        print("\n".join(lines))

    print()


def list_all_types() -> None:
    print("\nธาตุที่รองรับ (18 ธาตุ):")
    cols = [ALL_TYPES[i::3] for i in range(3)]
    for row in zip(*cols):
        print("  " + "    ".join(f"{t:<12}" for t in row))
    print()


def list_all_abilities() -> None:
    print("\n── Defender Abilities ──────────────────────────────")
    for name, ab in DEFENDER_ABILITIES.items():
        print(f"  {name:<20} {ab.description}")
    print("\n── Attacker Abilities ──────────────────────────────")
    for name, ab in ATTACKER_ABILITIES.items():
        print(f"  {name:<20} {ab.description}")
    print()


# ===========================================================================
# SECTION 5: Input Helpers
# ===========================================================================

def normalize_type(raw: str) -> str | None:
    raw = raw.strip().capitalize()
    return raw if raw in CHART else None


def normalize_defender_ability(raw: str) -> AbilityDef | None:
    raw = raw.strip().title()
    return DEFENDER_ABILITIES.get(raw)


def normalize_attacker_ability(raw: str) -> AttackerAbilityDef | None:
    raw = raw.strip().title()
    return ATTACKER_ABILITIES.get(raw)


# ===========================================================================
# SECTION 6: Main Loop
# ===========================================================================

def main() -> None:
    print("=" * 54)
    print("  Pokemon Type Effectiveness Checker v2")
    print("  Generation 6+ | Ability Interactions")
    print("=" * 54)
    print("  พิมพ์ 'list' → ธาตุทั้งหมด")
    print("  พิมพ์ 'abilities' → Ability ทั้งหมด")
    print("  พิมพ์ 'quit' → ออก")

    while True:
        print()

        # --- ธาตุฝ่ายรับ ---
        raw1 = input("ธาตุที่ 1          : ").strip()
        if raw1.lower() == "quit":
            print("ออกจากโปรแกรม")
            break
        if raw1.lower() == "list":
            list_all_types()
            continue
        if raw1.lower() == "abilities":
            list_all_abilities()
            continue

        type1 = normalize_type(raw1)
        if not type1:
            print(f"  [!] ไม่พบธาตุ '{raw1}'")
            continue

        raw2 = input("ธาตุที่ 2 (Enter ข้าม): ").strip()
        type2: str | None = None
        if raw2:
            type2 = normalize_type(raw2)
            if not type2:
                print(f"  [!] ไม่พบธาตุ '{raw2}' จะใช้ธาตุเดียว")
            elif type2 == type1:
                print("  [!] ธาตุซ้ำ จะใช้ธาตุเดียว")
                type2 = None

        # --- Ability ฝ่ายรับ ---
        raw_da = input("Ability ฝ่ายรับ   : ").strip()
        defender_ability: AbilityDef | None = None
        if raw_da:
            defender_ability = normalize_defender_ability(raw_da)
            if not defender_ability:
                print(f"  [!] ไม่พบ Defender Ability '{raw_da}' (พิมพ์ 'abilities' ดูรายการ)")

        # --- Ability ฝ่ายรุก ---
        raw_aa = input("Ability ฝ่ายรุก   : ").strip()
        attacker_ability: AttackerAbilityDef | None = None
        if raw_aa:
            attacker_ability = normalize_attacker_ability(raw_aa)
            if not attacker_ability:
                print(f"  [!] ไม่พบ Attacker Ability '{raw_aa}' (พิมพ์ 'abilities' ดูรายการ)")

        result = calc_effectiveness(type1, type2, defender_ability, attacker_ability)
        print_results(type1, type2, result, defender_ability, attacker_ability)

        again = input("เช็คอีกครั้ง? (y/n): ").strip().lower()
        if again != "y":
            print("ออกจากโปรแกรม")
            break


if __name__ == "__main__":
    main()
