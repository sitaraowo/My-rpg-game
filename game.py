"""
文字RPG游戏 - 勇者大战怪兽
Text-based RPG Game - Hero vs Monster
"""

import random
import time


# ─────────────────────────────────────────────
#  工具函数 / Utility helpers
# ─────────────────────────────────────────────

def render_bar(label: str, current: int, maximum: int, width: int = 20, fill: str = "█", empty: str = "░") -> str:
    """返回带标签的进度条字符串。"""
    current = max(0, current)
    filled = int(width * current / maximum) if maximum > 0 else 0
    bar = fill * filled + empty * (width - filled)
    return f"{label}: [{bar}] {current:>3}/{maximum}"


def pause(seconds: float = 0.8) -> None:
    time.sleep(seconds)


def separator(char: str = "─", width: int = 50) -> None:
    print(char * width)


# ─────────────────────────────────────────────
#  技能定义 / Skill definitions
# ─────────────────────────────────────────────

SKILLS = {
    1: {
        "name": "⚔  普通攻击",
        "desc": "挥剑攻击，不消耗蓝量",
        "mp_cost": 0,
        "damage_range": (18, 28),
        "heal_range": None,
        "effect": None,
    },
    2: {
        "name": "🔥 烈焰冲击",
        "desc": "释放熊熊烈火，造成大量伤害",
        "mp_cost": 20,
        "damage_range": (35, 50),
        "heal_range": None,
        "effect": None,
    },
    3: {
        "name": "❄  冰霜箭",
        "desc": "射出冰霜箭矢，造成伤害并使怪兽冻结一回合",
        "mp_cost": 15,
        "damage_range": (22, 36),
        "heal_range": None,
        "effect": "freeze",
    },
    4: {
        "name": "💚 治愈术",
        "desc": "施放治愈魔法，恢复自身生命值",
        "mp_cost": 25,
        "damage_range": None,
        "heal_range": (32, 48),
        "effect": None,
    },
}

# 怪兽技能
MONSTER_SKILLS = [
    {"name": "利爪撕裂", "damage_range": (15, 25)},
    {"name": "毒液喷射", "damage_range": (18, 30)},
    {"name": "狂暴猛击", "damage_range": (25, 38)},
]


# ─────────────────────────────────────────────
#  角色类 / Character classes
# ─────────────────────────────────────────────

class Character:
    """角色基类。"""

    def __init__(self, name: str, max_hp: int, max_mp: int):
        self.name = name
        self.max_hp = max_hp
        self.max_mp = max_mp
        self.hp = max_hp
        self.mp = max_mp
        self.is_frozen = False  # 是否被冻结

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        """承受伤害，返回实际扣血量。"""
        actual = min(amount, self.hp)
        self.hp -= actual
        return actual

    def restore_hp(self, amount: int) -> int:
        """恢复生命值，返回实际恢复量。"""
        can_restore = self.max_hp - self.hp
        actual = min(amount, can_restore)
        self.hp += actual
        return actual

    def spend_mp(self, amount: int) -> bool:
        """消耗蓝量，蓝量不足返回 False。"""
        if self.mp < amount:
            return False
        self.mp -= amount
        return True

    def restore_mp(self, amount: int) -> None:
        self.mp = min(self.max_mp, self.mp + amount)

    def status_lines(self) -> list[str]:
        hp_bar = render_bar("HP", self.hp, self.max_hp)
        mp_bar = render_bar("MP", self.mp, self.max_mp, fill="▓", empty="░")
        return [hp_bar, mp_bar]


class Hero(Character):
    """勇者。"""

    def __init__(self):
        super().__init__("勇者", max_hp=120, max_mp=80)


class Monster(Character):
    """怪兽。"""

    def __init__(self):
        super().__init__("暗影魔兽", max_hp=160, max_mp=60)
        self.enrage_threshold = 0.3  # 血量低于 30% 时进入狂暴状态

    @property
    def is_enraged(self) -> bool:
        return self.hp / self.max_hp <= self.enrage_threshold

    def choose_action(self) -> dict:
        """怪兽随机选择一个攻击技能，狂暴时伤害加成 20%。"""
        skill = random.choice(MONSTER_SKILLS)
        lo, hi = skill["damage_range"]
        if self.is_enraged:
            lo = int(lo * 1.2)
            hi = int(hi * 1.2)
        damage = random.randint(lo, hi)
        return {"name": skill["name"], "damage": damage}


# ─────────────────────────────────────────────
#  战斗循环 / Battle loop
# ─────────────────────────────────────────────

