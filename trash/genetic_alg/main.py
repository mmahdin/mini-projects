import numpy as np
import random
from copy import deepcopy
import matplotlib.pyplot as plt

class SudokuGeneticAlgorithm:
    def __init__(self, n, population_size, mutation_rate, crossover_rate, num_generations, selection_type):
        self.n = n
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.num_generations = num_generations
        self.selection_type = selection_type
        self.population = self.initialize_population()
        
    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            individual = np.zeros((self.n, self.n), dtype=int)
            for row in range(self.n):
                individual[row] = np.random.permutation(self.n) + 1
            population.append(individual)
        return population
    
    def fitness(self, individual):
        row_errors = sum([len(set(row)) != self.n for row in individual])
        col_errors = sum([len(set(individual[:, col])) != self.n for col in range(self.n)])
        
        knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        knight_errors = 0
        for i in range(self.n):
            for j in range(self.n):
                for move in knight_moves:
                    ni, nj = i + move[0], j + move[1]
                    if 0 <= ni < self.n and 0 <= nj < self.n:
                        if individual[i][j] == individual[ni][nj]:
                            knight_errors += 1
        print(row_errors, ',  ', col_errors, ',  ', knight_errors)
        return row_errors + col_errors + knight_errors

    def selection(self):
        fitness_scores = np.array([self.fitness(ind) for ind in self.population])
        
        if self.selection_type == 'random':
            selected = random.sample(self.population, self.population_size // 2)
        elif self.selection_type == 'rank':
            sorted_population = [self.population[i] for i in np.argsort(fitness_scores)]
            selected = sorted_population[:self.population_size // 2]
        elif self.selection_type == 'competition':
            selected = []
            for _ in range(self.population_size // 2):
                competitors = random.sample(self.population, 2)
                selected.append(min(competitors, key=lambda ind: self.fitness(ind)))
        elif self.selection_type == 'relative':
            total_fitness = np.sum(fitness_scores)
            selection_probs = (total_fitness - fitness_scores) / total_fitness
            selection_probs /= np.sum(selection_probs)
            selected_indices = np.random.choice(range(self.population_size), size=self.population_size // 2, p=selection_probs)
            selected = [self.population[i] for i in selected_indices]
        
        return selected

    def crossover(self, parent1, parent2):
        if random.random() > self.crossover_rate:
            return parent1, parent2
        crossover_point = random.randint(1, self.n - 1)

        child1 = np.vstack((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = np.vstack((parent2[:crossover_point], parent1[crossover_point:]))
        
        return child1, child2

    def mutate(self, individual):
        for i in range(self.n):
            if random.random() < self.mutation_rate:
                swap_idx = np.random.choice(self.n, 4, replace=False)
                individual[i, swap_idx[0]], individual[i, swap_idx[1]] = individual[i, swap_idx[1]], individual[i, swap_idx[0]]
                # individual[i, swap_idx[2]], individual[i, swap_idx[3]] = individual[i, swap_idx[3]], individual[i, swap_idx[2]]

        return individual

    def evolve(self):
        for generation in range(self.num_generations):
            new_population = self.selection()
            children = []
            while len(children) < self.population_size // 2:
                parents = random.sample(new_population, 2)
                child1, child2 = self.crossover(parents[0], parents[1])
                children.extend([self.mutate(child1), self.mutate(child2)])
            self.population = new_population + children
            # print(f"Generation {generation} best fitness: {min([self.fitness(ind) for ind in self.population])}")

    def display_individual(self, individual):
        plt.imshow(individual, cmap='viridis')
        plt.colorbar()
        plt.show()

# Parameters
n = 9  # Sudoku size
population_size = 120
mutation_rate = 0.1
crossover_rate = 0.7
num_generations = 10000
selection_type = 'rank'  # can be 'random', 'rank', 'competition', 'relative'

sudoku_ga = SudokuGeneticAlgorithm(n, population_size, mutation_rate, crossover_rate, num_generations, selection_type)
sudoku_ga.evolve()
