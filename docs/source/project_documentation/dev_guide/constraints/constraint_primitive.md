# Primitive Constraints

## Bool
Verify that a boolen value is True, False, or None.  None is considered False by python, so we allow None as a valid value.

```yaml
schema:
  name: ExampleSchema
  package: aac.lang
  fields:
    - name: name
      type: string
      is_required: true
```
In this example, 'is_required' is a Bool field.  If a value not interpretable as a Bool, then the 'bool' constraint will fail.

## Date
Verify that a date value is interpretable as a date.  Date should be in Year-Day-month format.

```yaml
date: 2023-22-1
```
The above example shows the correct format for dates.  If a date does not match that format, the 'date' constraint will fail.

## Directory
Verify that a directory value is interpretable as a directory. Argument must be in valid directory format.
```yaml
dir: /absolute/path/to/dir
dir: ./relative/path/to/dir
```
The above examples would pass the 'directory' constraint.


## File
Verify that a file value is interpretable as a file.  Argument must be in valid directory format with a filename and extension.
```yaml
file: /absolute/path/to/file.txt
```
The above example would pass the 'file' constraint.

## String
Verify that a string value is interpretable as a string. 

## Int
Verify that an integer value is interpretable as an integer.

## Number
Verify that a number value is interpretable as a number.

## Dataref
Verify that a data reference value is interpretable and exists.

```yaml
 fields:
    - name: modifiers
      type: dataref(modifier.name)[]
```

In this example, the 'dataref' constraint will fail if 'modifier.name' is not interpretable as a data reference

## Typeref
Verify that a type reference value is interpretable and exists.

```yaml
  fields:
    - name: type
      type: typeref(aac.lang.AacType)
```
In this example, the 'typeref' constraint will fail if 'aac.lang.AacType' is not interpretable as a type reference.