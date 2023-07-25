==========================
Architecture-as-Code (AaC)
==========================

Get started now by reading the :doc:`User Guide Documentation <user_guide/index>`.

`View it on GitHub <https://github.com/jondavid-black/AaC>`_ and walk through the code base.

What is Architecture-as-Code (AaC)?
===================================

Architecture-as-Code is under major construction at the moment, including this documentation.  We're doing a major design and implementation overhaul
to address 3 primary objectives:

#. Adoptability / Approachability - If AaC is going to provide any value, the intended stakeholders must be willing to use it and get value from it.
#. Extensibility - The domains we work in are complex and require tailoring of any solution.  Ensure AaC provides an approachable solution for extension.
#. Productivity / Efficiency - Embrace the DevOps principle of Flow by providing key automation to bridge MBSE and product development / delivery.

The contributors embrace open source, so you may see us "making sausage" for a bit as we establish a first stable release.  We'll update this
documentation when we believe AaC is production ready.  Until then, feel free to experiment and explore with us.

The AaC Modeling Language
-------------------------

AaC is a distinctly different take on Model-Based System Engineering (MBSE) that allows a
system modeler to define a system in code (YAML).  AaC defines the Architecture-as-Code
modeling language specification based upon ideas from the DevOps Infrastructure-as-Code (IaC).
IaC streamlines the flow from Development to Operations. AaC was created to streamline the flow from
System Engineering to Development.

The AaC model enables system modelers to maintain collection of machine and human readable plain-text YAML files that will enable new
constructs for maintaining vertical (i.e., its top-down structure) and horizontal (i.e., how components interact
with one another) traceability, quality assessment of architecture and design, and automation of system acceptance
tests. This is all to increase predictability and reduce risk within small-batch Agile program execution
environments.

AaC Motivation
--------------

Our team has spent many years engineering, building, testing, and delivering complex systems. In
that time we've seen an enormous amount of effort and money put into system modelling. We understand the potential
value of Model-Based System Engineering (MBSE) and want to help realize that potential.  Unfortunately,
it is common to see an MBSE solution become an "Ivory Tower" effort where system modelers
build models for system modelers and not downstream product development teams.  This results in the delivered system
not being represented by the system model which results in rework...usually of the model to represent the as-built system.
Another common MBSE implementation outcome we observe is added complexity to the downstream team's workflow by
injecting cumbersome (and expensive) MBSE dependencies into their development and delivery process which becomes an impediment. The
creators of AaC are committed to the principles of DevOps and believe that MBSE "done right" can improve
the professional experience of System Engineers, System Testers, System Developers, and System Integrators.
Efficiencies in the system delivery lifecycle can be achieved by knocking down the "wall of confusion" and optimizing
around DevOps principles of system thinking / flow, feedback, and continuous improvement through learning and experimentation.

The AaC modeling approach builds upon the concept of Infrastructure-as-Code with the idea to create an
"Architecture-as-Code" approach to system engineering and modeling. By utilizing this "Architecture-as-Code"
technique, the `flow <https://itrevolution.com/the-three-ways-principles-underpinning-devops/>`_
from systems engineering to development can likewise be improved.

The AaC model describes how the system is to be decomposed, the responsibility of the system, how the system will
be tested, and how the system is deployed. This makes it possible to create another type of pipeline from system
engineering to development. This pipeline can only be possible if there exists some model that describes the
design of the system. The AaC model is therefore the source artifact from which numerous other
types of artifacts can be created. These artifacts can be generated using the AaC CLI and evaluated as
part of a pipeline.

In short, we wanted to have an architectural artifact that can be:

* Fully configuration managed (including version controlled)
* Used to provide a fail-fast approach to System Engineering
* Used to facilitate rapid innovation and experimentation
* Used to increase flow from Systems Engineering and Development
* Used to facilitate and drive down-stream engineering
* Used to provide traceability between the architecture and what was actually built
* Evaluated as a part of a continuous delivery pipeline

Our Hypothesis
--------------

* We believe that:
    * building a MBSE solution that embraces DevOps principles
* for
    * System Engineers - e.g. domain experts, architects
    * System Testers - e.g. quality, compliance
    * and System Developers - e.g. implementation, delivery
* will achieve
    * higher quality MBSE products
    * higher quality system deliveries
    * better small batch Agile planning / execution for cross-functional teams
    * and greater efficiency in the total system delivery lifecycle.

We know we are successful when we see:

* rigorous configuration management of MBSE artifacts
* reduced MBSE work / rework
* upstream MBSE artifacts actively used by product development & delivery teams
* implementation of automated quality assurance in pipelines for MBSE artifacts
* and frequent delivery of complete system engineering, implementation, and test baselines with full traceability.

We believe we can discover new ways to define, deliver, and evolve complex systems using Architecture-as-Code.

The Command Line Interface
--------------------------

AaC is also the name of the modular command line interface (CLI) that can parse a Architecture-as-Code model
and produce artifacts from it. The CLI has an extensible command library that currently contains commands that
can verify syntax and patterns, generate code and produce static reports.

The entire AaC product is extensible so you can use only the features you want.  AaC is purposefully small.
Additional functionality is achieved through installing plugins.

The Graphical User Interface
----------------------------

AaC has a backlog item to create a GUI, but it has not yet been built.  We are currently performing interviews
with stakeholders to determine the best way to provide them value quickly.  Stay tuned for new releases.

AaC is Extensible
-----------------

AaC is designed with extensibility in mind.  The built-in functionality is intentionally minimized.
AaC uses a plug-in system to extend the base capability.  To further simplify this, AaC includes a
built-in command to generate new plugins from an AaC model.  There is an example of this for
Plant UML in the plugins folder of the repository.

About the project
=================

.. include:: <isonum.txt>

Architecture-as-Code (AaC) is |copy| 2021-present by `DevOps for Defense <http://devopsfordefense.org>`_.

License
-------

Arcitecture-as-Code is distributed by an `MIT license <https://github.com/jondavid-black/AaC/blob/main/LICENESE>`_.

Contributing
------------

When contributing to this repository, please first discuss the change you wish to make via issue or discussion topic with the owners of this repository before making a change. Read more about becoming a contributor on `GitHub contributions <https://github.com/pmarsceill/just-the-docs#contributing>`_ and see our `current contribution status <https://github.com/jondavid-black/AaC#note-to-contributors>`_.

*Thank you to the contributors of Architecture-as-Code!*

.. contributors:: jondavid-black/AaC
    :avatars:
    :order: ASC

Code of Conduct
---------------

Architecture-as-Code is committed to fostering a welcoming community.

`View our Code of Conduct <https://github.com/jondavid-black/AaC/blob/main/CODE_OF_CONDUCT.md>`_ on our GitHub repository.
