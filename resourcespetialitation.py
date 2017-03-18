import numpy as np
import random
import os
import dataset
import json

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
		
		:var meta_time: "Metabolic Time of the species" rate of events of the individuals of this species (birthR + deathR)
		:vartype meta_time: float
	"""
	
	def __init__(self, birthR,deadR,mainResource,ResourceSpecialization):
		
		self.id = None
		self.birthR = birthR
		self.deadR = deadR
		self.ResourceSpecialization = self.bindSpecialitation(mainResource,ResourceSpecialization.dist)
		self.offset = mainResource - len(ResourceSpecialization.dist)/2
		self.distribution = ResourceSpecialization
		self.partition = self.makePartition(np.array(ResourceSpecialization.dist))
		self.meta_time = birthR + deadR
		self.mainResource = mainResource
	
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
		
	def save(self,db,tableName='species'):
		"""
		Store the object to "table" in a SQLlite database if not stored previously
		"""
		table = db[tableName]
		distribution_id=self.distribution.save(db)
		args = dict(birthR=self.birthR, deadR=self.deadR, mainResource=self.mainResource, distribution_id=distribution_id)
		
		row = table.find_one(**args)
		if (row==None):
			row_id = table.insert(args)
		else:
			row_id = row["id"]
			
		self.id = row_id
		return row_id


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
		self.species = species
		self.place_in_list = None
		self.place_in_resource = None
		
class distribution:
	"""
	Represents a distribution
	"""
	
	def __init__(self, name, dist):
		self.name=name
		self.NoResources = len(dist)
		self.moments = [np.sum(dist), np.mean(dist)]
		self.dist=dist
		self.id = None
		
	def save(self,db,tableName='distribution'):
		"""
		Store the object to "table" in a SQLlite database if not stored previously
		"""
		table = db[tableName]
		
		moments_list = []
		for (i,),m in np.ndenumerate(self.moments):
			moments_list.append( (str(int(i)) + ' moment' , m) )
		
		args = dict({'name': self.name, 'NoResources': self.NoResources})
		args.update(dict(moments_list))
		row = table.find_one(**args)
		if (row==None):
			row_id = table.insert(args)
		else:
			row_id = row["id"]
		self.id = row_id
		return row_id

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
	Returns a "distribution" object representing a discreate distribution of the spacialization variation of a species. Of gaussian shape.
	
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
	Distribution = distribution("Gausssian", SpeciesResourceSpecialization)
	Distribution.moments[1]=mu
	Distribution.moments.append(variance)
	Distribution.NoResources = NoResources
	return Distribution

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
	:vartype individuals: list[individuals]
	:var meta_time: "Metabolic Time of the comunity" Maximun rate of events MAX_OF_SPECIES(birthR + deathR)
	:vartype meta_time: float
	"""
	
	def __init__(self, NoResources):
		self.NoResources = NoResources
		self.space = list([None] for i in xrange(NoResources) )
		self.capacity = distribution('Unlimited', np.array(list(-1 for i in xrange(NoResources) )))
		self.individuals = []
		self.meta_time = -1.0
		self.aux = 0.0
		self.populations = []
		
	def InsertPopulation(self, Population ):
		"""
		Inserts a Population in the resources space
		
		:param Population: The population to be inserted
		:type Population: list[individual]
		"""
		self.populations.append(Population)
		for Individual in Population:
			self.InsertIndividual(Individual)
			
	def InsertIndividual(self,Individual):
		"""
		Inserts an Individual in the resources space
		
		:param Individual: Individual to be inserted
		:type Individual: individual
		"""
		
		if (self.capacity.dist[Individual.resource]<0 or len(self.space[Individual.resource]) < self.capacity.dist[Individual.resource]):
			Individual.place_in_list = len(self.individuals)
			Individual.place_in_resource = len(self.space[Individual.resource])
			self.individuals.append(Individual)
			self.space[Individual.resource].append(Individual)
			if(self.meta_time < Individual.species.meta_time):
				self.meta_time = Individual.species.meta_time
			
	def KillIndividual(self, Individual):
		"""
		Eliminate the Individual from resource space.
		The Individual should previously habe been inserted with InsertIndividual(Individual)
		for this to work.
		A list of the inserted Individuals is in self.individuals
		
		:param Individual: The individual to be eliminate
		:type Individual: individual
		"""
		
		LastInResource = self.space[Individual.resource].pop()
		if not (LastInResource is Individual):
			place = Individual.place_in_resource
			LastInResource.place_in_resource = place
			self.space[Individual.resource][place:(place + 1)] = [LastInResource]

		LastInList = self.individuals.pop()
		if not (LastInList is Individual):
			place = Individual.place_in_list
			LastInList.place_in_list = place
			self.individuals[place:(place + 1)] = [LastInList]
		
	def bindResoucesCapacity(self, ResourcesCapacity):
		"""
		Bind the array characterizing the capacity of each resource to the instance of resourceSpace
		
		:param ResourcesCapacity: The array of capacities of the resources. Should be the same size or larger 
			than the size of the resource space size
		:type ResourcesCapacity: list(int) or numpy.array(int)
		"""
		
		self.capacity = ResourcesCapacity
				

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
	
