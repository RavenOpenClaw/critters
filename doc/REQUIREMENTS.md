# **Critters: Game Requirements & Design**

## **🌟 Core Vision**

A top-down, grid-based creature collector and incremental simulation. The player starts by hand-gathering resources to build an initial home, then pivots to managing a workforce of "Critters" to automate gathering, explore a hand-crafted world, and unlock new areas via massive "work projects" (e.g., clearing fallen trees, building bridges).

## **🎮 Gameplay Mechanics**

### **1. Player Actions**

* **Movement:** Smooth movement across a grid-based world.  
* **Gathering:** Manual interaction with world objects (berries, trees, rocks, sticks, grass).  
* **Crafting:** Menu-based crafting (no physical bench required for now).  
* **Infinite Inventory:** Simplified resource management for the prototype.  
* **Building:** Placing structures on the grid to provide buffs or task-hubs.

### **2. Buildings & Buffs**

* **Chair:** Provides "Rested" status (Movement Speed buff).  
* **Tools:** Increases manual chopping/mining speed.  
* **Campfire:** Cooks food for a "Strength" buff.  
* **Gathering Hut:** The anchor for Critter automation. Stores resources collected by assigned Critters.  
* **Mating Hut:** Late-prototype building for breeding Critters.

### **3. The Critters**

* **AI Loop:** 1. [IDLE]: At assigned building. 2. [GATHER]: Find random item in radius -> Walk to item -> Pick up. 3. [RETURN]: Walk back to Hut -> Deposit item.  
* **Visualization:** Current state label printed above the Critter's head. Simple 2-frame idle/action sprites.  
* **Stats (1-100):**  
  * **Strength:** Work speed (chopping/picking).  
  * **Speed:** Walk speed.  
  * **Endurance:** Frequency of eating and duration of IDLE state.  
* **Happiness/Food:** Being "Well Fed" gives a ~10% bonus to all stats.

### **4. World & Simulation**

* **Grid-Based:** All objects and buildings occupy discrete grid cells.  
* **Persistence:** Trees regrow, grass spreads, and common paths become "trampled" (temporarily preventing grass regrowth).  
* **Progression Gates:** Large-scale obstacles (Pikmin-style) that require massive amounts of "Work Units" to clear, incentivizing larger/stronger Critter workforces.

### **5. Breeding**

* Inherit base stats from parents with a chance for random mutations to allow for progression toward the 100-stat cap.