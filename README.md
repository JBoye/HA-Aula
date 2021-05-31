# HA-Aula

Work-In-Progress integration mellem Aula og Home Assistant

### Opsætning

```yaml
aula:
  username: UNILOGIN BRUGERNAVN
  password: UNILOGIN ADGANGSKODE
```

### Eksempel på sensor: 

<img width="395" alt="image" src="https://user-images.githubusercontent.com/5902488/119724332-e013b500-be6e-11eb-9529-afd4d4601123.png">


Selenium er nu droppet og i stedet lavet med inspiration fra Morten Helmstedt - helmstedt.dk


### Eksempel på middagslur-sensor (kræver at institutionen registrerer det):
```template:
  - sensor:
      - name: "Sovetid"
        state: >    
          {% set sleep_interval = state_attr('sensor.hoppelopperne_ellie', 'sleepIntervals')[0] %}
          {{strptime(sleep_interval.endTime, "%H:%M:%S") - strptime(sleep_interval.startTime, "%H:%M:%S")}}
```
