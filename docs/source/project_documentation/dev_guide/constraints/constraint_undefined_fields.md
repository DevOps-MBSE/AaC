# Undefined Fields
The `Undefined Fields` constraint is a Schema Constraint that checks that a field is defined by the schema when a value is assigned to it.

## Usage Example
In the below example, the schema `TimerAlert` has three defined fields: `name`, `triggeredTime`, and `alarmNoise`.  If you attempt to assign a value to a field that does not exist, i.e. `timeInterval`, the `Undefined Fields` constraint will fail.

```{eval-rst}
.. literalinclude:: ../../../../../python/features/alarm_clock/structures.yaml
    :language: yaml
    :lines: 1-12
    :emphasize-lines: 7, 9, 11
```
