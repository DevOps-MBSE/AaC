
- [ ] Are components and state the same thing?

----------------------------------


# FEATURES

## AlarmClock :  *A simple alarm clock*
COMPONENTS
- Clock: clock
- ClockTimer: timer
- ClockAlarm: alarm
      
### Clock :  *A simple clock that keeps track of the current time*

COMPONENTS:
  none

METHODS
| Behavior | Action | Input | Output |
| ---------------- | ------ | ----- | ------ |
| REQUEST_RESPONSE | getTime | | TimeStamp | 


### ClockAlarm : *A simple alarm that produces noise*

| Behavior         | Action       | Input                  | Output     |
| ---------------- | ------------ | ---------------------- | ---------- |
| REQUEST_RESPONSE | triggerAlarm | TimerAlert: timerAlert | AlarmNoise |

### ClockTimer : *A simple timer that can be set to a target*
| Behavior         | Action       | Input                  | Output     |
| ---------------- | ------------ | ---------------------- | ---------- |
| REQUEST_RESPONSE | setTime      | TimeStamp: targetTime  | TimeStamp  |
| TIMER            | triggerTimer | TimeStamp: currentTime | TimerAlert |


### ALTERNATE ENTRY FORMAT ###
+ REQUEST_RESPONSE | setTime(targetTime) -> TimeStamp
+ TIMER | triggerTimer(currentTime) -> TimerAlert


 # IMPORTS

 [structures.md](./structures.md)
- AlarmNoise
- TimeStamp
- TimerAlert


# CONSTRAINTS

   - all_types_unique
   - all_instances_unique
   - all_instances_defined
   - all_enum_values_defined