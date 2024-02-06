# Undefined Fields
The `Undefined Fields` constraint is a schema constraint that checks that a field is defined by the schema when a value is assigned to it.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/features/alarm_clock/structures.yaml
    :language: yaml
    :lines: 1-12
```

In the above example, the schema `TimerAlert` has three defined fields: `name`, `triggeredTime`, and `alarmNoise`.  If you attempt to assign a value to a field that does not exist, the `Undefined Fields` constraint will fail.
