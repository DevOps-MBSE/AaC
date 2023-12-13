

# FEATURES

## AlarmClock :  *A simple alarm clock*
- clock
- timer
- alarm
      
## Clock :  *A simple clock that keeps track of the current time*
+ REQUEST_RESPONSE | getTime() -> currentTime

## ClockAlarm : *A simple alarm that produces noise*
+ REQUEST_RESPONSE | triggerAlarm(timerAlert) -> alarmNoise

## ClockTimer : *A simple timer that can be set to a target*
+ REQUEST_RESPONSE | setTime(targetTime) -> currentTime
+ TIMER | triggerTimer(currentTime) -> timerAlert


 # IMPORTS

[LOCAL]()
Clock: clock
ClockAlarm: alarm
ClockTimer: timer

 [structures.md](./structures.md)
- AlarmNoise: alarmNoise
- TimeStamp: currentTime, targetTime
- TimerAlert: timerAlert


 | InheritsFrom | Type          | Description                                         | Local Instances          |
 | ------------ | ------------- | --------------------------------------------------- | ------------------------ |
 |              | AlarmNoise    | [./structures.md](#)                                | alarmNoise               |
 |              | Clock         | A simple clock that keeps track of the current time | clock                    |
 |              | ClockAlarm    | A simple alarm that produces noise                  | alarm                    |
 |              | ClockTimer    | A simple timer that can be set to a target          | timer                    |
 |              | TimeStamp     | [../alarm_clock/structures.md](#)                   | currentTime, targetTime  |
 |              | TimerAlert    | [../alarm_clock/structures.md](#)                   | timerAlert               |


# CONSTRAINTS

   - all_types_unique
   - all_instances_unique
   - all_instances_defined
   - all_enum_values_defined