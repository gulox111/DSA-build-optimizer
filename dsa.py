import itertools
import heapq

"""
For those unfamiliar, python is going to use the last known (declared) value of a variable
This will use the value 140:
atk_rune = 140.0
#atk_rune = 0.0

While this is going to use the value 0:
atk_rune = 140.0
atk_rune = 0.0
"""

# Runes
atk_rune = 140.0 # Attack
#atk_rune = 0.0
crit_rune = 0.085 # Crit Rate
#crit_rune = 0.0
cd_rune = 0.14 # Crit Damage
#cd_rune = 0.0

# Mainstats
m_atk_up= (0.3409, 0.3068, 0.2386,0.2386,0.2386) # Attack Power Up
m_crit = (0.1666, 0.1500, 0.1166, 0.1166, 0.1166)
m_cd = (0.2678, 0.2410,0.1875,0.1875,0.1875)


# Substats
# There is no Defense Ignore here, because I assume it will always be on (BiS), so we calcualte only the other 4 substats slots
# As for Armor Pen - I assume it's worse than everything else, also because this doesn't calculate damage to target, only Effective Attack before damage reductions, which isn't effected by Armor Pen

s_atk = (35,32,25,25,25)
s_atk_up = (0.0454,0.0409, 0.0318, 0.0318, 0.0318 )
s_crit = (0.0222, 0.0200, 0.0155, 0.0155, 0.0155)
s_cd = (0.0357, 0.0321, 0.0250,0.0250,0.0250)


# If you want to calculate the Effective Attack with these substats comment out the ones with 0s (add: #)
s_paap = (250,225,175,175,175) # Physical Additional Attack Power 1 - Airborne, Break, Knockdown, Stun
s_paap = (0, 0, 0, 0, 0)
s_paap_2 = (250,225,175,175,175) # Physical Additional Attack Power 2  - this one has to be added to SUBSTATS (it's removed for faster calculations (also it VERY VERY NICHE to use both))
s_paap_2 = (0, 0, 0, 0, 0)
s_eaap = (125, 112, 87,87,87) # Elemental Additional Attack Power 1 - Bleed, Burn, Frost, Shock, Poison 
s_eaap = (0, 0, 0, 0, 0)


# Status Additional Attack Power Increase (same as Attack Power Up, but for Status Additional Attack Power) - "Status Additional Attack Power Up"
s_saai = (0.0555, 0.0500,  0.0388, 0.0388, 0.0388) 
#s_saai = (0, 0, 0, 0, 0) 


# All Status Additional Attack Power - gives Status Additional Attack Power PER status
s_asaap = (110, 100, 76, 76, 76) # values if 2 statuses are up
s_asaap = (55, 50, 38, 38, 38) # 1 status
s_asaap= (0, 0, 0, 0, 0)

# Character specific stats

# Karma

# if you use a food buff that gives atk_up (or atk_up set), you can add it here 
k_atk_up = 0.0
# Status Additional Attack Power from Karma, NOT DAMAGE!
k_status_1 = 0.0
k_status_2 = 0.0

# atk_up from titles (max value: 0.1160)
t_atk_up = 0.1160


# The values you see on your character screen (no equipment, but WITH Karma on)
# Naked values (with karma on (and Bart food buff (100 AP)))
# Since this only calculates Effective Attack, if you are going to use the crit rate set, you have to add the set bonus to the char_crit variable

char_base = 2699 / (1.0 + k_atk_up + t_atk_up) # to get the real base value
char_crit = 0.42
char_cd = 0.8230

# TO START
# Press F5 (or w/e shortcut you have to run it)

base = char_base
SUBSTATS = ("atk", "atk_up", "crit", "cd", "paap", "eaap", "saai", "asaap") # you can remove the Substats you do not want (if you want it to calculate faster)

def eff_atk(s):
    """
    s = (atk_up, flat_atk, crit, cd, status_flat, status_pct)
    flat_atk already includes atk_rune values and s_atk values.
    """
    atk_up, flat_atk, crit, cd, status_flat, status_pct = s

    atk_up_total = 1.0 + k_atk_up + t_atk_up + atk_up 
    crit_total = min(char_crit  + crit, 1.0)
    cd_total = char_cd  + cd
    status_total = (status_flat + k_status_1 + k_status_2) * (1.0 + status_pct)
    

    return (
        ((base + flat_atk) * atk_up_total + status_total) * (1.0 + crit_total * cd_total)

    )

    """
    old equation:

    base * (atk_up_total * (1.0 + flat_atk / base) + status_total / base) * (1.0 + crit_total * cd_total)

    """

