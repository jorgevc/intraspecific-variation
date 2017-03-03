import numpy as np
import resourcespetialitation as rs
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
mpl.rcParams['animation.writer'] = 'avconv'

#Define the species

#specie 1
deadR = 0.2	#intrinsic per capita dead rate
offspringR = 0.25 #intrinsic per-capita offspring rate (birth rate)
NoResources = 10 # Size of the niche i.e. number of diferent resources
variance = 3.0 #variance of a normal distribution
SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #np vector (of dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
mainResource = 6 #label of its principal resource
species1 = rs.species(offspringR,deadR,mainResource,SpeciesResourceSpecialization,1) # 

#specie 2
deadR = 0.2	#intrinsic per capita dead rate
offspringR = 0.25 #intrinsic per-capita offspring rate (birth rate)
NoResources = 10 # Size of the niche i.e. number of diferent resources
variance = 3.0 #variance of a normal distribution
SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #np vector (of dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
mainResource = 13 #label of its principal resource
species2 = rs.species(offspringR,deadR,mainResource,SpeciesResourceSpecialization,2) # 
                     
#Create the populations
NoIndividuals = 1000
population1 = rs.generatePopulation( species1, NoIndividuals )
population2 = rs.generatePopulation( species2, NoIndividuals )

#Instance a space resource and insert the populations in it
SizeOfResourceSpace = 20
ResourceSpace = rs.resourceSpace(SizeOfResourceSpace)
Capacity = np.full_like(ResourceSpace.space,1000)
ResourceSpace.bindResoucesCapacity(Capacity)
ResourceSpace.InsertPopulation(population1)
ResourceSpace.InsertPopulation(population2)

#Evolve the sistem

#animation
fig, ax = plt.subplots()
ax = plt.axes(xlim=(0, 20), ylim=(0, 1000))
line1, = ax.plot([ len(rs.filterbyspecies(y,species1)) for y in ResourceSpace.space])
line2, = ax.plot([ len(rs.filterbyspecies(y,species2)) for y in ResourceSpace.space] )

def animate(i):
    label = 'timestep {0}'.format(i)
    rs.Evolve(ResourceSpace,10)
    line1.set_ydata([ len(y) for y in ResourceSpace.space])
    line2.set_ydata([ len(rs.filterbyspecies(y,species2)) for y in ResourceSpace.space])
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
ani.save('basic_animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
#ani.save('line.gif', dpi=80, fps=60 , writer='imagemagick')
print 'done'



