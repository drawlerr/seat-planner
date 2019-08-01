import csv
from collections import Counter

from constraint import *


def swap_kv_list(d):
    r = {}
    for k, v in d.items():
        if r.get(v) is None:
            r[v] = [k]
        else:
            r[v].append(k)
    return r


sols_seen = set()


def print_solution(s):
    sol = swap_kv_list(s)
    for t in sorted(sol.keys()):
        tbltext = str(sorted(sol[t]))

        table_title = f"Table {t} ({len(sol[t])} people)"
        print(table_title)
        if tbltext in sols_seen:
            print("(previously seen table!)")
        sols_seen.add(tbltext)

        print('=' * len(table_title))
        for p in sorted(sol[t]):
            print(p)
        print()


class MaxPerTableConstraint(Constraint):
    def __init__(self, max_per_table):
        self._max_per_table = max_per_table

    def __call__(self, variables, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        counter = Counter()
        for variable in variables:
            value = assignments.get(variable, _unassigned)
            if value is not _unassigned:
                if counter[value] >= self._max_per_table:
                    return False
                counter[value] += 1

        if forwardcheck:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    for v in domain:
                        if counter[v] > self._max_per_table:
                            domain.hideValue(v)
                            if not domain:
                                return False
        return True


class SameTableConstraint(Constraint):
    """
    After one name has been assigned, make sure the other ends up at same table.
    """
    def __init__(self, name1, name2):
        self._names = (name1, name2)

    def __call__(self, variables, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        value = assignments.get(self._names[0], _unassigned)
        value2 = assignments.get(self._names[1], _unassigned)

        if value is not _unassigned:
            if value2 is not _unassigned and value2 != value:
                return False

        if forwardcheck:
            if value is not _unassigned and value2 is _unassigned:
                domain2 = domains[self._names[1]]
                for v in domain2[:]:
                    if v != value:
                        domain2.hideValue(v)
            if value2 is not _unassigned and value is _unassigned:
                domain = domains[self._names[0]]
                for v in domain[:]:
                    if v != value2:
                        domain.hideValue(v)
        return True


class DifferentTableConstraint(Constraint):
    """
    After one name has been assigned, make sure the other ends up at same table.
    """
    def __init__(self, name1, name2):
        self._names = (name1, name2)

    def __call__(self, variables, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        value = assignments.get(self._names[0], _unassigned)
        value2 = assignments.get(self._names[1], _unassigned)

        if value is not _unassigned:
            if value2 is not _unassigned and value2 == value:
                return False

        if forwardcheck:
            if value is not _unassigned and value2 is _unassigned:
                domain2 = domains[self._names[1]]
                for v in domain2[:]:
                    if v == value:
                        domain2.hideValue(v)
            if value2 is not _unassigned and value is _unassigned:
                domain = domains[self._names[0]]
                for v in domain[:]:
                    if v == value2:
                        domain.hideValue(v)
        return True


def main():
    guests = set()
    prefer = []
    avoid = []
    with open("guests") as f:
        for l in f:
            guests.add(l.strip())
    with open("prefer.csv") as f:
        reader = csv.reader(f)
        for r in reader:
            prefer.append((r[0].strip(), r[1].strip()))
    with open("avoid.csv") as f:
        reader = csv.reader(f)
        for r in reader:
            avoid.append((r[0].strip(), r[1].strip()))

    # subset for profiling
    # guests = list(sorted(guests))[:10]
    num_tables = 4
    print("Guests:")
    print(guests)
    total_guests = len(guests)
    per_table = int((total_guests+1)/num_tables) + 1
    print(f"Total guests: {total_guests} per table: {per_table}")

    problem = Problem()
    problem.addVariables(guests, range(1, num_tables+1))
    problem.addConstraint(MaxPerTableConstraint(per_table))
    for p in prefer:
        if p[0] in guests and p[1] in guests:
            problem.addConstraint(SameTableConstraint(*p))
        else:
            if p[0] not in guests:
                raise Exception(f"{p[0]} not in guests!")
            if p[1] not in guests:
                raise Exception(f"{p[1]} not in guests!")
    for a in avoid:
        if a[0] in guests and a[1] in guests:
            problem.addConstraint(DifferentTableConstraint(*a))
        else:
            if a[0] not in guests:
                raise Exception(f"{a[0]} not in guests!")
            if a[1] not in guests:
                raise Exception(f"{a[1]} not in guests!")
    solution = problem.getSolution()
    if solution is None:
        print("no solution?")
        return

#    print("At least one solution!")
#    print_solution(solution)

    print("\nSolutions:\n")
    solutions = problem.getSolutionIter()
    num_solutions = 0
    for s in solutions:
        num_solutions += 1
        print(f"Solution #{num_solutions}:")
        print_solution(s)
        print()
        if num_solutions > 10:
            break


if __name__ == "__main__":
    main()
