import numpy as np
import resourcespetialitation as rs
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
mpl.rcParams['animation.writer'] = 'avconv'


#Define the species

#specie 1
birthR = 0.21 #intrinsic per-capita offspring rate (birth rate)
deadR = 0.2	#intrinsic per capita dead rate
mainResource = 6 #label of its principal resource
NoResources = 10 # Size of the niche i.e. number of diferent resources
variance = 3.0 #variance of a normal distribution
SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #Distribution (Object) ( dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
species1 = rs.species(birthR,deadR,mainResource,SpeciesResourceSpecialization) # 

#specie 2
deadR = 0.2	#intrinsic per capita dead rate
offspringR = 0.21 #intrinsic per-capita offspring rate (birth rate)
NoResources = 10 # Size of the niche i.e. number of diferent resources
variance = 3.0 #variance of a normal distribution
SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #Distribution (Object) (of dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
mainResource = 13 #label of its principal resource
species2 = rs.species(offspringR,deadR,mainResource,SpeciesResourceSpecialization) # 
                     
#Create the populations
NoIndividuals = 1000
population1 = rs.generatePopulation( species1, NoIndividuals )
population2 = rs.generatePopulation( species2, NoIndividuals )

#Instance a space resource and insert the populations in it
SizeOfResourceSpace = 20
ResourceSpace = rs.resourceSpace(SizeOfResourceSpace)
Capacity = rs.distribution('constant', np.full_like(ResourceSpace.space,1000))
ResourceSpace.bindResoucesCapacity(Capacity)
ResourceSpace.InsertPopulation(population1)
ResourceSpace.InsertPopulation(population2)

#Create Simulation object from inital ResourceSpace ----------

Simulation = rs.simulation(ResourceSpace)

#Evolve the sistem

#animation
fig, ax = plt.subplots()
ax = plt.axes(xlim=(0, 20), ylim=(0, 1000))
line1, = ax.plot([ len(rs.filterbyspecies(y,species1)) for y in Simulation.ResourceSpace.space])
line2, = ax.plot([ len(rs.filterbyspecies(y,species2)) for y in Simulation.ResourceSpace.space] )

def animate(i):
    label = 'timestep {0}'.format(i)
    Simulation.evolve(10.0)
    line1.set_ydata([ len(rs.filterbyspecies(y,species1)) for y in Simulation.ResourceSpace.space])
    line2.set_ydata([ len(rs.filterbyspecies(y,species2)) for y in Simulation.ResourceSpace.space])
    ax.set_xlabel(label)
    return line1, line2
    
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2   

#ani = animation.FuncAnimation(fig, animate, np.arange(1, 10), init_func=init,
#                              interval=25, blit=True)               
print 'generating animation ...'
ani = animation.FuncAnimation(fig, animate, np.arange(1,30),interval=10)
#plt.show()
print 'writing file ...'
try:
	#ani.save(Simulation.dir() + 'basic_animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
	ani.save(Simulation.dir() + 'animation.mp4', fps=10) 
except TypeError:
	print "error en simulacion ignorado"
finally:
	print "otro error"
	
print 'Resalvando simulacion'
Simulation.save()
print 'done'



