import random

# Building suitability matrix, this contains the suitability of each building for each use
BUILDING_SUITABILITY = [[35, 10, 12, 7, 12, 24, 15],
                        [30, 14, 16, 25, 25, 29, 28],
                        [18, 22, 21, 29, 27, 37, 37],
                        [20, 34, 27, 26, 26, 34, 28],
                        [24, 26, 35, 15, 15, 37, 29],
                        [24, 19, 25, 24, 24, 20, 23],
                        [18, 22, 30, 25, 27, 21, 19],
                        [33, 29, 22, 25, 25, 25, 33]]


class State(object):
    """
    The state class is a configuration that is used to create
    a generations population
    """
    MUTATION = 0.8

    def __init__(self, parents=None, generation=1):
        r = random.Random()
        self._fitness = 0
        self._probability = None
        self.generation = generation

        # If the state has no parents, signifying its a 1st generation that
        # it should create a random state
        if parents is None:
            self.parents = None
            self.state = r.sample(range(0, 8), 8)

        # If the state has parents then this means its a descendant
        # of a generation, this allows for crossover and mutation
        # to be applied to create the population
        else:
            parent1 = parents[0]
            parent2 = parents[1]
            self.parents = parents
            self.state = self.crossover(parent1, parent2)
            self.mutate()

    def __str__(self):
        """
        Returns the state of the configuration in a string
        representation of the array
        """
        return ''.join(str(e) for e in self.state)

    def fitness(self):
        """
        This method calculates the fitness by iterating through the state
        and adding the corresponding data from the BUILDING_SUITABILITY matrix
        to the fitness total.
        """

        # If the fitness has not been calculated we need to do this
        if not self._fitness:
            state = self.state

            # Enumerate over the state and get the relevant index for the BUILDING_SUITABILITY
            # matrix and add it to the fitness
            for i, col in enumerate(state):
                if col != 0:
                    self._fitness += BUILDING_SUITABILITY[i][col - 1]

        return self._fitness

    def probability(self, population):
        """
        Method that calculates the probability of this configuration being selected
        using the roulette wheel technique, the greater the fitness the greater
        probability it is selected.
        """
        if not self._probability:
            self._probability = self.fitness() / sum([x.fitness() for x in population])

        return self._probability

    def crossover(self, parent1, parent2):
        """
        Crossover function that create a new chromosome by using a
        random single index to split the chromosomes. This is not naive
        so it ensures that any new chromosomes created do not have invalid
        states with repeating genes, this is because if a gene is already present
        then it will move to the next and not duplicate a gene value.
        """

        # Create random number to represent index where crossover will split
        r = random.Random()
        crossover_index = r.randint(0, 8)

        # Separate the parents into left and right using the random index position
        left = parent1.state[0:crossover_index]
        right = parent2.state[crossover_index:8]

        # Extend the right chromosome to contain both parent slices
        right.extend(parent2.state[0:crossover_index])
        right.extend(parent1.state[crossover_index:8])

        j = len(left)
        k = 0

        # Iterate unit j is equal to the parent1 chromosomes length
        while j < len(parent1.state):

            # Check if k iterator is equal to rights length
            if k < len(right):

                # Check to ensure that the right gene is not present in the left proportion,
                # if it isnt then we append it to the chromosome and continue iterating other
                # the list, if its present will skip and continue iterating
                if not (right[k] in left):
                    left.append(right[k])
                    j += 1
                k += 1

            # If the iterator has reached the end of the chromosome then we attach the
            # right side to the left and set the termination condition to the length of
            # the parent chromosome to terminate the loop
            else:
                a = len(parent1.state) - j
                pos = len(right) - (8 - crossover_index) - crossover_index + 1
                left.extend(right[pos:pos + a])
                j = len(parent1.state)

        return left

    def mutate(self):
        """
        Mutation method used to swap two genes in a chromosome, this method allows for
        only valid solutions to occur as it swaps two genes around instead of randomly
        changing the value of one which would lead to conflicts.
        """
        k = 0
        i = 0
        pos = []

        # Loop to produce the position of the two genes that will
        # be swapped for the mutation
        while (i < len(self.state)) and (k <= 1):
            # Generate a random number between 0 - 1, if the value is less than
            # the chromosomes mutation rate, then select the current iterations
            # position for mutation, else continue iterating through the chromosome
            if random.random() < self.MUTATION:
                pos.append(i)
                k += 1
            i += 1

        # If two genes have been selected for mutating then swap the
        # value of the genes, if two genes have not been flagged for
        # mutating no action will be taken.
        if k == 2:
            ind1 = pos[0]
            ind2 = pos[1]
            temp = self.state[ind1]
            self.state[ind1] = self.state[ind2]
            self.state[ind2] = temp


