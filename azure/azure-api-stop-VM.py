#!/usr/bin/env python

'''
The Jenkins azure-cli plugin doesn't handle jmespath query strings at all.
I attempted to write a small python script to run the Azure commands but even 
that had problems dealing with the jmespath query strings.

So instead I'm using the Azure Python API to interact with Azure and manipulate the
existing VM.

Borrowed some Azure API stuff from here:
https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py

This script expects that the following environment vars are set:
AZURE_TENANT_ID: your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: your Azure Subscription Id
RESOURCE_GROUP: The Resource Group where your VM is configured
VM_NAME: the VM to operate on

'''

import os

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

def get_vm_status(resource_group_name, vm_name):
    # Construct headers
    header_parameters = {}
    header_parameters['Content-Type'] = 'application/json; charset=utf-8'
    print("resource group: {}\nvm_name: {}".format(resource_group_name, vm_name))
    return compute_client.virtual_machines.get(resource_group_name, vm_name, expand='instanceView',
                                                custom_headers=header_parameters).instance_view.statuses[1].display_status

def stop_vm():
    async_vm_stop = compute_client.virtual_machines.power_off(group, vm_name)
    async_vm_stop.wait()

if __name__ == "__main__":
    
    group = os.environ.get('RESOURCE_GROUP')
    vm_name = os.environ.get('VM_NAME')

    if group is None:
        print("Error: Environment variable \'RESOURCE_GROUP\' not set. Exiting...")
        exit(1)
    if vm_name is None:
        print("Error: Environment variable \'VM_NAME\' not set. Exiting...")
        exit(1)

    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    print("Checking VM \'{}\' status...".format(vm_name))
    status = get_vm_status(group, vm_name)
    print("Status: {}".format(status))
    if status != 'VM running':
        print("Error: VM not in \'VM running\' state, currently \'{}\' state. Exiting...".format(status))
        exit(1)
    
    print("Stopping VM \'{}\'".format(vm_name))
    stop_vm()

    print("Checking VM \'{}\' status...".format(vm_name))
    status = get_vm_status(group, vm_name)
    print("Status is now: \'{}\'".format(status))

