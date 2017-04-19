import numpy as np
import resourcespetialitation as rs
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
mpl.rcParams['animation.writer'] = 'avconv'


def main1():
	#Define the species

	#specie 1
	birthR = 0.21 #intrinsic per-capita offspring rate (birth rate)
	deadR = 0.2	#intrinsic per capita dead rate
	mainResource = 10 #label of its principal resource
	NoResources = 1 # Size of the niche i.e. number of diferent resources
	variance = 3.0 #variance of a normal distribution
	SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #Distribution (Object) ( dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
	#SpeciesResourceSpecialization = rs.uncenteredGaussian(NoResources,variance,-5)
	species1 = rs.species(birthR,deadR,mainResource,SpeciesResourceSpecialization) # 

	#specie 1a
	NoResources = 10
	SpeciesResourceSpecializationA = rs.gaussianSpecialization(NoResources,variance)
	species1A = rs.species(birthR,deadR,mainResource,SpeciesResourceSpecializationA)

	#specie 2
	birthR = 0.25 #intrinsic per-capita offspring rate (birth rate)
	deadR = 0.2	#intrinsic per capita dead rate
	mainResource = 10 #label of its principal resource
	NoResources = 1 # Size of the niche i.e. number of diferent resources
	variance = 3.0 #variance of a normal distribution
	SpeciesResourceSpecialization = rs.gaussianSpecialization(NoResources,variance) #Distribution (Object) (of dimension NoResources) with a discretized normal distribution centered at the middle of the vector with variance "variance" in units of index of the vector. 
	#SpeciesResourceSpecialization = rs.uncenteredGaussian(NoResources,variance,5)
	species2 = rs.species(birthR,deadR,mainResource,SpeciesResourceSpecialization) # 
				   
	#specie 2a
	NoResources = 10
	SpeciesResourceSpecializationA = rs.gaussianSpecialization(NoResources,variance)
	species2A = rs.species(birthR,deadR,mainResource,SpeciesResourceSpecializationA)
		  
	#Create the populations
	NoIndividuals = 4000
	population1 = rs.generatePopulation( species1, NoIndividuals )
	population2 = rs.generatePopulation( species2, NoIndividuals )

	#populations A
	NoIndividuals = 4000
	population1A = rs.generatePopulation( species1A, NoIndividuals )
	population2A = rs.generatePopulation( species2A, NoIndividuals )

	#Instance a space resource and insert the populations in it
	SizeOfResourceSpace = 20
	ResourceSpace = rs.resourceSpace(SizeOfResourceSpace)
	Capacity = rs.distribution('constant', np.full_like(ResourceSpace.space,10000))
	ResourceSpace.bindResoucesCapacity(Capacity)
	ResourceSpace.InsertPopulation(population1)
	ResourceSpace.InsertPopulation(population2)

	#space A
	ResourceSpaceA = rs.resourceSpace(SizeOfResourceSpace)
	CapacityA = rs.distribution('constant', np.full_like(ResourceSpace.space,1000))
	ResourceSpaceA.bindResoucesCapacity(CapacityA)
	ResourceSpaceA.InsertPopulation(population1A)
	ResourceSpaceA.InsertPopulation(population2A)

	#Create Simulation object from inital ResourceSpace ----------

	Simulation = rs.simulation(ResourceSpace)
	simulation_dir = Simulation.dir()

	#Simulation A
	SimulationA = rs.simulation(ResourceSpaceA)
	simulation_dirA = SimulationA.dir()

	####Evolve the sistem

	abundance_specie1 = []
	abundance_specie2 = []
	time_space = []

	#animation
	fig, ax = plt.subplots()
	ax = plt.axes(xlim=(0, 20), ylim=(0, 100))
	species1_dist = [ len(rs.filterbyspecies(y,species1)) for y in Simulation.ResourceSpace.space]
	line1, = ax.plot(species1_dist)
	species2_dist = [ len(rs.filterbyspecies(y,species2)) for y in Simulation.ResourceSpace.space]
	line2, = ax.plot(species2_dist )
	abundance_specie1.append(np.sum(species1_dist))
	abundance_specie2.append(np.sum(species2_dist))
	time_space.append(0)

	resolution = 1.0
	T_final=250

	def animate(i):
		label = 'timestep {0}'.format(i)
		Simulation.evolve(resolution)
		species1_dist = [ len(rs.filterbyspecies(y,species1)) for y in Simulation.ResourceSpace.space]
		line1.set_ydata(species1_dist)
		species2_dist = [ len(rs.filterbyspecies(y,species2)) for y in Simulation.ResourceSpace.space]
		line2.set_ydata(species2_dist)
		ax.set_xlabel(label)
		abundance_specie1.append(np.sum(species1_dist))
		abundance_specie2.append(np.sum(species2_dist))
		time_space.append(Simulation.duration)
		return line1, line2
		
	def init():
		line1.set_data([], [])
		line2.set_data([], [])
		return line1, line2   

	#ani = animation.FuncAnimation(fig, animate, np.arange(1, 10), init_func=init,
	#                              interval=25, blit=True)               
	print 'generating animation ...'
	ani = animation.FuncAnimation(fig, animate, np.arange(1,T_final/resolution),interval=10)
	#plt.show()
	print 'writing file ...'
	try:
		#ani.save(Simulation.dir() + 'basic_animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
		ani.save(simulation_dir + 'animation.mp4', fps=10) 
	except TypeError:
		print "error en simulacion ignorado"
	finally:
		print "otro error"

	plt.figure(2)
	plt.plot(time_space, abundance_specie1 , label='species1')
	plt.plot(time_space, abundance_specie2,  label='species2')
	plt.legend(loc='upper right',framealpha=0.6)
	plt.savefig(simulation_dir + 'evolution.png')

	plt.figure(3)
	relative_populations=np.divide(np.array(abundance_specie1).astype(float) ,np.array(abundance_specie2).astype(float))
	plt.plot(relative_populations, label="relative abundance")
	plt.legend(loc='upper right',framealpha=0.6)
	plt.savefig(simulation_dir + 'relative_abundance.png')

	print 'Resalvando simulacion'
	Simulation.save()
	print 'simulation : ' + str(Simulation.id)


	####Evolve simulation A

	abundance_specie1A = []
	abundance_specie2A = []
	time_spaceA = []

	#animation
	plt.figure(4)
	fig, ax = plt.subplots()
	ax = plt.axes(xlim=(0, 20), ylim=(0, 100))
	species1_dist = [ len(rs.filterbyspecies(y,species1A)) for y in SimulationA.ResourceSpace.space]
	line1, = ax.plot(species1_dist)
	species2_dist = [ len(rs.filterbyspecies(y,species2A)) for y in SimulationA.ResourceSpace.space]
	line2, = ax.plot(species2_dist )
	abundance_specie1A.append(np.sum(species1_dist))
	abundance_specie2A.append(np.sum(species2_dist))
	time_spaceA.append(0)

	resolution = 1.0
	T_final=250

	def animateA(i):
		label = 'timestep {0}'.format(i)
		SimulationA.evolve(resolution)
		species1_dist = [ len(rs.filterbyspecies(y,species1A)) for y in SimulationA.ResourceSpace.space]
		line1.set_ydata(species1_dist)
		species2_dist = [ len(rs.filterbyspecies(y,species2A)) for y in SimulationA.ResourceSpace.space]
		line2.set_ydata(species2_dist)
		ax.set_xlabel(label)
		abundance_specie1A.append(np.sum(species1_dist))
		abundance_specie2A.append(np.sum(species2_dist))
		time_spaceA.append(SimulationA.duration)
		return line1, line2
		
	def init():
		line1.set_data([], [])
		line2.set_data([], [])
		return line1, line2   

	#ani = animation.FuncAnimation(fig, animate, np.arange(1, 10), init_func=init,
	#                              interval=25, blit=True)               
	print 'generating animation ...'
	ani = animation.FuncAnimation(fig, animateA, np.arange(1,T_final/resolution),interval=10)
	#plt.show()
	print 'writing file ...'
	try:
		#ani.save(Simulation.dir() + 'basic_animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
		ani.save(simulation_dirA + 'animation.mp4', fps=10) 
	except TypeError:
		print "error en simulacion ignorado"
	finally:
		print "otro error"

	plt.figure(5)
	plt.plot(time_spaceA, abundance_specie1A , label='species1')
	plt.plot(time_spaceA, abundance_specie2A,  label='species2')
	plt.legend(loc='upper right',framealpha=0.6)
	plt.savefig(simulation_dirA + 'evolution.png')

	plt.figure(6)
	relative_populationsA=np.divide(np.array(abundance_specie1A).astype(float) ,np.array(abundance_specie2A).astype(float))
	plt.plot(relative_populations, label="relative abundance")
	plt.legend(loc='upper right',framealpha=0.6)
	plt.savefig(simulation_dirA + 'relative_abundance.png')

	print 'Resalvando simulacion'
	Simulation.save()
	print 'simulation : ' + str(SimulationA.id)

	##join the relative abundances
	plt.figure(7)
	plt.plot(relative_populations, label="Specialist")
	plt.plot(relative_populationsA, label="Generalist" )
	plt.legend(loc='upper right',framealpha=0.6)
	plt.savefig(simulation_dirA + 'comparison.png')
	plt.savefig(simulation_dir + 'comparison.png')
