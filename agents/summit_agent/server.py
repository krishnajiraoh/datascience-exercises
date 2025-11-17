from mcp.server.fastmcp import FastMCP
import requests
import json
import asyncio

# Create an MCP server
mcp = FastMCP("Demo")
summit_service_url = "https://qamanualapex20copilotphase1-1.symphonysummit.com/api-copilot/REST/Summit_RESTWCF.svc/RESTService/CommonWS_JsonObjCall"
api_key = "vBNaLe5Lm7OdrwV2LLNHsxCfaPxyaP/X4KCbYv8E+ls="


@mcp.tool()
def create_incident(
    caller_email: str,
    incident_description: str,
):
    """
    Create an incident using the Summit `IM_LogOrUpdateIncident` API.

    Parameters
    ----------
    caller_email : str
        Caller/initiator email or ID.

    incident_description : str
        User description to add to the ticket (e.g., `"flickering more"`).

    Returns
    -------
    dict
        Parsed JSON response from the Summit API.

    Raises
    ------
    requests.exceptions.RequestException
        For network, connection, or timeout issues.

    ValueError
        If the response cannot be parsed as JSON.

    Example
    -------
    >>> response = create_incident(
    ...     caller_email="sysadmin@example.com",
    ...     user_log="flickering more"
    ... )
    >>> print(response)
    """

    payload = {
        "ServiceName": "IM_LogOrUpdateIncident",
        "objCommonParameters": {
            "_ProxyDetails": {
                "AuthType": "APIKEY",
                "APIKey": api_key,
                "ProxyID": 0,
                "ReturnType": "JSON",
                "OrgID": 1,
                "TokenID": ""
            },
            "incidentParamsJSON": {
                "IncidentContainerJsonObj": {
                    "Updater": "Executive",
                    "CI_ID": "",
                    "CI_Key": "",
                    "CI_Value": "",
                    "Ticket": {
                        "IsFromWebService": True,
                        "Ticket_No": "",
                        "Priority_Name": "",
                        "Classification_Name": "",
                        "Sup_Function": "IT",
                        "Caller_EmailID": caller_email,
                        "Status": "Assigned",
                        "Urgency_Name": "",
                        "Assigned_WorkGroup_Name": "",
                        "Medium": "Web",
                        "Impact_Name": "",
                        "Category_Name": "",
                        "SLA_Name": "",
                        "OpenCategory_Name": "",
                        "Source": "",
                        "Assigned_Engineer_Email": "",
                        "PageName": "TicketDetail"
                    },
                    "TicketInformation": {
                        "UserLog": incident_description
                    },
                    "CustomFields": []
                }
            },
            "RequestType": "RemoteCall"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(summit_service_url, json=payload, headers=headers)

    try:
        return response.json()
    except ValueError:
        raise ValueError(f"Invalid JSON response: {response.text}")
    

@mcp.tool()
def list_incidents(
    caller_email: str):
    """
    List the Incidents

    Parameters
    ----------
    caller_email : str
        Caller/initiator email or ID.

    Raises
    ------
    requests.exceptions.RequestException
        For network, connection, or timeout issues.

    ValueError
        If the response cannot be parsed as JSON.

    Example
    -------
    >>> response = list_incidents(
    ...     caller_email="sysadmin@example.com",
    ... )
    >>> print(response)
    """

    payload = {
        "ServiceName": "IM_GetMyIncidents",
        "objCommonParameters": {
            "_ProxyDetails": {
                "AuthType": "APIKEY",
                "APIKey": api_key,
                "ProxyID": 0,
                "ReturnType": "JSON",
                "OrgID": 1,
                "RequestType": "RemoteCall",
            },
            "InstanceCode" : "IT",
            "IncidentParam": {
            "CurrentPageIndex": 0,
            "OrgID": "1",
            "PageSize": 20,
            "Caller": "55",
            "CallerName": "",
            "CallerEmailID": "",
            "Instance": "IT",
            "Status": "All",
            "Workgroup": 0,
            "Executive": 0,
            #"SortColumn": null,
            "SortOrder": "DESC",
            #"FromID": null,
            #"ToID": null,
            #"FromDate": null,
            #"ToDate": null,
            "TextSearch": "Outlook",
            "TextSearchIn": "ALL",
            "Description": ""
            },
            "RequestType": "RemoteCall"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(summit_service_url, json=payload, headers=headers)
    tickets = json.loads(response.text)["OutputObject"]["MyTickets"]

    print(tickets[:3])

    return {
        "Status": response.status_code,
        "Response": json.dumps(tickets[:5])
    }
        
# EKM tool
@mcp.tool()
def get_ekm_response(query):
    """
    Send a query request to the EKM Summit API.

    This function calls the EKM `/user_query` endpoint and submits a user query.
    The API responds with a JSON string containing results or error details.

    Parameters
    ----------
    query : str
        The search query or issue description (e.g., "outlook issue").

    
    Returns
    -------
    dict
        A dictionary containing:
        - `status_code`: HTTP status code returned by the endpoint.
        - `response`: Parsed JSON response (if valid), otherwise raw text.

        
    Examples
    --------
    >>> get_ekm_response(
    ...     query="outlook issue",
    ... )
    {'status_code': 200, 'response': {...}}
    """

    url = "https://it-ekm-us.symphonysummit.com/EKM_FS/user_query"

    payload = {
        "query": query,
        "user_email": "sysadmin@summitaicoe.co",
        "itsm_platform": "Summit",
        "client_name": "inapex20-copilot"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return {
        "Status" : response.status_code,
        "Response" : response.text
    }

# Add a tool for making an API request
@mcp.tool()
def get_ticket_details(userID : int) -> dict:
    """
    Make an API request to retrieve ticket details.
    """
    payload = {
        "ServiceName": "IM_SR_GetTicketDetails",
        "objCommonParameters": {
            "_ProxyDetails": {
                "AuthType": "APIKEY",
                "APIKey": api_key,
                "ProxyID": 0,
                "ReturnType": "JSON",
                "OrgID": 1,
                "TokenID": ""
            },
            "objSR_SearchFilterParam": {
                "CurrentPageIndex": 0,
                "PageSize": 5,
                "OrgID":1,
                "Instance": "IT",
                "Status": "ALL",
                "strFromDate": "",
                "strToDate": "",
                "IsWebServiceRequest": "true",
                "TicketType": "SR",
                "TextSearch": "",
                "Caller": userID,
                "DateFilterType": "Created",
                "FromID": "",
                "ToID": "",
                "TicketNo": "",
                "UserID": userID
            }
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(summit_service_url, json=payload, headers=headers)
    tickets = json.loads(response.text)["OutputObject"]["TicketDetails"]["ServiceRequests"]

    return {
        "Status": response.status_code,
        "Response": json.dumps(tickets[:5])
    }


def main():
    # Initialize and run the server
    asyncio.run(mcp.run(transport='stdio'))

if __name__ == "__main__":
    main()