def roulette_selection(population_probability):
    """
    This is the roulette function that selects individuals using the roulette wheel
    selection method, it takes in a list of the populations probality of being selected,
    which represents their proportion of the populations total fitness
    :param population_probability: list of chromosomes proportion of populations total fitness
    """
    i = 0
    selected_state = None
    accumulated_fitness = 0
    random_number = random.random()

    # Iterate through the chromosomes proportion of populations
    # total fitness.
    while selected_state is None:
        # Select the current chromosome from the list
        current = population_probability[i]

        # Add the current chromosome fitness proportion to the accumulated fitness, then compare
        # it to the random number between 0 - 1 created, if the current accumulated proportion
        # is greater than the random number return the current chromosome
        accumulated_fitness += current[0]
        if accumulated_fitness >= random_number:
            return current[1]


def create_new_population(population, population_size):
    """
    Function that created a new generation of population, it calculates the
    current populations proportion of the total fitness and then uses the
    roulette_selection() function to select two parents to be used for a
    new chromosome
    """
    new_population = []

    # Create new population until it reaches the specified size
    while len(new_population) < population_size:
        # Create the value of probability that each individual will be selected
        population_by_probability = [(x.probability(population), x) for x in population]

        # Pick random individual from population using the probability calculated previously, remove parent from list
        parent1 = roulette_selection(population_by_probability)
        population_by_probability = [x for x in population_by_probability if x[1] != parent1]

        # Pick the second parent at random from the remaining individuals
        parent2 = roulette_selection(population_by_probability)

        # Attach the two individuals to the new population
        new_population.append(State((parent1, parent2), parent1.generation + 1))

    return new_population


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Initialise algorithm conditions
    population_size = 100
    generation = 1
    no_improvement = 0

    # Placeholder for the solution with the best result found
    solution = State(generation=0)

    # Initialise population pool
    population = [State(generation=generation) for x in range(population_size)]

    # Run the genetic algorithm until there has been no improvement in
    # the population for x iterations
    while no_improvement <= 100:

        # Get the fittest chromosome from the current population and increment
        # the termination condition
        generation_fittest = max(population, key=lambda State: State.fitness())
        no_improvement += 1

        # If the current generations fittest chromosome is an improvement
        # on the one previously found then store and reset the termination condition
        if generation_fittest.fitness() > solution.fitness():
            solution = generation_fittest
            no_improvement = 0

        # Print the general details about each generation
        print('Generation: %d' % generation)
        print('Best State: %s' % generation_fittest)
        print('Max Fitness: %d' % generation_fittest.fitness())

        # Create a new generation
        population = create_new_population(population, population_size)
        generation += 1

        # Uncomment if you wish to see the breakdown of the chromosomes
        # in each generational population
        # for x in population:
        #     if x.parents is not None:
        #         print('---------------------')
        #         print('Parents: ')
        #         print(x.parents[0])
        #         print(x.parents[1])
        #         print('State:')
        #         print(x.state)
        #         print('Fitness:')
        #         print(x.fitness())
        #         print('---------------------')

    # Print info on the fittest chromosome found
    print('Solution State: ')
    print(solution.state)
    print('Solution Generation: ')
    print(solution.generation)
    print('Solution Fitness: ')
    print(solution.fitness())