class Battle:

    def __init__(self):
        self.hero = Hero()
        self.monster = Monster()
        self.turn = 1

    # ── 显示状态 ──────────────────────────────

    def show_status(self) -> None:
        separator()
        print(f"  【第 {self.turn} 回合】")
        separator()
        print(f"  ★ {self.hero.name}")
        for line in self.hero.status_lines():
            print(f"    {line}")
        if self.hero.is_frozen:
            print("    ⚠  状态：冻结（跳过本回合）")
        print()
        print(f"  ☠ {self.monster.name}" + ("  【狂暴！】" if self.monster.is_enraged else ""))
        for line in self.monster.status_lines():
            print(f"    {line}")
        if self.monster.is_frozen:
            print("    ❄  状态：冻结（跳过本回合）")
        separator()

    # ── 显示技能菜单 ────────────────────────

    def show_skill_menu(self) -> None:
        print("  请选择行动：")
        for key, skill in SKILLS.items():
            cost_str = f"消耗 {skill['mp_cost']} MP" if skill["mp_cost"] > 0 else "无消耗"
            available = "  " if self.hero.mp >= skill["mp_cost"] else "🚫"
            print(f"  {available} [{key}] {skill['name']}  ({cost_str})")
            print(f"       {skill['desc']}")
        print("  [0] 逃跑")
        separator("─", 50)

    # ── 玩家回合 ────────────────────────────

    def player_turn(self) -> bool:
        """返回 False 表示玩家逃跑。"""
        self.show_skill_menu()

        while True:
            try:
                choice = int(input("  > 输入数字选择：").strip())
            except ValueError:
                print("  ❌ 请输入有效数字！")
                continue

            if choice == 0:
                print("\n  你选择了逃跑……冒险者的旅程就此结束。")
                return False

            if choice not in SKILLS:
                print("  ❌ 无效选项，请重新输入。")
                continue

            skill = SKILLS[choice]

            if self.hero.mp < skill["mp_cost"]:
                print(f"  🚫 蓝量不足！{skill['name']} 需要 {skill['mp_cost']} MP，当前 MP：{self.hero.mp}")
                continue

            # 消耗蓝量
            self.hero.spend_mp(skill["mp_cost"])
            print()

            # 执行技能效果
            if skill["heal_range"]:
                # 治愈技能
                amount = random.randint(*skill["heal_range"])
                actual = self.hero.restore_hp(amount)
                print(f"  💚 {self.hero.name} 施放【{skill['name'].strip()}】，恢复了 {actual} 点生命值！")
            elif skill["damage_range"]:
                # 攻击技能
                damage = random.randint(*skill["damage_range"])
                actual = self.monster.take_damage(damage)
                print(f"  ⚔  {self.hero.name} 使用【{skill['name'].strip()}】，对 {self.monster.name} 造成了 {actual} 点伤害！")

                if skill["effect"] == "freeze" and not self.monster.is_frozen:
                    self.monster.is_frozen = True
                    print(f"  ❄  {self.monster.name} 被冻结，下一回合将无法行动！")

            pause()
            return True

    # ── 怪兽回合 ────────────────────────────

    def monster_turn(self) -> None:
        if self.monster.is_frozen:
            print(f"\n  ❄  {self.monster.name} 被冻结，无法行动！")
            self.monster.is_frozen = False
            pause()
            return

        action = self.monster.choose_action()
        actual = self.hero.take_damage(action["damage"])
        enrage_tag = "【狂暴】" if self.monster.is_enraged else ""
        print(f"\n  ☠  {self.monster.name} {enrage_tag}使用【{action['name']}】，对 {self.hero.name} 造成了 {actual} 点伤害！")

        # 怪兽每回合小量恢复蓝量
        self.monster.restore_mp(5)
        pause()

    # ── 主循环 ──────────────────────────────

    def run(self) -> None:
        print()
        separator("═", 50)
        print("  ✦  文字 RPG 游戏  ✦  勇者大战暗影魔兽  ✦")
        separator("═", 50)
        print(f"""
  【背景】
  黑暗森林深处，潜伏着一只凶残的暗影魔兽。
  它掠夺村庄、残害生灵。
  作为王国最后的勇者，你必须将其击败！

  【勇者属性】HP: {self.hero.max_hp}  MP: {self.hero.max_mp}
  【魔兽属性】HP: {self.monster.max_hp}  MP: {self.monster.max_mp}
""")
        separator("═", 50)
        input("  按 Enter 开始战斗……")

        while self.hero.is_alive and self.monster.is_alive:
            print()
            self.show_status()

            # 勇者回合
            escaped = not self.player_turn()
            if escaped:
                break

            if not self.monster.is_alive:
                break

            # 怪兽回合
            self.monster_turn()
            self.turn += 1

            # 勇者每回合小量恢复蓝量（冥想效果）
            self.hero.restore_mp(3)

        print()
        separator("═", 50)
        self._show_result()
        separator("═", 50)

    def _show_result(self) -> None:
        if not self.monster.is_alive and self.hero.is_alive:
            print(f"""
  🎉 恭喜！你击败了 {self.monster.name}！
  经过 {self.turn} 个回合的激战，
  勇者以 {self.hero.hp} HP、{self.hero.mp} MP 存活！
  王国的平静重新降临……
""")
        elif not self.hero.is_alive:
            print(f"""
  💀 你被 {self.monster.name} 击败了……
  经过 {self.turn} 个回合的激战，勇者英勇牺牲。
  {self.monster.name} 剩余 {self.monster.hp} HP。
  黑暗笼罩了王国……
""")
        else:
            print("""
  🏃 你选择了逃离战场……
  也许改天再战是明智之举。
""")


# ─────────────────────────────────────────────
#  入口 / Entry point
# ─────────────────────────────────────────────

def main() -> None:
    while True:
        battle = Battle()
        battle.run()
        print()
        again = input("  是否重新开始？(y/n) > ").strip().lower()
        if again != "y":
            print("\n  感谢游玩！再见！\n")
            break


if __name__ == "__main__":
    main()
