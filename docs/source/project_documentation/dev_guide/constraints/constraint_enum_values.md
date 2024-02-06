# Enum Values
`Enum Values` is a constraint that checks enum fields and structures and confirms that their defined value is a possible enum value.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/features/alarm_clock/structures.yaml
    :language: yaml
    :lines: 79-87
```

In the above example, `AlarmNoise` is an enum, and must be defined as either `SONIC_BOOM`, `SIREN`, `KLAXON`, or `DOG_BARKING`.  If the defined value is not one of these, the Enum Values constraint will fail.
