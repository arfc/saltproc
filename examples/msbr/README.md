## MSBR Model

This model is based on the following technical report:

Robertson, R. C. (1971). Conceptual Design Study of a Single-Fluid Molten-Salt Breeder Reactor. (ORNL--4541). ORNL.

For a complete discussion of the model, please see Chapter 4 in:

Yardas, O. (2023). Implementation and validation of OpenMC in SaltProc [MS Thesis, University of Illinois at Urbana-Champaign].


## Key features
- Zone IB 
- Zone IIA
- Simplified Zone IIB (graphite slabs are constructed from cylindrical sectors, and so do not have a consistent width; the last gap in the ccw direction in each octant is smaller than the other gaps, which all have the same dimension)
- Control rod elements (A Guess, as no spec was provided)
- Radial reflectors.
- Simplified axial reflectors (flat as opposed to dished in the reference specification)

## Missing from model
- Zone IA
- Support structure above the main core
- Radial reflector axial ribs
- Radial reflector retaining rings
- Zone IIB Graphite Dowel pins and Hastelloy N eliptical pins
- Salt inlets and outlest
- Zone I eliptical graphite sealing pins
