# Dna Generator

![dna-thumb](https://github.com/user-attachments/assets/4161e8fd-53e4-461d-a85e-3e5cddb0a767)

**Author:** The French Monkey (TFMSTYLE)  
**Version:** 1.0.0  

---

## Overview

The DNA Generator creates a parametric double-helix mesh structure inspired by biological DNA molecules.  
It procedurally builds two intertwined helical strands connected by evenly spaced bridge segments, which represent the molecular base pairs.  
Each aspect of the helix — including twist, thickness, and spacing — is fully adjustable, allowing the creation of scientific models or stylized DNA-like designs.

---

## Parameters

### Live Update
Automatically rebuilds the DNA structure whenever a parameter changes.  
Enabling this option provides instant visual feedback but may reduce performance on complex models.

---

### Turns
Defines the total number of helical rotations in the DNA strand.  
Higher values increase the overall height and complexity of the double helix.

---

### Steps per Turn
Controls the number of segments used to form each rotation of the helix.  
More steps result in smoother curvature but increase geometry density.

---

### Helix Radius
Sets the distance between the central axis and each DNA strand.  
Larger values make the helix wider and more open.

---

### Height per Turn
Specifies the vertical height of one full helix rotation.  
Adjusts the overall vertical scale and elongation of the DNA strand.

---

### Helix Thickness
Controls the radius of each helical strand.  
Affects how thick or thin the DNA filaments appear.

---

### Bridge Thickness
Determines the diameter of the bridge segments connecting the two strands.  
Larger values produce thicker base pair connectors.

---

### Base Pair Interval
Defines the number of curve steps between each connecting bridge.  
Smaller intervals create more frequent bridges; larger intervals make them sparser.

---

### Twist Factor
Scales the rotational offset of the helix along its height.  
A value of 1.0 creates a perfect double helix, while lower values result in looser twisting.

---

### Tilt (°)
Applies alternating rotation to the connecting bridges.  
Adding a small tilt gives a more dynamic, natural structure to the base pairs.

---

### Smooth Shading
Enables or disables smooth shading for the DNA mesh.  
When enabled, the surface appears continuous and organic; disabling it reveals polygonal facets.

---

## Operators

### Generate DNA
Creates or regenerates the DNA mesh using the current parameters.  
If a generated DNA object is already selected, it will be replaced with an updated version.

---

## Usage Notes

- **Helix Radius** and **Height per Turn** together define the overall proportions of the double helix.  
- Use **Base Pair Interval** to control bridge spacing for aesthetic or scientific accuracy.  
- Enable **Smooth Shading** for presentation models and disable it for clean wireframe visualization.  
- Materials for both strands and bridges are automatically assigned for quick rendering setup.  
- To create multiple variations, duplicate the DNA object and adjust **Seed** or structural parameters individually.
