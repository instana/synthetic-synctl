# synctl update cred

Update Synthetic credential

## Syntax
```
synctl update cred <cred-name> [options]
```
## Options

### Common options
```
    -h, --help                                         show this help message and exit
    --verify-tls                                       verify tls certificate
    
    --value <value>                                    set credential value
    --apps, --applications [<id> ...]                  set multiple applications
    --websites [<id> ...]                              set multiple websites
    --mobile-apps, --mobile-applications [<id> ...]    set multiple mobile appliactions         
```
## Examples
### Common Example for credentials
```
synctl update cred swecred --value <value> \
    --apps "$APPID-1" "$APPID-2" ...\
    --websites "$MOBILE-APPID-1" "$MOBILE-APPID-2" ...\ 
    --mobile-apps "$WEBSITE-1" "$WEBSITE-2" ...
```