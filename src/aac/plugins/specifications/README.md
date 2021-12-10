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
  dataExt:
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
  dataExt:
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
  dataExt:
    add:
    - name: requirements
      type: RequirementReference[]
  name: addSpecTraceToData
  type: data

```

### Data - Specification

TODO: Add descriptive information about Specification

```yaml
data:
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

### Data - SpecSection

TODO: Add descriptive information about SpecSection

```yaml
data:
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

### Data - Requirement

TODO: Add descriptive information about Requirement

```yaml
data:
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

### Data - RequirementAttribute

TODO: Add descriptive information about RequirementAttribute

```yaml
data:
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

### Data - RequirementReference

TODO: Add descriptive information about RequirementReference

```yaml
data:
  fields:
  - name: ids
    type: string[]
  name: RequirementReference
  required:
  - ids

```