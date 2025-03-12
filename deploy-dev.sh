#!/bin/bash
This script deploys the Metrics application to a development Kubernetes environment

To run this script in different environments:

- Git Bash (Recommended on Windows):
  - Open Git Bash.
  - Navigate to the directory containing this script: `cd path/to/script`
  - Run the script: `./deploy-dev.sh`

- PowerShell (Not recommended, use Git Bash instead):
  - PowerShell does not natively support executing bash scripts directly.
  - You can try to use the Windows Subsystem for Linux (WSL) if you have it enabled.
  - It's highly recommended to use Git Bash for a smoother experience.
  
Deploy using the development values
./deploy-helm.sh development

Apply the values-dev.yaml file override
helm upgrade metrics ./metrics-chart --values ./metrics-chart/values-dev.yaml --namespace default

echo "Development deployment complete!"