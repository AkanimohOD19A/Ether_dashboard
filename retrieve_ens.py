import requests
from subgrounds import Subgrounds
from datetime import datetime
from subgrounds.subgraph import SyntheticField

## Retreive Data
query = """
{
  # latest 1000 ENS registrations
  registrations(first:1000, orderBy:registrationDate, orderDirection:desc){
    domain{
      name # like`vitalik.eth`
    }
    registrant {
      id # hexadecimal address
    }
    registrationDate 
    cost 
    expiryDate 
  }
}
"""


def get_data(query):
    """This function posts a request to make an API call to ENS Subgraph URL
    parameters:
    ------------
    query: payload containing specific data we need
    return:
    -------
    response.json(): queried data in JSON format
    """

    response = requests.post('https://api.thegraph.com/subgraphs/name/ensdomains/ens'
                             '',
                             json={"query": query})

    if response.status_code == 200:  # code 200 means no errors
        return response.json()
    else:  # if errors, print the error code for debugging
        raise Exception("Query failed with return code {}".format(response.staus_code))


def get_subgraphs():
    print("Requesting Data ..")
    data = get_data(query)
    # display(data) ## Returns a json-like structure.

    sg = Subgrounds()
    # load ENS subgraph
    ens = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/ensdomains/ens')

    ## query_df will show data as per Pandas

    print("Adding Synthetic Fields ..")
    # registrationdate synthetic field
    ens.Registration.registrationdate = SyntheticField(
        lambda registrationDate: str(datetime.fromtimestamp(registrationDate)),
        SyntheticField.STRING,
        ens.Registration.registrationDate
    )

    # expirydate synthetic field
    ens.Registration.expirydate = SyntheticField(
        lambda expiryDate: str(datetime.fromtimestamp(expiryDate)),
        SyntheticField.STRING,
        ens.Registration.expiryDate
    )

    # Select the latest 1000 registration names by registration datetime
    registrations = ens.Query.registrations(
        first=1000,  # latest 1000 registrations
        orderBy=ens.Registration.registrationDate,  # order registrations by time
        orderDirection="desc"  # latest registration data will be first
    )

    field_paths = [
        registrations.domain.name,  # ens domain like "vitalik.eth"
        registrations.registrant.id,  # hexadecimal eth address
        registrations.registrationdate,  # time in epoch format
        registrations.cost,  # price for registration
        registrations.expirydate  # expiry date of domain
    ]

    df = sg.query_df(field_paths)
    # print(df.head())

    ### Transformations
    # Convert `registrations_cost` column from wei to ether
    # 1 ether = 1,000,000,000,000,000,000 wei (10^18)
    df['registrations_cost'] = df['registrations_cost'] / (10 ** 18)

    print("Transforming Data ..")
    # rename columns for simplicity
    df = df.rename(columns={'registrations_domain_name': 'ens_name',
                            'registrations_registrant_id': 'owner_address',
                            'registrations_registrationdate': 'registration_date',
                            'registrations_cost': 'registration_cost_ether',
                            'registrations_expirydate': 'expiry_date'
                            })
    # inspect the changes in df

    # print(df.head())
    print("Retrived Data successfully")

    return df


if __name__ == '__main__':
    get_subgraphs()