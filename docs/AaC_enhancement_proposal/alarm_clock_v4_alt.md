# AaC Format Key
> -----------------------------------------------------------------------------------------------------
> ```
> # FEATURES
>
>
> ## Feature : *optional description of the feature type*
> __Is a:__ OptionalParentFeature
>
> ### SubFeature: (Same as Feature)
> #### SubSubFeature: (same as Feature)
>
> __Has:__
> - component1
> - component2
> - component3
> 
> - src_component --simple_action--> dest_component : *optional condition description*
> - src_component ==request/response==> dest_component : * optional condition description*
> - component <--action_both_ways--> dest_component : *optional condiion description*
> - component <==request/response_both_ways==> *optional condition description*
> - multiple_componentA, multiple_componentB, multiple_componentC --action--> m_component1, m_component2, m_component3
>       : *optional condition description on next line*
>
> ACTIONS
> + one_way_action(input1, input2, input3)
> + action_with_response(input1, input2, input3) -> output1, output2, output3
>
> ACTIONS (alternate format)
>| Action                 | Inputs                  | Outputs     |
>| ---------------------- | ----------------------- | ----------- |
>| triggerAlarm           | TimerAlert: timerAlert  | AlarmNoise  |
>
> # SCHEMA
>
> [LOCAL]()
> * LocalType1 : local_component1
>
> [external_filename](filepath)
> * ExternalType1 : component2
> * ExternalType2 : component3
>
>
> # CONSTRAINTS
> - constraint_name_1
> - constraint_name_2
>
>
> # USECASES
>
> ## USECASE1 : *optional description*
>
> ### INITIAL_CONDITIONS
> - component1 : {
>    fieldA: valueA
>    fieldB: valueB
>    fieldC: valueC
>}
> - component2 : {
>    fieldA: valueA
>    fieldB: valueB
>}
> ### SEQUENCE
> 1. src_component --action--> dest_component : description
> 2. src_component --action--> dest_component : description
> 3. src_component --action--> dest_component : description
>
>## USECASE2 : *optional description*
> .
> .
> .
> ```
> 



# FEATURES


## AlarmClock :  *A simple alarm clock*
__Is a:__ ParentAlarmClock

__Has:__
- Clock: clock
- ClockTimer : timer
- ClockAlarm: alarm
      
### Clock :  *A simple clock that keeps track of the current time*
__Does:__
| Action                 | Inputs                  | Outputs     |
| ---------------------- | ----------------------- | ----------- |
| getTime                |                         | TimeStamp   |

### ClockAlarm : *A simple alarm that produces noise*
__Does:__
| Action                 | Inputs                  | Outputs     |
| ---------------------- | ----------------------- | ----------- |
| triggerAlarm           | TimerAlert: timerAlert  | AlarmNoise  |

### ClockTimer : *A simple timer that can be set to a target*
__Does:__
| Action                 | Inputs                  | Outputs     |
| ---------------------- | ----------------------- | ----------- |
| setTime                | TimeStamp: targetTime   |             |


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