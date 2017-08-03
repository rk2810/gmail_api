from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import dateutil.parser as parser
import unicodecsv as csv
# to treat unicode nicely in csv
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
# specify scope as Modify cuz we want to mark the messages as read
store = file.Storage('storage.json')
credentials = store.get()
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    credentials = tools.run_flow(flow, store)
MAIL = discovery.build('gmail', 'v1', http=credentials.authorize(Http()))

user_id = 'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'

unread_msgs = MAIL.users().messages().list(userId='me', labelIds=[label_id_two]).execute()
# add label_id_one to search inbox

# to read obtained dict
message_list = unread_msgs['messages']

print ("Total unread messages in inbox: ", str(len(message_list)))

final_list = []

for mssg in message_list:
    temp_dict = {}
    m_id = mssg['id']  # get id of individual message
    message = MAIL.users().messages().get(userId=user_id, id=m_id).execute()  # fetch the message using API
    payload = message['payload']  # get payload of the message
    header = payload['headers']  # get header of the payload

    for one in header:  # get Subject
        if one['name'] == 'Subject':
            message_subject = one['value']
            temp_dict['Subject'] = message_subject
        else:
            pass

    for two in header:  # get date
        if two['name'] == 'Date':
            message_date = two['value']
            date_parse = (parser.parse(message_date))
            m_date = (date_parse.date())
            temp_dict['Date'] = str(m_date)
        else:
            pass

    for three in header:  # get the Sender
        if three['name'] == 'From':
            message_from = three['value']
            temp_dict['Sender'] = message_from
        else:
            pass

    temp_dict['Snippet'] = message['snippet']  # fetch message snippet

    try:

        # Fetching message body
        message_parts = payload['parts']
        part_one = message_parts[0]  # fetch first element of the part
        part_body = part_one['body']  # fetch body of the message
        part_data = part_body['data']  # fetch data from the body
        clean_one = part_data.replace("-", "+")  # from Base64 to UTF-8
        clean_one = clean_one.replace("_", "/")  # from Base64 to UTF-8
        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # from Base64 to UTF-8
        soup = BeautifulSoup(clean_two, "lxml")
        message_body = soup.body()

        temp_dict['Message_body'] = message_body

    except:
        pass

    print (temp_dict)
    final_list.append(temp_dict)  # We make a final dict to append into a csv

    MAIL.users().messages().modify(userId=user_id, id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()

print ("Total messaged retrived: ", str(len(final_list)))

# exporting the values as .csv
with open('data.csv', 'w') as csvfile:
    fieldnames = ['Sender', 'Subject', 'Date', 'Snippet', 'Message_body']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()
    for val in final_list:
        writer.writerow(val)
