# USECASES

## Set Alarm Time : *The user sets the time for the alarm clock.*
1. user --setAlarm--> alarm: The user sets the time on system.
2. alarm --setTime--> timer: The alarm clock stores the time in the timer.

## Trigger Alarm : The alarm emits a noise at the user-specified time.
1. clock --emitCurrentTime--> timer : The clock emits the current time to the timer.
2. timer --emitAlarmTrigger--> alarm : The timer emits an alarm notification to the alarm.
3. alarm --triggerSpeaker--> alarmClock : The alarm is activated to emit a noise from the AlarmClock speaker.
4. alarmClock --emitAlarmNoise--> user : The alarm speaker emits the alarm noise to the user.

# SCHEMA

[LOCAL]()

[alarm_clock.md](./alarm_clock.md)
- AlarmClock : alarmClock

[structures.md](./structures.md)
- ClockAlarm : alarm
- ClockTimer : timer
- Clock : clock

[external.md](./external.md)
- Person : user





