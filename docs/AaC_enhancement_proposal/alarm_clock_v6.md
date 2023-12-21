# AaC Format Key
> -----------------------------------------------------------------------------------------------------
> ```
> # SYSTEM
>
>
> ## System<OptionalParentSystem> : *optional description of the system type*
> [ ] Abstract
>
> # STATES:
>      - STARTING:
>         - isConditionA >> RUNNING
>         - isConditionB >> STOPPING
>      - RUNNING:
          - isConditionB >> STOPPING
       - STOPPING:
          - isConditionC >> STOPPED
          - isConditionA >> RUNNING
       - STOPPED:
          - isConditionD >> STARTING
>
> # COMPONENTS
> - component1<OptionalParentSystem>
> - component2<OptionalParentSystem>
> - component3<OptionalParentSystem>
>
> # EXTERNAL_CONNECTIONS (maybe derived from INPUTS & OUTPUTS below)
> - system1
> - system2
> - system3
>
> # INPUTS
> - system1, system2 ==optionalComponent.action(param1, param2, param3)==> optionalResponseFeatureA
>
> # OUTPUTS
> - optionalComponent ==system3.action(param1, param2)==> system3 => optionalResponseFeatureB
> 
> # TESTCASES
>
> ## Testcase 1
> 1. 
>
> # REFERENCED_BY
> - Doc1D #997: { location: [x], size: [dx] }
> - Doc2D #998: { location: [x,y], size: [dx, dy] } 
> - Doc3D #999: { location: [x, y, z], size: [dx, dy, dz] }
> - Doc4D #1000: { location: [x, y, z, t], size: [ dx, dy, dz, dt] } 
>
> - TextDoc #997: { location: [x], size: [dx] }
> - Diagram #998: { location: [x,y], size: [dx, dy] } 
> - Space #999: { location: [x, y, z], size: [dx, dy, dz] }
> - Video #1000: { location: [x, y, z, t], size: [ dx, dy, dz, dt] } 
>
>
>
> - src_component --action--> dest_component : *optional condition description*
> - src_component ==action/response==> dest_component : * optional condition description*
> - component <--action_both_ways--> dest_component : *optional condition description*
> - component <==action/response_both_ways==> *optional condition description*
> - multiple_componentA, multiple_componentB, multiple_componentC --action--> m_component1, m_component2, m_component3
>       : *optional condition description on next line*
>
> ACTIONS
> + one_way_action(input1, input2, input3): *optional description*
> + action_with_response(input1, input2, input3) -> output1, output2, output3 : *optional description*
> ? isCondition(input1, input2, input3) -> Boolean : description
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
> - STATE: STOPPED
> - component1 : {
>    fieldA: valueA
>    fieldB: valueB
>    fieldC: valueC
>}
> - component2 : {
>    fieldA: valueA
>    fieldB: valueB
>}
> 
> ### STATE: RUNNING
> 1. src_component --action--> dest_component : description
> 2. src_component --action--> dest_component : description
> 3. src_component --action--> dest_component : description
>
> ### STATE: RUNNING
>
> ### STATE: STOPPING
> 
> ### STATE: STOPPED
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

# DEVELOPER NOTES

- systems can access their own components directly, but no other system's components directly
- components can output to external system.actions
- systems direct actions to their corresponding component
- components may not share the same action name
- the INPUT section defines public system or component actions
- the OUTPUT section defines connections to other systems
- system names must be unique. A two pass parse gets all system and component names on the first pass by recursing through all configuration files and directories. Thus import statements are not necessary.
- components define instances of their abstract <parent> system
- if System is abstract, then it does not exist as a component instance, but only as a Type to define components