def pareto_filter(opts):
    """
    Remove options that are strictly dominated inside the same item.
    If option A has all stats >= option B, B can never be useful.
    """
    filtered = []
    n = len(opts)

    for i in range(n):
        s1, d1 = opts[i]
        dominated = False

        for j in range(n):
            if i == j:
                continue
            s2, d2 = opts[j]

            if all(s2[k] >= s1[k] for k in range(6)) and any(
                s2[k] > s1[k] for k in range(6)
            ):
                dominated = True
                break

        if not dominated:
            filtered.append((s1, d1))

    return filtered


def build_pieces():
    pieces = []

    for i in range(5):
        opts = []

        for main in ("atk_up", "crit", "cd","saai"):
            for sub_combo in itertools.combinations(SUBSTATS, 4): # you can change the number of substats to calculate

                
                for rune in ("atk", "crit", "cd"):
                    atk_up_add = 0.0
                    flat_atk_add = 0.0
                    crit_add = 0.0
                    cd_add = 0.0
                    status_flat_add = 0.0
                    status_pct_add = 0.0

                    # Mainstat
                    if main == "atk_up":
                        atk_up_add += m_atk_up[i]
                    elif main == "crit":
                        crit_add += m_crit[i]
                    elif main == "cd":
                        cd_add += m_cd[i]

                    # Substats
                    for s in sub_combo:
                        if s == "atk":
                            flat_atk_add += s_atk[i]
                        elif s == "atk_up":
                            atk_up_add += s_atk_up[i]
                        elif s == "crit":
                            crit_add += s_crit[i]
                        elif s == "cd":
                            cd_add += s_cd[i]
                        elif s == "paap":
                            status_flat_add += s_paap[i]
                        elif s == "paap_2":
                            status_flat_add += s_paap_2[i]    
                        elif s == "eaap":
                            status_flat_add += s_eaap[i]
                        
                        elif s == "saai":
                            status_pct_add += s_saai[i]
                        elif s== "asaap":
                            status_flat_add += s_asaap[i]
                        
                         

                    # Rune
                    if rune == "atk":
                        flat_atk_add += atk_rune
                    elif rune == "crit":
                        crit_add += crit_rune
                    elif rune == "cd":
                        cd_add += cd_rune

                    stats = (
                        atk_up_add,
                        flat_atk_add,
                        crit_add,
                        cd_add,
                        status_flat_add,
                        status_pct_add,
                    )
                    desc = (main, sub_combo, rune)
                    opts.append((stats, desc))

        opts = pareto_filter(opts)
        pieces.append(opts)

    return pieces

def beam_search(pieces, beam_width=5000, top_n=5): #displays the top 5 results
    states = [((0.0,) * 6, ())]

    for depth, opts in enumerate(pieces):
        new_states = []
        for cur, ch in states:
            for stats, desc in opts:
                nc = tuple(cur[j] + stats[j] for j in range(6))
                new_states.append((nc, ch + (desc,)))

        if len(new_states) > beam_width:
            new_states = heapq.nlargest(
                beam_width, new_states, key=lambda x: eff_atk(x[0])
            )
        states = new_states

    states.sort(key=lambda x: eff_atk(x[0]), reverse=True)

    # Dedup: two builds with the same totals have the same eff_atk,
    # no matter how the choices are distributed across interchangeable items.
    seen = set()
    unique = []
    for totals, choices in states:
        key = tuple(round(t, 6) for t in totals)
        if key in seen:
            continue
        seen.add(key)
        unique.append((totals, list(choices)))
        if len(unique) >= top_n:
            break

    return unique

def main():
    pieces = build_pieces()

    print("Options per item after pareto filter:")
    for i, p in enumerate(pieces):
        print(f"  Item {i}: {len(p)}")
    print()

    top5 = beam_search(pieces, beam_width=5000)

    for rank, (stats, choices) in enumerate(top5, 1):
        e = eff_atk(stats)
        print(f"Rank {rank}: eff_atk = {e:.4f}")
        ITEM_NAMES = ("Chest", "Legs", "Head", "Hands", "Boots")
        for i, (main, sub_combo, rune) in enumerate(choices, 0):
            print(
                #f"  Item {i}: main={main}, "
                f" {ITEM_NAMES[i]:<5} main={main:<6} / "
                f"sub={', '.join(sub_combo):<28} / rune={rune}"
            )

        atk_up, flat_atk, crit, cd, sf, sp = stats
        atk_up_total = k_atk_up + t_atk_up + atk_up
        crit_total = char_crit + crit
        cd_total =  char_cd + cd
        status_total = sf * (1.0 + sp)

        print(
            f"  Totals: atk_up={atk_up_total:.4f}, "
            f"flat_atk={flat_atk:.1f}, "
            f"crit={crit_total:.4f}, "
            f"cd={cd_total:.4f}, "
            f"status={status_total:.1f}"
        )
        print()


if __name__ == "__main__":
    main()
