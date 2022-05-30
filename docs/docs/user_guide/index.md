---
layout: default
title: AaC User's Guide
nav_order: 2
has_children: true
permalink: docs/user_guide
---

# What is Architecture-as-Code?
Architecture-as-Code (AaC) is a distinctly different take on Model-Based System Engineering (MBSE) that allows a system modeller to define a system in simple yaml. This approach allows engineers to apply rigorous configuration management to their baselines and to leverage modern software development tools and practices, such as Continuous Integration and automated quality gates, to modeled systems, environments, products, or whatever it is that you're modeling with AaC.

## Who is AaC for?
While "code" is in the name, AaC isn't solely for coders, programmers, or software engineers. Instead, AaC is intended to be a single-source of truth shared between all development stakeholders including those who have a hand in designing, implementing, or auditing a modeled system. Following this desire, AaC provides several interfaces for interacting with the language and tool set.

|Interface|Implementation Status| References |
|---------|---------------------|------------|
| Command-line Interface | ✅ Implemented | [AaC Command Line Interface](./aac_cli)
| Application Programming Interface | ✅ Implemented (Python)  | N/A |
| Visualization | ❌ In-progress | N/A |

# Getting started
Not sure where to start? We've got you covered; just checkout
[Getting Started](./getting_started)!

# AaC DSL Overview
The AaC DSL's focus on extensibility can make the language difficult to pickup without context. Checkout out the
[Overview of the AaC DSL](./aac_language) for an overview and intro to the AaC DSL.

# Project Structure and Good Practices
[AaC Project and File Structure](./project_structure)

# Decomposing models and systems in AaC
[Decomposing system in AaC](./decomposing_systems)

# Leveraging AaC in VCS and CI/CD Environments
AaC's use of plain-text YAML representation allows AaC users to leverage version control software tools such as Git and Continuous Integration/Continuous Delivery practices for extremely high levels of automation.
[AaC and GitOps](./aac_gitops)

# Glossary
For all of those acronyms or ambiguous words we use.
[AaC Glossary](./glossary)