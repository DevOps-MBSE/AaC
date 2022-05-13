# aac-spec

## Plugin Commands

### Command: spec-validate

Validates spec traces within the AaC model.

Example shell usage:

```bash
(.env) $ aac spec-validate -h
```

#### Command arguments

- `-h`, `--help`: Shows a help message
- `architecture_file`: The file to validate for spec cross-references.

## Plugin Extensions and Definitions

### Ext - addLoggingToBehaviorType

TODO: Add descriptive information about addLoggingToBehaviorType

```yaml
ext:
  enumExt:
    add:
    - logging
  name: addLoggingToBehaviorType
  type: BehaviorType

```

### Ext - addSpecificationToRoot

TODO: Add descriptive information about addSpecificationToRoot

```yaml
ext:
  schemaExt:
    add:
    - name: spec
      type: Specification
  name: addSpecificationToRoot
  type: root

```

### Ext - addSpecTraceToBehavior

TODO: Add descriptive information about addSpecTraceToBehavior

```yaml
ext:
  schemaExt:
    add:
    - name: requirements
      type: RequirementReference[]
  name: addSpecTraceToBehavior
  type: Behavior

```

### Ext - addSpecTraceToData

TODO: Add descriptive information about addSpecTraceToData

```yaml
ext:
  schemaExt:
    add:
    - name: requirements
      type: RequirementReference[]
  name: addSpecTraceToData
  type: schema

```

### Schema - Specification

TODO: Add descriptive information about Specification

```yaml
schema:
  fields:
  - name: name
    type: string
  - name: description
    type: string
  - name: sections
    type: SpecSection[]
  - name: requirements
    type: Requirement[]
  name: Specification
  required:
  - name

```

### Schema - SpecSection

TODO: Add descriptive information about SpecSection

```yaml
schema:
  fields:
  - name: name
    type: string
  - name: description
    type: string
  - name: requirements
    type: Requirement[]
  name: SpecSection
  required:
  - name

```

### Schema - Requirement

TODO: Add descriptive information about Requirement

```yaml
schema:
  fields:
  - name: id
    type: string
  - name: shall
    type: string
  - name: parent
    type: RequirementReference[]
  - name: attributes
    type: RequirementAttribute[]
  name: Requirement
  required:
  - id
  - shall

```

### Schema - RequirementAttribute

TODO: Add descriptive information about RequirementAttribute

```yaml
schema:
  fields:
  - name: name
    type: string
  - name: value
    type: string
  name: RequirementAttribute
  required:
  - name
  - value

```

### Schema - RequirementReference

TODO: Add descriptive information about RequirementReference

```yaml
schema:
  fields:
  - name: ids
    type: string[]
  name: RequirementReference
  required:
  - ids

```