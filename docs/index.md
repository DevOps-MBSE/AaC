---
layout: default
title: Home
nav_order: 1
description: "Architecture-as-Code is a Model-Based System Engineering approach that enabled DevOps practices for system specification."
permalink: /
---

# Architecture-as-Code (AaC)

[Get started now](docs/userguide){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [View it on GitHub](https://github.com/jondavid-black/AaC){: .btn .fs-5 .mb-4 .mb-md-0 }

## What is Architecture-as-Code (AaC)?

### The AaC Modeling Language
      
AaC is a distinctly different take on Model-Based System Engineering (MBSE) that allows a
system modeller to define a system in code (yaml).  AaC defines the Architecture-as-Code 
modeling language specification based upon ideas from the DevOps Infrastructure-as-Code (IaC).
IaC streamlines the flow from Development to Operations. AaC was created to streamline the flow from 
System Engineering to Development.

The AaC model enables system modelers to maintain collection of machine and human readable plain-text YAML files that will enable new
constructs for maintaining vertical (i.e., its top-down structure) and horizontal (i.e., how components interact
with one another) traceability, quality assessment of architecture and design, and automation system acceptance
tests. This is all to increase predictability and reduce risk within small-batch Agile program execution
environments.

### AaC Motivation

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
technique, the <a href="https://itrevolution.com/the-three-ways-principles-underpinning-devops/">flow</a>
from systems engineering to development can likewise be improved.

The AaC model describes how the system is to be decomposed, the responsibility of the system, how the system will
be tested, and how the system is deployed. This makes it possible to create another type of pipeline from system
engineering to development. This pipeline can only be possible if there exists some model that describes the
design of the system. The AaC model is therefore the source artifact from which numerous other
types of artifacts can be created. These artifacts can be generated using the AaC CLI and evaluated as
part of a pipeline.

In short, we wanted to have an architectural artifact that can be:
- Fully configuration managed (including version controlled)
- Used to provide a fail-fast approach to System Engineering
- Used to faciliate rapid innovation and experimentation
- Used to increase flow from Systems Engineering and Development
- Used to faciliate and drive down-stream engineering
- Used to provide traceablity between the architecture and what was actually built
- Evaluated as a part of a continuous delivery pipeline

### Our Hypothesis

- We believe that: 
    - buiding a MBSE solution that embraces DevOps principles
 - for 
    - System Engineers - e.g. domain experts, architects
    - System Testers - e.g. quality, compliance
    - and System Developers - e.g. implementation, delivery
 - will achieve 
    - higher quality MBSE products
    - higher quality system deliveries
    - better small batch Agile planning / execution for cross-functional teams
    - and greater efficiency in the total system delivery lifecycle.

We know we are successful when we see:
  - rigorous configuration management of MBSE artifacts
  - reduced MBSE work / rework
  - upstream MBSE artifacts actively used by product development & delivery teams
  - implementation of automated quality assurance in pipelines for MBSE artifacts
  - and frequent delivery of complete system engineering, implementaiton, and test baselines with full traceability.

We believe we can discover new ways to define, deliver, and evolve complex systems using Architecture-as-Code.

### The Command Line Interface
      
AaC is also the name of the modular command line interface (CLI) that can parse a Architecture-as-Code model
and produce artifacts from it. The CLI has an extensible command library that currently contains commands that
can verify syntax and patterns, generate code and produce static reports.

The entire AaC product is extensible so you can use only the features you want.  AaC is purposefully small.
Additional functionallity is achieved through installing plugins.

### The Graphical User Interface

AaC has a backlog item to create a GUI, but it has not yet been built.  We are currently performing interviews
with stakeholders to determine the best way to provide them value quickly.  Stay tuned for new releases.

### AaC is Extensible

AaC is designed with extensibility in mind.  The built-in functionallity is intentionally minimized.
AaC uses a plug-in system to extend the base capability.  To further simplify this, AaC includes a
built-in command to generate new plugins from an AaC model.  There is an example of this for
Plant UML in the plugins folder of the repository.

---

## About the project

Architecture-as-Code (AaC) is &copy; 2021-{{ "now" | date: "%Y" }} by [COMPANY NAME](http://devopsfordefense.org).

### License

Just the Docs is distributed by an [MIT license](https://github.com/jondavid-black/AaC/blob/main/LICENESE).

### Contributing

When contributing to this repository, please first discuss the change you wish to make via issue or discussion topic with the owners of this repository before making a change. Read more about becoming a contributor in [our GitHub repo](https://github.com/pmarsceill/just-the-docs#contributing).

*Thank you to the contributors of Architecture-as-Code!*

<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}"><img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}"/></a>
  </li>
{% endfor %}
</ul>

### Code of Conduct

Architecture-as-Code is committed to fostering a welcoming community.

[View our Code of Conduct](https://github.com/jondavid-black/AaC/blob/main/CODE_OF_CONDUCT.md) on our GitHub repository.
