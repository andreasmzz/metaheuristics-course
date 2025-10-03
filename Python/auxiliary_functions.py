# Python 3.13.4

# Evaluates the total benefit of packages related to selected dependencies
def evaluate_packs(pack_benefits:list[int], pack_dep:list[tuple[int, int]], select_dep:list[bool]) -> int:
    total_benefits: int = 0
    pack_all_deps: dict[int, set[int]] = get_pack_dict(pack_dep)

    for pack in pack_all_deps:
        if pack_all_deps[pack].issubset(set(i for i in range(len(select_dep)) if select_dep[i])): # if all dependencies of the package are selected
            total_benefits += pack_benefits[pack]

    return total_benefits

def get_remaining_capacity(dep_sizes:list[int], selec_dep:list[bool], capacity:int) -> int:
    used_space: int = sum(dep_sizes[i] for i in range(len(selec_dep)) if selec_dep[i])
    return capacity - used_space

# pack_id -> set of dependencies it needs
def get_pack_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]:
    pack_dict: dict[int, set[int]] = {}
    for (pack, dep) in pack_dep:
        if pack not in pack_dict: # first time seeing this package
            pack_dict[pack] = set()
        pack_dict[pack].add(dep)
    return pack_dict

# dep_id -> set of packages that depend on it
def get_dep_dict(pack_dep:list[tuple[int, int]]) -> dict[int, set[int]]:
    dep_dict: dict[int, set[int]] = {}
    for (pack, dep) in pack_dep:
        if dep not in dep_dict: # first time seeing this dependency
            dep_dict[dep] = set()
        dep_dict[dep].add(pack)
    return dep_dict

# 
def register_results(results: list[list[bool]], pack_benefits:list[int], dep_sizes:list[int], pack_dep:list[tuple[int, int]], capacity:int, terminal:bool=True, external_file:bool=False, file_name:str="results.txt", file_mode:str="a") -> None:
    avaluation_values:list[int] = [evaluate_packs(pack_benefits, pack_dep, sol) for sol in results]
    capacities_left:list[int] = [get_remaining_capacity([dep_size for dep_size in dep_sizes], sol, capacity) for sol in results]
    
    with open(file_name, file_mode) as file:
        for i, sol in enumerate(results):
            if terminal:
                print(f"Solution {i+1}: Benefit = {avaluation_values[i]}, Capacity left = {capacities_left[i]}, Selected dependencies = {[index for index, val in enumerate(sol) if val]}")
            if external_file:
                file.write(f"Solution {i+1}: Benefit = {avaluation_values[i]}, Capacity left = {capacities_left[i]}, Selected dependencies = {[index for index, val in enumerate(sol) if val]}\n")
    pass
