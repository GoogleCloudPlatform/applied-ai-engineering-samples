# Define a backend config for a new project or environment.
See the Terraform Overview doc for examples on [flexible backend configurations](../t2x_terraform_overview.md#terraform-backends).

# Set [input variables](https://developer.hashicorp.com/terraform/language/values/variables#assigning-values-to-root-module-variables).
Use a `.tfvars` file, the `-var` command line argument, or the `TF_VAR_` environment variable.

# Initialize and apply.
```sh
tf init
tf apply
```

([back to deployment README](../README.md))
