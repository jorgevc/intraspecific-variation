import numpy as np
import random

class species:
	"""
	Represents a species
		
		:param birthR: Birth rate of species's individuals
		:param deadR: Dead rate of species's individuals
		:param mainResource: the central resouce of the specie
		:param ResourceSpecialization: Distribution of resource variation around the mainResource
		:param id: id of the specie
		:type birthR: float
		:type deadR: float
		:type mainResource: int
		:type ResourceSpecialization: array[float]
		:type id: int
		:return: objet describing a species
		:rtype: species
	"""
	
	def __init__(self, birthR,deadR,mainResource,ResourceSpecialization,id):
		
		self.id = id
		self.birthR = birthR
		self.deadR = deadR
		self.ResourceSpecialization = self.bindSpecialitation(mainResource,ResourceSpecialization)
		self.offset = mainResource - len(ResourceSpecialization)/2
		self.distribution = np.array(ResourceSpecialization)
		self.partition = self.makePartition(ResourceSpecialization)

	def bindSpecialitation(self,mainResource,ResourceSpecialization): #to deprecate ?
		"""
		Relocates the resource spetialitation distribution to a absolute position
		where the mainResource is in the center of the distribution given by Resourcespecialization
		
		:param mainResource: location of the Resouce distribution
		:param ResourceSpecialization: distribution of specialization
		:type mainResource: int
		:type ResourceSpecialization: array[float]
		:return: array of float representing the resource specialitation in absolute position
		:rtype: array[float]
		"""
		
		specialitation = []
		mid = len(ResourceSpecialization)/2
		for i in range(0,len(ResourceSpecialization)):
			if(i + mid >= mainResource and i + mid - mainResource < len(ResourceSpecialization)):
				specialitation.append(ResourceSpecialization[i + mid - mainResource])
			else:
				specialitation.append(0.0)
		return np.array(specialitation)
		
	def makePartition(self, ResourceSpecialization):
		"""
		Returns an array of cumulative probability of the Resoucespecialization distribution
		
		:param ResourceSpecialization: Discreate distribution representing the variability of resources specialitation
		:type ResourceSpecialization: array[float]
		:return: Discreate cumulative probability
		:rtype: array[float]
		"""
		partition = []
		partition.append(ResourceSpecialization[0])
		for i in range(1, len(ResourceSpecialization)):
			cumulative = partition[i-1] + ResourceSpecialization[i]
			partition.append(cumulative)
		return np.array(partition)


def gaussian( x, mu, var):
	"""
	Returns the value of evaluating a gaussian `exp((x-mu)^{2}/2var^{2})`
	
	:type x: float
	:type mu: float
	:type var: float
	:rtype: float
	"""
	return np.exp(-np.power(x - mu, 2.) / (2 * np.power(var, 2.)))

def gaussianSpecialization(NoResources,variance):
	"""
	Returns a np array representing a discreate distribution of the spacialization variation of a species. Of gaussian shape.
	
	:param NoResources: Width of the distribution
	:param variance: Variance of the gaussian distribution
	:type NoResources: int
	:type variance: float
	:rtype: np array
	"""
	SpeciesResourceSpecialization = np.zeros(NoResources)
	mu = ((NoResources/2.0) + 0.5) - 1.0
	for i in range(0,NoResources):
		SpeciesResourceSpecialization[i] = (gaussian(i-0.5,mu,variance) + gaussian(i+0.5,mu,variance))/2.0
	SpeciesResourceSpecialization = SpeciesResourceSpecialization/np.sum(SpeciesResourceSpecialization)
	return SpeciesResourceSpecialization

class resourceSpace:
	"""
	Represent the resource space where individuals are
	
	:param NoResources: Size of the space
	:type NoResources: int
	
	:var NoResources: size of the resources space
	:vartype NoResources: int
	:var space: list of list. The position in the list represent the resource, the list there is a list
	 of individuals with that specialization.
	:vartype space: list[list[individual]]
	:var capacity: array indicating the maximun number of individuals allowed per resource
	:vartype capacity: array[int]
	:var individuals: Unordered list of individuals in the resource space
	:vartype individuals: list[species]
	"""
	
	def __init__(self, NoResources):
		self.NoResources = NoResources
		self.space = list([None] for i in xrange(NoResources) )
		self.capacity = list(-1 for i in xrange(NoResources) )
		self.individuals = []
		
	def InsertPopulation(self, Population ):
		"""
		Inserts a Population in the resources space
		
		:param Population: The population to be inserted
		:type Population: list[individual]
		"""
		
		for Individual in Population:
			self.InsertIndividual(Individual)
			
	def InsertIndividual(self,Individual):
		"""
		Inserts an Individual in the resources space
		
		:param Individual: Individual to be inserted
		:type Individual: individual
		"""
		
		if (self.capacity[Individual.resource]<0 or len(self.space[Individual.resource]) < self.capacity[Individual.resource]):
			Individual.place_in_list = len(self.individuals)
			Individual.place_in_resource = len(self.space[Individual.resource])
			self.individuals.append(Individual)
			self.space[Individual.resource].append(Individual)
			
	def KillIndividual(self, Individual):
		"""
		Eliminate the Individual from resource space.
		The Individual should previously habe been inserted with InsertIndividual(Individual)
		for this to work.
		A list of the inserted Individuals is in self.individuals
		
		:param Individual: The individual to be eliminate
		:type Individual: individual
		"""
		
		del self.space[Individual.resouce][Individual.place_in_resource]
		del self.individuals[Individual.place_in_list]
		
	def bindResoucesCapacity(ResourcesCapacity):
		"""
		Bind the array characterizing the capacity of each resource to the instance of resourceSpace
		
		:param ResourcesCapacity: The array of capacities of the resources. Should be the same size or larger 
			than the size of the resource space size
		:type ResourcesCapacity: list(int) or numpy.array(int)
		"""
		
		self.capacity = np.array(ResourcesCapacity)
				
class individual:
	"""
	Represents a single individual
	
	:param species: the specie of the indiviudal to be instanced
	:type species: species
	:var resource: the resource specialitation of this individual
	:vartype resource: int
	:var species: Its species id
	:vartype species: int
	:var place_in_list: place (index) in the list resourceSpace.individuals
	:vartype place_in_list: int
	:var place_in_resource: index in list resourceSpace.space[resource][index] where the individual is located
	:vartype place_in_resource: int
	"""
	
	def __init__(self, species):
		partLenght = len(species.partition)
		rdN =random.uniform(0.0,species.partition[partLenght-1])
		for i in xrange(partLenght):
			if rdN <= species.partition[i]:
				resource = i
				break
		resource = resource + species.offset
		self.resource = resource
		self.species = species.id
		self.place_in_list = None
		self.place_in_resource = None

def generatePopulation( species, NoIndividuals ):
	"""
	Returns a list of individuals of a given species
	
	:param species: the species of the generated individuals
	:type species: species
	:param NoIndividuals: Number of individuals to be generated
	:type NoIndividuals: int
	:return: A list of individuals
	:rtype: list[individual]
	"""
	
	population = []
	for i in xrange(NoIndividuals):
		Individual = individual(species)
		population.append(Individual)
	return population
		
def Step(resourceSpace):
	rdN = random.randint(0,len(resourceSpace.individuals))
	rdNfloat = random.random()
	if(rdNfloat < birthR_Probability):
		
	else:
		