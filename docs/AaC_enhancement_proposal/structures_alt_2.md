

# FEATURES

## AlarmClock :  *A simple alarm clock*
 
   - clock
        + REQUEST_RESPONSE | getTime() -> currentTime
   - timer
        + REQUEST_RESPONSE | setTime(targetTime) -> currentTime
        + TIMER | triggerTimer(currentTime) -> timerAlert
   - alarm
        + REQUEST_RESPONSE | triggerAlarm(timerAlert) -> alarmNoise
      

 # SCHEMA

 | Type          | Description                                         | Instances                |
 | ------------- | --------------------------------------------------- | ------------------------ |
 | AlarmNoise    | [./structures.aac](X)                               | alarmNoise               |
 | Clock         | A simple clock that keeps track of the current time | clock                    |
 | ClockAlarm    | A simple alarm that produces noise                  | alarm                    |
 | ClockTimer    | A simple timer that can be set to a target          | timer                    |
 | TimeStamp     | [../alarm_clock/structures.aac](#)                  | currentTime, targetTime  |
 | TimerAlert    | [../alarm_clock/structures.aac](#)                  | timerAlert               |


# INSTANCES
none


# CONSTRAINTS

   - all_types_unique
   - all_instances_unique
   - all_instances_defined
   - all_enum_values_defined