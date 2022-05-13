# AAC Material Model Plug-In

When architecting a system it is important to comprehend both the logical and physical aspects of that system.
It is not uncommon for material decisions to drive significant cost or complexity in a system.  The material
model plug-in allows you to define a organized structure for your material within a rigorously configuration
managed environment.  Hopefully this simplifies and improves on the "huge spreadsheet approach" used by some teams.

There are 3 primary schema types to understand when modeling material:
- Part: This is a material line item you may find in a vendor quote.  It may represent
hardware, software, or services.  It may have a cost or be free (i.e. Open Source Software).
- Assembly:  This is a collection of parts that make up a logical "thing" in your material design.  It gives you
the ability to define and reference that collection of parts as a meaningful item as you design your system.
Assemblies may also include sub-assemblies to help promote clarity in defining large or complex configurations.
- Deployment:  This is the collection of things (assemblies and parts) required to instantiate a working solution
at a particular location at a particular time.  Deployments may also include sub-deployments to help promote clarity in definition large or complex deployments across multiple locations.

Defining and managing material can be a remarkably complex activity.  This plug-in does not attempt to address all concerns
with managing material, but is extensible to allow for incremental improvement.

## Usage

AAC material modeling can be done top-down, bottom-up, or as a combination of these using incremental definition.  In
this usage example we'll take a top-down approach.  Let's say we're moving into a new 1 bedroom apartment and need to ensure
everything is in order.  First we can create a high level deployment model.

```my_apartment.yaml```
```yaml
deployment:
  name: My_New_Apartment
  description: The place I'm going to live.
  location: Crystal Terrace Apartments Unit 1234
  sub-deployments:
    - name: Living_Room
      quantity: 1
    - name: Kitchen
      quantity: 1
```

Now we can define each of the sub-deployments.  For simplicity we'll just focus on the Living Room.  I know that the living room will have an entertainment system and a seating area, so we'll define assemblies for those.

```living_room.yaml```
```yaml
deployment:
  name: Living_Room
  description:  The place I'll hang out a lot.
  assemblies:
    - name: Entertainment_System
      quantity: 1
    - name: Seating_Area
      quantity: 1

```
We can now start to consider the individual items that make up our entertainment system and seating area.  Let's keep things simple and just drill down into the seating area.

```seating_area.yaml```
```yaml
assembly:
  name: Seating_Area
  description:  The place I'll hang out a lot.
  parts:
    - name: Couch
      quantity: 1
    - name: Arm_Chair
      quantity: 1
    - name: Coffee_Table
      quantity: 1
    - name: Side_Table
      quantity: 2
    - name: Table_Lamp
      quantity: 2
    - name: Coasters
      quantity: 1
```

And now we just have to do our research and define each of the parts we need to make up our living room.

```amazon_parts.yaml```
```yaml
part:
  name: Coasters
  make: HUAOAO
  model: Cork Coaster Set
  descriptioN: Set of 12 plain cork coasters.
  unit_cost: 7.19
  quote_type: Web_Reference
  quote: https://smile.amazon.com/Coaster-Absorbent-Resistant-Reusable-Coasters/dp/B08PZ15J2N
```
Now we rinse and repeat for the other deployments, assemblies, and parts we have identified and we will have our material model complete.  Be sure to go back and add in the import statements to ensure content references can be validated. With the model complete we can do some operations on it to ensure validity (i.e. no obvious errors in the definitions).

```bash
aac validate my_apartment.yaml
```

A complete example of this material model can be found in the [model/material folder on GitHub](https://github.com/jondavid-black/AaC/tree/material-model/python/model/material).