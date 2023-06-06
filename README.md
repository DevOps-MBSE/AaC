[![Main branch AaC Workflow](https://github.com/jondavid-black/AaC/actions/workflows/main-branch.yml/badge.svg)](https://github.com/jondavid-black/AaC/actions/workflows/main-branch.yml)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/from-referrer/)

# Note to Contributors

Due to certain uncontrollable circumstances surrounding the environment in which
Architecture-as-Code is being developed and funded, we cannot accept any new outside
contributions at this time. We will reject any pull requests from unknown sources.
While this is unfortunate, we still accept feedback and ideas that will better the
form and function of the AaC product in all of its forms. We apologize for this inconvenience.

In the future, it is our intention to accept contributions from outside sources
per our standards and code of conduct. We are committed to reaching the goal of an
open source repository and hope that potential contributors will still follow our
progress and join us in the future.


# Architecture-as-Code (AaC)

AaC is a distinctly different take on Model-Based System Engineering (MBSE) that allows a
system modeller to define a system in simple yaml.  This approach allows engineers to
apply rigorous configuration management to their baselines (unlike other "boxes and lines" approaches).
Our team has spent many years engineering, building, testing, and delivering complex systems. In
that time we've seen an enormous amount of effort and money put into system modelling. Unfortunately,
it is almost always the case that the system model is either never used by the teams building and
delivering product, or it adds complexity to those team's workflow and becomes an impediment. The
creators of AaC have spent many years working to adopt and tailor the principles of DevOps within
our professional workplaces.  We've seen the amazing efficiencies that can be achieved by knocking down
the "wall of confusion" between developers and operations and optimizing around system thinking, flow,
and continuous improvement through learning and experimentation. We believe the critical tipping point
that allowed this to occur was the creation of Infrastructure-as-Code and the adoption of new practices
like GitOps that embrace automated quality assurance, automated deployment, and continuous monitoring.
Our objective is to knock down the "wall of confusion" that exists between systems engineering and
development, optimizing the total system delivery value stream from concept/requirement through to
operations with complete traceability and configuration management throughout.  We believe we can
discover new ways to define, deliver, and evolve complex systems using Architecture-as-Code.

AaC is a self-defining solution. At the heart of the AaC application is a definition of AaC itself.
This model is used in validation of itself.  Core data types are purposefully simple and can be
extended by a user.

AaC is designed with extensibility in mind.  The built-in functionality is intentionally minimized.
AaC uses a plug-in system to extend the base capability.  To further simplify this, AaC includes a
built-in command to generate new plugins from an AaC model.  There is an example of this for
Plant UML in the plugins folder of the repository and more info below.

## Using AaC to Model Your System
AaC is written in Python to help make it more approachable for casual users and easily extensible for
power users.

**You will need Python 3.9 or later to run AaC.**

To install AaC on Linux or Windows:
```bash
pip install aac
```

To use AaC you first define a model of your system in yaml.  Refer to the documentation for more details.
A simple model for an EchoService is provided here for reference.  Cut and paste the below model into a
file called EchoService.yaml.
*Note: This is using a little yaml trick to concatenate the content of two yaml files into a single file.*
```yaml
schema:
  name: Message
  fields:
  - name: body
    type: string
  - name: sender
    type: string
---
model:
  name: EchoService
  description: This is a message mirror.
  behavior:
    - name: echo
      type: request-response
      description: This is the one thing it does.
      input:
        - name: inbound
          type: Message
      output:
        - name: outbound
          type: Message
      acceptance:
        - scenario: onReceive
          given:
           - The EchoService is running.
          when:
            - The user sends a message to EchoService.
          then:
            - The user receives the same message from EchoService.
```

Now you can run AaC against your model.
```bash
aac validate EchoService.yaml
```

AaC has some core "root types" for you to work with.  You can see the root types of `schema` and `model` used in the example above.
The AaC core root types are:
- schema: Allows you to model data structures used within your system as user-defined types.
- enum: Allows you to model enumerated values (types with only specific values allowed).
- model: Allows you to model the components of your system and their interfaces.  These can be abstract or concrete.
- usecase: Allows you to model the behavior and interactions between your models.
- ext: Allows you to easily extend the AaC DSL itself and tailor it to your needs.

Although you can use the yaml trick above when modelling your system, it would be better to keep things more
structured and organized.  To help with this AaC allows you to define each item you model in a separate file and
then import it as needed.  To do this just put an **import** at the root of your model file.

Here's an example of the EchoService broken into two files:
- Message.yaml
    ```yaml
    schema:
      name: Message
      fields:
        - name: body
          type: string
        - name: sender
          type: string
    ```
- EchoService.yaml
    ```yaml
    import:
    - ./Message.yaml
    ---
    model:
      name: EchoService
      description: This is a message mirror.
      behavior:
        - name: echo
          type: request-response
          description: This is the one thing it does.
          input:
            - name: inbound
            type: Message
          output:
            - name: outbound
            type: Message
          acceptance:
            - scenario: onReceive
              given:
                - The EchoService is running.
              when:
                - The user sends a message to EchoService.
              then:
                - The user receives the same message from EchoService.

    ```
Ok, so that's interesting, but what can you do with the AaC model once you've built it?
AaC is designed and built on years of experimentation, experience, and learning.  But this version
is a brand new implementation rewritten entirely in Python in an attempt to make AaC more user friendly
to both the casual user and the power user. Right now AaC doesn't have a lot of additional features.
But new plugins are being created to deliver more functionality.  Over time there will be plugins
available to use the AaC model to auto-generate content for reviews, documentation, and even system
development and deployment.

## User Documentation
Users who would like more detailed documentation on leveraging AaC can find it in our Github pages user documentation here: https://jondavid-black.github.io/AaC/docs/user_guide

## Example AaC Template Repository
We have a [Github Template Repository](https://github.com/Coffee2Bits/AaC-User-Template-Repository) that's setup to allow users exploring AaC to immediately create and experiment with an AaC project in their own GitHub repository. The created repository is pre-populated with a simple example model and Github Action workflow.

## Developer Documentation
Contributors, developers, or just generally interested parties who would like to understand the more technical underpinnings of AaC are welcome to read the project and developer documentation found in our Github pages documentation here: https://jondavid-black.github.io/AaC/docs/dev_guide

## Driving Value with AaC Plugins
A simple example of one of the plugins mentioned above is the Plant UML plugin in the /plugins/aac-plantuml directory
of this repository.  This plugin allows you to generate component diagrams, object diagrams, and sequence
diagrams from the AaC model of your system.  You can test this yourself by using the models in the /model
director of this repository.

To build the Plant UML plugin, first we modeled the plugin behavior we wanted using AaC.  I'll walk you through building
that plugin so you can build your own plugin for your own need.
1) Model the Plugin behavior using AaC
    - The /plugins/aac-plantuml/aac-plantuml.yaml file contains the specification of 3 desired behaviors.
1) Generate the plugin boiler-plate code.
    - Run aac gen-plugin aac-plantuml.yaml
    - When prompted if you want to write files type "y" and hit enter.
    - Everything you need for a plugin to work in the AaC tool has been generated except the business logic.
    - Note:  Plugins have a pre-defined interface.  They have 2 arguments: path to the file being processes, and the
       parsed_model which is a dict.  This key is the type name and the value is the model content for that type.
1) Write the business logic for your plug-in.
    - You can see the business logic in /plugins/aac-plantuml/aac_plantuml_impl.py.
    - Note:  The other files in the directory are auto-generated and will be overwritten if you rerun gen-plugin.  Your
       plugin impl file will not be overwritten, so keep your business logic here or in other non-generated files.
1) Build your plugin.
    - From your plugin directory run '''pip install -e .''' and your plugin will be built and installed locally.
1) Test your plugin
    - Run '''aac plugin-behavior-name model_file''' to see your plugin in action.
1) If you wish you can now package and publish your plugin to PyPI for other AaC users to download and use.
    - From your plugin directory run '''python -m build'''
    - From your plugin directory run '''python -m twine upload dist/*'''

We're also actively working on other functionality so keep an eye out for new updates.
