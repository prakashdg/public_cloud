######### Public Cloud resource monitoring Tool ############

1. Monitor All deployed public cloud resources

2. Based on tags terminate expired resources

3. Collect All resource details and create csv that helps to monitor all running resources

##########################################################


414f3a85c027:/azure/azure# python3 azure_resource_analysis.py --help
usage: azure_resource_analysis.py [-h] -az AZURE_LOGIN [-s STORAGE_ACCOUNT]
                                  [-r RESOURCE_GROUP]

Azure resource monitoring tool

optional arguments:
  -h, --help            show this help message and exit
  -az AZURE_LOGIN, --azure_login AZURE_LOGIN
                        azure login file
  -s STORAGE_ACCOUNT, --storage_account STORAGE_ACCOUNT
                        storage account name
  -r RESOURCE_GROUP, --resource_group RESOURCE_GROUP
                        resource group name

####################################################################
