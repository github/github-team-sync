from google.oauth2 import service_account
import os
import googleapiclient.discovery

SCOPES = [
   'https://www.googleapis.com/auth/admin.directory.group.readonly',
   'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
   'https://www.googleapis.com/auth/admin.directory.user.readonly'
   ]
SERVICE_ACCOUNT_FILE = '/tmp/credentials.json'

def create_service():
  credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  delegated_credentials = credentials.with_subject(os.environ.get("ADMIN"))

  service = googleapiclient.discovery.build(
    'admin',
    'directory_v1',
    credentials=delegated_credentials)

  return service

def printUsers():
    service = create_service().users()
    request = service.list(customer="my_customer", viewType="admin_view", projection="custom", customFieldMask="GithubUsername")
    while request is not None:
        users = request.execute()
        for u in users.get('users', []):
          if not u['suspended'] and not u['archived']:
            githubUsername = u.get('customSchemas', {}).get("GithubUsername", {}).get("GithubUsername")
            if githubUsername:
                print(f"{u['primaryEmail']}: {githubUsername}")
        request = service.list_next(request, users)

def printGroups():
    service = create_service().groups()
    request = service.list(customer="my_customer")
    while request is not None:
        groups = request.execute()
        for g in groups.get('groups', []):
          print(f"\n{g['name']:}")
          printMembers(g['id'])
        request = service.list_next(request, groups)

def printMembers(group_id):
    service = create_service().members()
    request = service.list(groupKey=group_id)
    while request is not None:
        members = request.execute()
        for g in members.get('members', []):
            print(g["email"])
        request = service.list_next(request, members)

def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    printUsers()
    printGroups()

if __name__ == '__main__':
    main()
# [END admin_sdk_directory_quickstart]