# synctl command
```
Usage: synctl [--verify-tls] <command> [options]

Options:
  -h, --help            show this help message and exit
  --version, -v         show version
  --verify-tls          verify tls certificate

Commands:
    config              manage configuration file
    create              create a Synthetic test, credential and smart alert
    get                 get Synthetic tests, locations, credentials, smart alert and pop-size
    patch               patch a Synthetic test
    update              update a Synthetic test and smart alert
    delete              delete Synthetic tests, locations credentials and smart alert

Use "synctl <command> -h/--help" for more information about a command.
```

# Document
- [synctl config](synctl-config.md) - Add configuration of Instana.
- [synctl get test](synctl-get-test.md) - Display Synthetic tests.
- [synctl get result](synctl-get-result.md) - Display Synthetic test result.
- [synctl get location](synctl-get-loc.md) - Display Synthetic locations.
- [synctl get alert](synctl-get-alert.md) - Display smart alert.
- [synctl get application](synctl-get-app.md) - Display Instana application.
- [synctl get pop-cost](synctl-get-cost.md) - Estimate cost of Instana hosted Synthetic POP.
- [synctl get pop-size](synctl-get-size.md) - Estimate size of Instana hosted Synthetic PoP.
- [synctl create test](synctl-create-test.md) - Create Synthetic tests.
- [synctl create alert](synctl-create-alert.md) - Create smart alert.
- [synctl create/update/delete cred](synctl-credential.md) - Manage credentials.
- [synctl delete test](synctl-delete-test.md) - Delete Synthetic tests.
- [synctl delete location](synctl-delete-loc.md) - Delete Synthetic locations.
- [synctl delete alert](synctl-delete-alert.md) - Delete smart alert.
- [synctl patch test](synctl-patch-test.md) - Patch Synthetic test.
- [synctl update alert](synctl-update-alert.md) - Update properties of Smart Alert.
- [synctl update test](synctl-update-test.md) - Update properties of Synthetic test.
