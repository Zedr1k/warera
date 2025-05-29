
import itertools


####################################################################
########### Pueden ajustar parametros y agregar los ################
########### stats de su equipamiento en esta seccion ###############
####################################################################

STATS_EQUIPAMIENTO = { #stats del equipamiento actual
    "arma_daño": 100,
    "arma_critico": 15,
    "casco_crit_damage": 10,
    "chaleco_armor": 15,
    "pant_armor": 10,
    "botas_dodge": 15,
    "guantes_acc": 20
    
}

MAX_LEVEL = 12 #level del jugador
FOOD_HEALTH = 20 #vida por comida consumida, 10 para pan, 20 para carne o 30 para pescado
COSTO_COMIDA = 2.2 #costo por comida consumida
BATTLE_DURATION = 7 # duracion de la batalla
COSTO_BALAS_GRANDES = 2.11 
COSTO_BALAS_CHICAS = 0.56


#### Aca pueden agregar un set de stats manualmente para comparar con el optimo ####
STATS_MANUALES = [5, #damage 
                  4, #accuracy
                  1, #crit_chance
                  1, #crit_damage
                  0, #armor
                  5, #hp
                  0, #hambre
                  3] #dodge

####################################################################


STATS_BASE = {
    "damage": 100,
    "accuracy": 50,
    "crit_chance": 10,
    "crit_damage": 50,
    "armor": 0,
    "hp": 50,
    "hambre": 4,
    "dodge": 0
}

STATS = {
    "damage": (STATS_BASE["damage"]+STATS_EQUIPAMIENTO["arma_daño"], 20),
    "accuracy": (STATS_BASE["accuracy"]+STATS_EQUIPAMIENTO["guantes_acc"], 5),
    "crit_chance": (STATS_BASE["crit_chance"]+STATS_EQUIPAMIENTO["arma_critico"], 5),
    "crit_damage": (STATS_BASE["crit_damage"]+STATS_EQUIPAMIENTO["casco_crit_damage"], 10),
    "armor": (STATS_BASE["armor"]+STATS_EQUIPAMIENTO["chaleco_armor"]+STATS_EQUIPAMIENTO["pant_armor"], 4),
    "hp": (50, 10),
    "hambre": (4, 1),
    "dodge": (STATS_BASE["dodge"]+STATS_EQUIPAMIENTO["botas_dodge"], 4)
}

STAT_KEYS = list(STATS.keys())
POINTS_PER_LEVEL = 4

def alloc_cost(k):
    return k * (k + 1) // 2

def total_cost(levels):
    return sum(alloc_cost(lvl) for lvl in levels)

def compute_stats(levels):
    final_stats = {}
    for i, key in enumerate(STAT_KEYS):
        base, inc = STATS[key]
        final_stats[key] = base + inc * levels[i]
    return final_stats

def evaluate_build(stats):
    accuracy = min(stats["accuracy"], 100) / 100
    crit_rate = min(stats["crit_chance"], 100) / 100
    crit_multiplier = 1 + (stats["crit_damage"] / 100)

    expected_damage = stats["damage"] * accuracy * ((1 - crit_rate) + crit_rate * crit_multiplier)

    dodge_chance = min(stats.get("dodge", 0), 100) / 100
    damage_taken = max(0.0001, 10 * (1 - stats["armor"] / 100))
    damage_taken *= (1 - dodge_chance)

    max_hp = stats["hp"]
    max_hambre = stats["hambre"]
    total_hambre = max_hambre
    total_hp = max_hp

    for hour in range(1, BATTLE_DURATION + 1):
        total_hp += max_hp * 0.1
        total_hambre += max_hambre * 0.1

    total_hp += total_hambre * FOOD_HEALTH
    comida_usada = total_hambre
    ataques_totales = total_hp / damage_taken

    return expected_damage * ataques_totales, comida_usada, ataques_totales

def find_best_distribution(levels):
    max_points = POINTS_PER_LEVEL * levels
    best_score = 0
    best_allocation = None

    def backtrack(i, remaining_points, current):
        nonlocal best_score, best_allocation
        if i == len(STAT_KEYS):
            if remaining_points == 0:
                stats = compute_stats(current)
                score, _, _ = evaluate_build(stats)
                if score > best_score:
                    best_score = score
                    best_allocation = (tuple(current), stats, score)
            return

        for lvl in range(0, MAX_LEVEL + 1):
            cost = alloc_cost(lvl)
            if cost <= remaining_points:
                current.append(lvl)
                backtrack(i + 1, remaining_points - cost, current)
                current.pop()

    backtrack(0, max_points, [])
    return best_allocation

def evaluate_custom_distribution(levels):
    if len(levels) != len(STAT_KEYS):
        raise ValueError(f"Se esperaban {len(STAT_KEYS)} valores de nivel. Recibido: {len(levels)}")
    if total_cost(levels) > POINTS_PER_LEVEL * MAX_LEVEL:
        raise ValueError("La distribución excede el total de puntos disponibles.")

    stats = compute_stats(levels)
    score, comida_usada, ataques_totales = evaluate_build(stats)
    return stats, score, comida_usada, ataques_totales

if __name__ == "__main__":
    best = find_best_distribution(MAX_LEVEL)
    if best:
        levels_distribution, final_stats, score = best
        print("Mejor distribución de niveles:")
        for stat, level in zip(STAT_KEYS, levels_distribution):
            print(f"  {stat}: nivel {level}")
        print("\nEstadísticas finales:")
        for stat, value in final_stats.items():
            print(f"  {stat}: {value}")
        score, comida_usada, ataques_totales = evaluate_build(final_stats)
        costo_comida = comida_usada * COSTO_COMIDA
        coto_balas_grandes = ataques_totales * COSTO_BALAS_GRANDES
        costo_balas_chicas = ataques_totales * COSTO_BALAS_CHICAS
        print(f"\nDaño evaluado: {score:.2f}")
        print(f"Comida usada en {BATTLE_DURATION} horas: {comida_usada:.2f}")
        print(f"Costo comida: {costo_comida:.2f}")
        print(f"Ataques totales posibles en {BATTLE_DURATION} horas: {ataques_totales:.2f}")
        print(f"Posible gasto en balas grandes: {coto_balas_grandes:.2f}")
        print(f"Posible gasto en balas chicas: {costo_balas_chicas:.2f}")


    print("\n--- Evaluación manual ---")
    custom_levels = STATS_MANUALES
    try:
        stats, score, comida_usada, ataques_totales = evaluate_custom_distribution(custom_levels)
        print("Build personalizada evaluada:")
        for stat, value in stats.items():
            print(f"  {stat}: {value}")
        costo_comida = comida_usada * COSTO_COMIDA
        coto_balas_grandes = ataques_totales * COSTO_BALAS_GRANDES
        costo_balas_chicas = ataques_totales * COSTO_BALAS_CHICAS
        print(f"\nPuntaje evaluado: {score:.2f}")
        print(f"Comida usada en {BATTLE_DURATION} horas: {comida_usada:.2f}")
        print(f"Costo comida: {costo_comida:.2f}")
        print(f"Ataques totales posibles en {BATTLE_DURATION} horas: {ataques_totales:.2f}")
        print(f"Posible gasto en balas grandes: {coto_balas_grandes:.2f}")
        print(f"Posible gasto en balas chicas: {costo_balas_chicas:.2f}")
    except ValueError as e:
        print(f"Error en build personalizada: {e}")
