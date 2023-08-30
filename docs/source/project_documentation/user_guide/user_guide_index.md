# What is Architecture-as-Code?
Architecture-as-Code (AaC) is a distinctly different take on Model-Based System Engineering (MBSE) that allows system modellers to define a system in simple plain-text YAML that can be leveraged to drive value and design consensus with developers. AaC's approach to storing models as YAML allows engineers to apply tools and practices including rigorous configuration management of their baselines, automated quality and testing gates, automated artifact generation, and automated deployment of artifacts which were previously only the domain of software development teams.

## Who is AaC for?
While "code" is in the name, AaC isn't solely for coders, programmers, or software engineers. Instead, AaC is intended to be a single-source of truth shared between all stakeholders from design to implementation and auditing. Towards this goal, AaC provides several interfaces for interacting with the language and tool set.

| Interface                         | Implementation Status    | References                                  |
|-----------------------------------|--------------------------|---------------------------------------------|
| Command-line Interface            | ✅ Implemented           | [AaC Command Line Interface](./aac_cli)     |
| Application Programming Interface | ✅ Implemented (Python)  | [AaC API Documentation](../../index)|
| Visualization                     | ⚠️ In-progress           | [AaC VSCode Extension](../vscode_extension/index) |

## Getting Started
Not sure where to start with AaC? We've got you covered; just checkout
[Getting Started](./getting_started)!

## AaC DSL Overview
The AaC DSL's focus on extensibility can make the language difficult to pickup without context. Checkout out the
[Overview of the AaC DSL](./aac_language) for an overview and intro to the AaC DSL.

## AaC Project Structure
Ready to start creating more than a few definitions in a file? Checkout how our notes on organizing more complex AaC projects.
[AaC Project and File Structure](./project_structure)

## Leveraging AaC with Version-Control Software and CI/CD Environments
AaC's use of plain-text YAML representation allows AaC users to leverage version control software tools (such as Git) and Continuous Integration/Continuous Delivery practices for extremely high levels of automation.
[AaC and GitOps](./aac_gitops)

## AaC Glossary
While we strive to be clear by avoiding the overuse of jargon, we do reference a few things that may not be clear, at first. For context on all of those acronyms or ambiguous words we use, check out the
[AaC Glossary.](./glossary)

## Big Thanks!
We want to extend a big thanks to the [CEACIDE team](https://northropgrumman.github.io/jellyfish/) for pioneering most of ideas behind AaC, and for providing us with some great documentation examples.
