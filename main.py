import random


BUILDING_SUITIBILITES = [[35, 10, 12, 7, 12, 24, 15],
                         [30, 14, 16, 25, 25, 29, 28],
                         [18, 22, 21, 29, 27, 37, 37],
                         [20, 34, 27, 26, 26, 34, 28],
                         [24, 26, 35, 15, 15, 37, 29],
                         [24, 19, 25, 24, 24, 20, 23],
                         [18, 22, 30, 25, 27, 21, 19],
                         [33, 29, 22, 25, 25, 25, 33]]


class State(object):
    MUTATION = 0.5

    def __init__(self, parents=None, generation=1):
        r = random.Random()
        self._fitness = 0
        self._probability = None
        self.generation = generation

        if parents is None:
            self.parents = None
            self.state = r.sample(range(0, 8), 7)

        else:
            parent1 = parents[0]
            parent2 = parents[1]
            self.parents = parents
            self.state = self.crossover(parent1, parent2)
            self.mutate()

    def __str__(self):
        return ''.join(str(e) for e in self.state)

    def fitness(self):
        if not self._fitness:
            state = self.state

            for i, col in enumerate(state):
                if col != 0:
                    self._fitness += BUILDING_SUITIBILITES[i][col-1]

        return self._fitness

    def probability(self, population):
        if not self._probability:
            self._probability = self.fitness() / sum([x.fitness() for x in population])

        return self._probability

    def crossover(self, parent1, parent2):
        r = random.Random()
        crossover_index = r.randint(0, 8)
        left = parent1.state[0:crossover_index]
        right = parent2.state[crossover_index:8]
        right.extend(parent2.state[0:crossover_index])
        right.extend(parent1.state[crossover_index:8])

        j = len(left)
        k = 0

        while j < len(parent1.state):
            if k < len(right):
                if not (right[k] in left):
                    left.append(right[k])
                    j += 1
                k += 1
            else:
                a = len(parent1.state) - j
                pos = len(right) - (8 - crossover_index) - crossover_index + 1
                left.extend(right[pos:pos+a])
                j = len(parent1.state)

        return left

    def mutate(self):
        k = 0
        i = 0
        pos = []

        while (i < len(self.state)) and (k <= 1):
            if random.random() < self.MUTATION:
                pos.append(i)
                k += 1
            i += 1

        if k == 2:
            ind1 = pos[0]
            ind2 = pos[1]
            temp=self.state[ind1]
            self.state[ind1] = self.state[ind2]
            self.state[ind2] = temp


def pick_random(population_probability):
    i = 0
    selected_state = None

    while selected_state == None:
        current = population_probability[i]

        if current[0] <= random.random():
            return current[1]

        if i + 1 <= len(population_probability):
            i = 0
        else:
            i += 1


def create_new_population(population, population_size):
    new_population = []

    while len(new_population) < population_size:
        population_by_probability = [(x.probability(population), x) for x in population]

        parent1 = pick_random(population_by_probability)
        population_by_probability = [x for x in population_by_probability if x[1] != parent1]

        parent2 = pick_random(population_by_probability)
        new_population.append(State((parent1, parent2), parent1.generation + 1))

    return new_population


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    population_size = 10
    generation = 1
    population = [State(generation=generation) for x in range(population_size)]

    while not 200 in [x.fitness() for x in population]:
        print('Generation %d Max Fitness: %d' % (generation, max([x.fitness() for x in population])))
        population = create_new_population(population, population_size)
        generation += 1

    for x in population:
        # if x.fitness() == 350:
        if x.parents is not None:
            print('Parents: ')
            print(x.parents[0])
            print(x.parents[1])

        print('Solution State:')
        print(x)