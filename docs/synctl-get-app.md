# Manage Application

List Instana Application, application can be used to create Synthetic test.

## Syntax
```
synctl get app [id] [options]
```

## Options
```
commands:
    app|application

options:
  -h, --help            show this help message and exit
  --verify-tls           verify tls certificate
  
  --name-filter <app>   filter application by name
```

## Examples

### List Instana applications

```
synctl get app
```

### Filter application by name
```
synctl get app --name-filter <patten>
```


### Create Synthetic test with application id
```
synctl create test --apps "$APPLICATION1" "$APPLICATION2" "$APPLICATION3" ... -t <type>...
```


