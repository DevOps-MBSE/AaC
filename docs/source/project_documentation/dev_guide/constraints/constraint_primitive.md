# Primitive Constraints

## Bool
Verify that a boolen value is `True`, `False`, or `None`.  `None` is considered `False` by Python, so we allow `None` as a valid value.

### Example Usage
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 299-304
    :emphasize-lines: 6
```
In this example, `is_required` is a Boolean field.  If the value is not interpretable as a Boolean, then the `bool` constraint will fail.

## Date
Verify that a date value is interpretable as a date.  Date values should be in Year-Month-Day (YYYY-MM-DD) format.

### Example Usage
```yaml
date: 2023-01-22
```
The above example shows the correct format for date values.  If a date value does not match that format, the `date` constraint will fail.

## Directory
Verify that a directory value is interpretable as a `directory`. Argument must be in valid directory format.

### Example Usage
```yaml
dir: /absolute/path/to/dir
dir: ./relative/path/to/dir
```
The above examples would pass the `directory` constraint.


## File
Verify that a file value is interpretable as a `file`.  Argument must be in valid file format with a filename and extension.

### Example Usage
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/plugins/gen_plugin/gen_plugin_generator.aac
    :language: yaml
    :lines: 29-32
    :emphasize-lines: 4
```
The above example would pass the `file` constraint.

## String
Verify that a string value is interpretable as a string.

## Int
Verify that an integer value is interpretable as an integer.

## Number
Verify that a number value is interpretable as a number.

## Dataref
Verify that a data reference value is interpretable and exists.

### Example Usage
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 221-222
```
In this example, the `dataref` constraint will fail if `modifier.name` is not interpretable as a data reference.

## Typeref
Verify that a type reference value is interpretable and exists.

### Example Usage
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 269-270
```
In this example, the `typeref` constraint will fail if `aac.lang.AacType` is not interpretable as a type reference.
