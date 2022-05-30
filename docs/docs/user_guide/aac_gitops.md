

# Configuration Management
One of the main benefits of using Architecture-as-Code is that your models and systems are stored in plain-text yaml files instead of binary or database formats. Storing models as plain-text allows version control tools, like Git, to easily track and manage changes to your models and systems. Leveraging tools like Git opens modeling teams to using software development practices such as [feature branch workflows](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) to enable parallel development on the the models or systems.

# Leveraging AaC in CI/CD pipelines
Architecture-as-Code not only allows users to leverage the power of version-control tools like Git for systems modeling, but it also enables users to leverage Continuous Integration/Continuous Delivery pipelines.

The [AaC-User-Template-Repository](https://github.com/Coffee2Bits/AaC-User-Template-Repository/actions/runs/2380729241) comes with a simple, prepared pipeline that automatically validates any changes to the AaC models and automatically generates a markdown document of the models, Protobuf3 messages for interfaces, and PlantUML diagrams.