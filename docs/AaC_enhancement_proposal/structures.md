

# FEATURES

## TimerAlert : *Data structure for timer alerts*
    - name
    - triggeredTime
    - alarmNoise

## TimeStamp : *Date/time with timezone*
    - hour
    - minute
    - second
    - year
    - month
    - day
    - timezone


# SCHEMA

| Type           | Description                                         | Variable Names                      |
| -------------- | --------------------------------------------------- | ----------------------------------- |
| AlarmNoise     | enum                                                | alarmNoise                          |
| TimeStamp      | date/time with timezone                             | triggeredTime                       |
| TimerAlert     | data structure for timer alerts                     | timerAlert                          |
| int            | primitive                                           | hour, min, second, year, month, day |
| TimeZoneOffset | enum                                                | timezone                            |
| string         | primitive                                           | name                                |

# ENUMS

| Name | Description | Values |
| ---- | ----------- | ------ |
| ALARM_NOISE     | *List of available alarm noises* | SONIC_BOOM, SIREN, KLAXON, DOG_BARKING |
| TIMEZONE_OFFSET | *List of timezone offsets. All values are -/+ from GMT* | -12:00, -11:00, -10:00, -09:50, -09:00, -08:00, -07:00, -06:00, -05:00, -04:50, -04:00, -03:50, -03:00, -02:00, -01:00, +00:00, +01:00, +02:00, +03:00, +03:50, +04:00, +04:50, +05:00, +05:50, +05:75, +06:00, +06:50, +07:00, +08:00, +08:75, +09:00, +09:50, +10:00, +10:50, +11:00, +11:50, +12:00, +12:75, +13:00, +14:00 |

# INITIAL CONDITIONS

## TimerAlert 

    timerAlert = { 
        name: my_alert 
        triggeredTime:
            hour: 06
            minute: 30
            second: 00
            year: 2022
            month: 01
            day: 01
    }