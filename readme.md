# DDNS script
Just run it, look into running this as a service when you migrate the cluster host to NixOS

## SOPS
Decided to use SOPS to encrypt values

Make sure you can decrypt on the machine you are running this on with:
```
sops -d secrets.enc.yaml
```
Make sure your key is defined in your sops config dir in the form of: 
.../sops/age/keys.txt

