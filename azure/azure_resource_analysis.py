
import csv
import argparse
from datetime import datetime, timedelta, timezone
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_auth_file

TIMEDELTA_24_HOURS = timedelta(hours=24)
DATETIME_NOW_UTC = datetime.now(timezone.utc)
RESOURCE_NAME = 'cloudJenkinsResource'


class AzureUtils(object):
    def __init__(self):
        self.credentials_file = 'azure.json'
        self.storage_mgmt = get_client_from_auth_file(StorageManagementClient,
                                                      auth_path=self.credentials_file,
                                                      api_version='2019-06-01')
        self.compute_client = get_client_from_auth_file(ComputeManagementClient,
                                                        auth_path=self.credentials_file,
                                                        api_version='2019-07-01')
        self.resource_client = get_client_from_auth_file(ResourceManagementClient,
                                                         auth_path=self.credentials_file,
                                                         api_version='2019-07-01')


def add_args(parser):
    """ Supports the command-line arguments listed below """

    parser.add_argument('-az', '--azure_login',
                        required=True,
                        default=False,
                        action='store',
                        help='azure login file')
    parser.add_argument('-s', '--storage_account',
                        required=False,
                        default=False,
                        action='store',
                        help='storage account name')
    parser.add_argument('-r', '--resource_group',
                        required=False,
                        default=False,
                        action='store',
                        help='resource group name')
    return parser


class AzureMonitor(object):

    def __init__(self, args):
        self.azure_login = args.azure_login
        self.storage_account = args.storage_account
        self.resource_group = args.resource_group
        self.storage_mgmt = get_client_from_auth_file(StorageManagementClient,
                                                      auth_path=self.azure_login, api_version='2019-06-01')
        self.compute_client = get_client_from_auth_file(ComputeManagementClient,
                                                        auth_path=self.azure_login, api_version='2019-07-01')
        self.resource_client = get_client_from_auth_file(ResourceManagementClient,
                                                         auth_path=self.azure_login, api_version='2019-07-01')
        self.images = self.compute_client.images
        self.disks = self.compute_client.disks
        self.resources = self.resource_client.resources

    def delete_expired_images(self):
        """
            Maintiain Expire tag YYYY:MM:DD on expiry Images will be auto-terminated
        """

        images = self.images.list()
        print("****** CLOUD IMAGES ***********")
        for elem in images:
            if 'DO_NOT_CLEANUP' not in elem.name:
                creation_date = elem.tags['created'].split('T')[0]
                creation_date = datetime.strptime(creation_date, '%Y-%m-%d')
                current_date = f'{DATETIME_NOW_UTC.year}-{DATETIME_NOW_UTC.month}-{DATETIME_NOW_UTC.day}'
                current_date = datetime.strptime(current_date, '%Y-%m-%d')
                days_diff = (current_date - creation_date).days
                if days_diff > 5:
                    print(f"Deleting name {elem.name} days diff {days_diff} {elem.tags['product']}")
                    try:
                        self.images.delete(RESOURCE_NAME, elem.name)
                    except Exception as error:
                        print(f"Exception While deleting {error}")
        print("************************************")

    def delete_expired_disks(self):
        """
            Maintiain Expire tag YYYY:MM:DD on expiry disks will be auto-terminated
        """

        disks = self.disks.list()
        print("****** CLOUD IMAGE DISKS ***********")
        for elem in disks:
            if elem.tags and elem.tags.get('product', ''):
                creation_date = elem.time_created + TIMEDELTA_24_HOURS
                days_diff = (DATETIME_NOW_UTC - creation_date).days
                if 'DO_NOT_CLEANUP' not in elem.name and days_diff > 5:
                    print(
                        f"Deleting {elem.name} days diff {days_diff} {elem.tags['product']}")
                    self.disks.delete(RESOURCE_NAME, elem.name)
        print("************************************")

    def get_expire_date(self, tags):
        for key, value in tags.items():
            if 'expire' in key.lower():
                return value
        else:
            return False

    def delete_expired_resources(self):
        """
            Maintiain Expire tag YYYY:MM:DD on expiry Resources will be auto-terminated
        """
        cont = []
        without_expire = []
        with_expire = []
        print("************* VM details ***************")

        for elem in self.resources.list():
            if 'virtualMachines' in elem.type:
                if not elem.tags:
                    elem_list = [elem.name, 'Nil', 'Nil']
                    without_expire.append(elem_list)
                    #print(f"Name {elem.name} Tags not Found")
                    continue
                expire_name = self.get_expire_date(elem.tags)

                if expire_name:
                    try:
                        elem_list = [elem.name, elem.tags, expire_name]
                        with_expire.append(elem_list)
                        creation_date = datetime.strptime(expire_name, '%Y-%m-%d')
                        current_date = f'{DATETIME_NOW_UTC.year}-{DATETIME_NOW_UTC.month}-{DATETIME_NOW_UTC.day}'
                        current_date = datetime.strptime(current_date, '%Y-%m-%d')
                        days_diff = (current_date - creation_date).days
                        if days_diff > 1:
                            print(f"Deleting {elem.name} Expire date is {expire_name}")
                            self.resources.delete_by_id(elem.id, '2019-07-01')
                    except Exception as error:
                        print(f"Error message is {error}")
                else:
                    elem_list = [elem.name, elem.tags, 'Nil']
                    without_expire.append(elem_list)
                    #print(f"Name {elem.name} Expire date not specified")
                cont.append(elem)

        with open('without_tags.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Tags", "Expire"])
            writer.writerow(without_expire)
        with open('wit_tags.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Tags", "Expire"])
            writer.writerow(with_expire)
        return cont


def process(args):
    azure = AzureMonitor(args)
    azure.delete_expired_images()
    azure.delete_expired_disks()
    azure.delete_expired_resources()


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(description='Azure resource monitoring tool')
    parser = add_args(my_parser)
    args = parser.parse_args()
    proces(args)

