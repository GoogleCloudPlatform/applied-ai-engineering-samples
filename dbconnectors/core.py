"""
Provides the base class for all Connectors 
"""


from abc import ABC


class DBConnector(ABC):
    """
    The core class for all Connectors
    """

    connectorType: str = "Base"

    def __init__(self,
                project_id:str, 
                region:str, 
                instance_name:str,
                database_name:str, 
                database_user:str, 
                database_password:str,
                dataset_name:str):
        """
        Args:
            project_id (str | None): GCP Project Id.
            dataset_name (str): 
            TODO
        """
        self.project_id = project_id
        self.region = region 
        self.instance_name = instance_name 
        self.database_name = database_name
        self.database_user = database_user
        self.database_password = database_password
        self.dataset_name = dataset_name
    