class simulation:
	"""
	Class to save the simulation parameters to db
	"""
	def __init__(self, ResourceSpace):
		self.NoResources = ResourceSpace.NoResources
		self.capacity = ResourceSpace.capacity
		self.populations = ResourceSpace.populations
		self.duration = 0.0
		self.populations_list = []
		self.id = None
		self.simulation_dir = None
		self.ResourceSpace = ResourceSpace
		
	def save(self, storage='data', table_name='simulation'):
		data_directory = './' + storage + '/'
		if not os.path.exists(data_directory):
			os.makedirs(data_directory)
		
		database_path = 'sqlite:///' + storage + '/IntraspecificVariation.sqlite'  
		db = dataset.connect(database_path)
		
		for p in self.populations:
			p[0].species.save(db)
			if( (p[0].species.id, len(p) ) not in self.populations_list ):
				self.populations_list.append( (p[0].species.id, len(p) ) )
		self.populations_list.sort()
		self.capacity.save(db)
		simulation_param = dict({ 'NoResources' : self.NoResources, 'Capacity (distribution id)': self.capacity.id, 'initial_conditions': json.dumps(self.populations_list)})
		simulationTable = db[table_name]
		row = simulationTable.find_one(**simulation_param)
		if (row==None):
			simulation_param.update(dict({'duration': self.duration}))
			self.id = simulationTable.insert(simulation_param)
		else:
			self.id = row['id']
			if(float(row['duration'])<self.duration):
				print 'hay que actualizar'
				data = dict(id=row['id'], duration=self.duration)
				simulationTable.update(data, ['id'])
		self.simulation_dir = data_directory + str(self.id) + '/'
		if not os.path.exists(self.simulation_dir):
			os.makedirs(self.simulation_dir)
		return self.id
		
	def dir(self):
		if(self.simulation_dir != None):
			return self.simulation_dir
		else:
			self.save()
			return self.simulation_dir
		
	def evolve(self,Time):
		"""
		Todo
		"""
		
		Sweeps = int(Time*self.ResourceSpace.meta_time)
		for i in xrange(Sweeps):
			MCSweep(self.ResourceSpace)
		self.duration = self.duration + Time

	
#Dynamics
		
def Step(resourceSpace):
	"""
    Evolve resourceSpace one computational step
    with birth and dead rates of a randomly choosen individual
    in resourceSpace
    
    :param resourceSpace: The system (resource space) to be updated
    """
    
	rdN = random.randint(0,len(resourceSpace.individuals)-1)
	Active_Individual = resourceSpace.individuals[rdN]
	Active_Species = Active_Individual.species
	rdNfloat = random.random()
	birthR_Probability = Active_Species.birthR/resourceSpace.meta_time
	deadR_Probability = Active_Species.deadR/resourceSpace.meta_time
	if(rdNfloat < birthR_Probability): #new birth
		newIndividual = individual(Active_Species)
		resourceSpace.InsertIndividual(newIndividual)
	elif(rdNfloat <= deadR_Probability + birthR_Probability ):  #death
		resourceSpace.KillIndividual(Active_Individual)
		
def MCSweep(resourceSpace):
    """
    TODO
    """
    
    updates = len(resourceSpace.individuals)
    for i in xrange(updates):
        Step(resourceSpace)
        


#Auxiliaries
def filterbyspecies(seq, species):
    l = [el for el in seq if isinstance(el, individual) and el.species is species ]
    return l
