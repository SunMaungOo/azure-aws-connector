from azure.storage.filedatalake import DataLakeServiceClient

class AzureDataLake:
    """
    Simplified API interface to azure data lake library 
    Usage : 
        with AzureDataLake(storage_account="storage-account-name",credential="credential") as datalake:
          pass
    """
    def __init__(self,storage_account:str,credential:str):
        """
        storage_account = name of the storage account
        credential = can be storage account access key , container shared access signature (SAS) token.
        container SAS token started with prefix "sp"
        """
        self.storage_account = storage_account
        self.credential=credential
        self.service_client = None

    def __enter__(self):
        """
        Connect the data lake service client
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up the data lake service client
        """
        if self.is_connected():
            self.service_client.close()

    def connect(self)->bool:
        """
        Connect to the storage account.
        Support only https connection method
        Will return false if we cannot connect to it
        """
        account_url = f"https://{self.storage_account}.dfs.core.windows.net"

        try:
            self.service_client = DataLakeServiceClient(account_url=account_url,credential=self.credential)
            return True
        except Exception as e:
            self.service_client = None

        return False

    def is_connected(self)->bool:
        """
        Check whether we have valid 
        """
        return self.service_client is not None

    def list_file_names(self,container_name:str,dir_path:str="/")->list[str]:
        """
        List the file name
        path : / = means return all the file in the container. If you path test ,
        it will list all the files which is in the test folder of the container.
        Path in this context mean the directory/directory format
        Return : 
            files = list of path which is in directory/fileName.fileExtension format
            return empty list on error
        Usage  = list_file_names(container_name="example-container",dir_path="folder1/folder2")
        """

        file_properties = self.list_file_properties(container_name=container_name,dir_path=dir_path)

        return [file_property["name"] for file_property in file_properties if file_property["is_directory"]==False] 
        
    def list_file_properties(self,container_name:str,dir_path:str="/")->list:
        """
        Return list of file properties 
        path : / = means return all the file properties in the container. If you path test ,
        it will list all the file properties which is in the test folder of the container.
        Path in this context mean the directory/directory format
        Return : 
            file_properties = list of file properties
            return empty list on error
        Usage  = list_file_properties(container_name="example-container",dir_path="folder1/folder2")
        """
        try:            
            with self.service_client.get_file_system_client(container_name) as file_system_client:

                return list(file_system_client.get_paths(path=dir_path))
                        
        except Exception:
            return []
        
    def download_file(self,container_name:str,dir_path:str,file_name:str,local_file_path:str)->bool:
        """
        Download the file
        
        Usage : Consider you wanted to download a file from folder1/folder2/test.csv from the container called "container-test" 
        as local-test.csv
        download_file(container_name="container-test",dir_path="folder1/folder2",file_name="test.csv",local_file_path="local-test.csv")
        """

        try:

            with self.service_client.get_file_system_client(container_name) as file_system_client:

                with file_system_client.get_directory_client(dir_path) as directory_client:

                    with directory_client.get_file_client(file_name) as file_client:

                        with open(local_file_path,"wb") as file:
                            stream = file_client.download_file()
                            file.write(stream.readall())
                            return True
            
        except Exception:
            return False
        
    def upload_file(self,container_name:str,dir_path:str,file_name:str,local_file_path:str)->bool:
        """
        Upload a file
        Usage:Consider we wanted to upload the local file called "local-test.csv" to folder1/folder2 which is in 
        container called "container-test" with the name of "remote-test.csv"
        upload_file(container_name="container-test",dir_path="folder1/folder2",file_name="remote-test.csv",local_file_path="local-test.csv")
        """
        try:

            with open(local_file_path,"rb") as local_file:
                local_data = local_file.read()

            with self.service_client.get_file_system_client(container_name) as file_system_client:

                with file_system_client.get_directory_client(dir_path) as directory_client:

                    with directory_client.get_file_client(file_name) as file_client:
                        
                        #create the file in the azure container
                        file_client.create_file()

                        #add the data into the file we have created
                        file_client.append_data(data=local_data,offset=0,length=len(local_data))

                        #flush the data back to azure data lake

                        file_client.flush_data(len(local_data))

                        return True
        
        except Exception:
            return False

    def delete_file(self,container_name:str,dir_path:str,file_name:str)->bool:
        """
        Delete a file
        Usage : Consider we wanted to delete the file called "remote-test.csv" which is in folder1/folder2 of container called
        "container-test"
        delete_file(container_name="container-test",dir_path="folder1/folder2",file_name="remote-test.csv")
        """

        try:
            with self.service_client.get_file_system_client(container_name) as file_system_client:

                with file_system_client.get_directory_client(dir_path) as directory_client:

                    with directory_client.get_file_client(file_name) as file_client:
                        
                        file_client.delete_file()

                        return True
        
        except Exception:

            return False