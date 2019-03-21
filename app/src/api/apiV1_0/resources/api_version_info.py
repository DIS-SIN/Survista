from flask_restful import Resource
import json
class V1(Resource):
    def get(self):
        try:
            with open("./api_v1/version_info.json") as f:
                info = json.load(f)
                f.close()
        except Exception as e:
            return {"error" : repr(e)}, 500
        for endpoint in info['endpoints']:
            print(" endpoint " + endpoint)
            self.__process_endpoint(info['endpoints'],info['endpoints'][endpoint])
        return info
    def __process_endpoint(self, endpoints, endpoint):
        #get the subEndpoints for the endpoint
        subEndpoints = endpoint.get('subEndpoints')
        #if the type of the subEndpoints field is a dictionary return as already processed
        if type(subEndpoints) == dict:
            return
        #if array means endpoint's subendpoints are not processed
        subEndpointsDict = {}
        if subEndpoints is not None:
            #loop over subEndpoints and call recursive processor
            for subEnd in subEndpoints:
                subEndpointsDict[subEnd] = self.__process_subendpoint(endpoints, subEnd)
            endpoint['subEndpoints'] = subEndpointsDict
    def __process_subendpoint(self,endpoints,subEndpointName):
        #get the subendpoint from the subEndpointName
        subEndpoint = endpoints.get(subEndpointName)
        subSubEndpoints = subEndpoint.get('subEndpoints')
        #get the subendpoint of that subendpoint to check if it's a leaf or its already been processed
        if type(subSubEndpoints) == dict or subSubEndpoints is None:
            #return the subEndpoint if so
            return subEndpoint
        #otherwise loop over the subendpoint's subendpoints and call the recursive function again
        subSubEndpointDict = {}
        for subSubEnd in subSubEndpoints:
            subSubEndpoint = self.__process_subendpoint(endpoints,subSubEnd)
            #add the processed endpoint with its name as the key
            subSubEndpointDict[subSubEnd] = subSubEndpoint
        #replace the subendpoint
        subEndpoint['subEndpoints'] = subSubEndpointDict
        return subEndpoint
        
