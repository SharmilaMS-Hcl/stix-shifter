from stix_shifter_utils.modules.base.stix_transmission.base_json_results_connector import BaseJsonResultsConnector
from stix_shifter_utils.utils.error_response import ErrorResponder
from stix_shifter_utils.utils import logger
import json

class ResultsConnector(BaseJsonResultsConnector):
    def __init__(self, api_client):
        self.api_client = api_client
        self.logger = logger.set_logger(__name__)
        self.connector = __name__.split('.')[1]

    async def create_results_connection(self, query_data, offset, length):
        try:
            query_data = query_data.replace('\'', "\"")
            query_json = json.loads(query_data)
            response, namespace = await self.api_client.get_search_results(query_json)
            response_code = response['code']
            return_obj = dict()
            if response_code == 200:
                response['report'] = response['data']
                response['data'] =  query_json['data']
                response['dataType'] = query_json['dataType']
                extra_info = None
                try:
                    extra_info = response['report']['full']['data']['info']
                except Exception as e:
                    pass
                if extra_info:
                    response['external_reference'] = {"source_name":"VirusTotal_Connector","url": extra_info['permalink']}
                else:
                    response['external_reference'] = {"source_name":"VirusTotal_Connector","url":"N/A"} # No permalink attributes, use "N/A" instead
                response['namespace'] = namespace
                return_obj['success'] = True
                return_obj['data'] = [response]
            else:
                ErrorResponder.fill_error(return_obj, response, connector=self.connector)
                return_obj['error'] = response['error']
            return return_obj
        except Exception as err:
            self.logger.error('error when creating search: {}'.format(err))
            raise