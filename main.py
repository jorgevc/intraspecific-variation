import numpy as np
import resourcespetialitation as rs
import matplotlib.pyplot as plt

#Define the species

deadR = 0.1	#intrinsic per capita dead rate
offspringR = 0.2 #intrinsic per-capita offspring rate (birth rate)
NoResources = 10 # Size of the niche i.e. number of diferent resources
variance = 3.0 #variance of a normal distribution
SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #np vector (of dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
mainResource = 2 #label of its principal resource
species1 = rs.species(offspringR,deadR,mainResource,SpeciesResourceSpecialization,1) # 

#Create the populations
NoIndividuals = 1000
population1 = rs.generatePopulation( species1, NoIndividuals )

#Instance a space resource and insert the populations in it
SizeOfResourceSpace = 20
ResourceSpace = rs.resourceSpace(SizeOfResourceSpace)
ResourceSpace.InsertPopulation(population1)

plt.plot(species1.ResourceSpecialization )
plt.show()
plt.plot([ len(y) for y in ResourceSpace.space])
plt.show()
#Evolve the sistem
T=100
#ResourceSpace = rs.evolveSpace(ResourceSpace,T)









