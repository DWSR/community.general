#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Steve Smith <ssmith@atlassian.com>
# Atlassian open-source approval reference OSR-76.
#
# (c) 2020, Per Abildgaard Toft <per@minfejl.dk> Search and update function
# (c) 2021, Brandon McNama <brandonmcnama@outlook.com> Issue attachment functionality
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: jira
short_description: create and modify issues in a JIRA instance
description:
  - Create and modify issues in a JIRA instance.

options:
  uri:
    type: str
    required: true
    description:
      - Base URI for the JIRA instance.

  operation:
    type: str
    required: true
    aliases: [ command ]
    choices: [ attach, comment, create, edit, fetch, link, search, transition, update ]
    description:
      - The operation to perform.

  username:
    type: str
    required: true
    description:
      - The username to log-in with.

  password:
    type: str
    required: true
    description:
      - The password to log-in with.

  project:
    type: str
    required: false
    description:
      - The project for this operation. Required for issue creation.

  summary:
    type: str
    required: false
    description:
     - The issue summary, where appropriate.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  description:
    type: str
    required: false
    description:
     - The issue description, where appropriate.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  issuetype:
    type: str
    required: false
    description:
     - The issue type, for issue creation.

  issue:
    type: str
    required: false
    description:
     - An existing issue key to operate on.
    aliases: ['ticket']

  comment:
    type: str
    required: false
    description:
     - The comment text to add.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  status:
    type: str
    required: false
    description:
     - Only used when I(operation) is C(transition), and a bit of a misnomer, it actually refers to the transition name.

  assignee:
    type: str
    required: false
    description:
     - Sets the the assignee when I(operation) is C(create), C(transition) or C(edit).
     - Recent versions of JIRA no longer accept a user name as a user identifier. In that case, use I(account_id) instead.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  account_id:
    type: str
    description:
     - Sets the account identifier for the assignee when I(operation) is C(create), C(transition) or C(edit).
     - Note that JIRA may not allow changing field values on specific transitions or states.
    version_added: 2.5.0

  linktype:
    type: str
    required: false
    description:
     - Set type of link, when action 'link' selected.

  inwardissue:
    type: str
    required: false
    description:
     - Set issue from which link will be created.

  outwardissue:
    type: str
    required: false
    description:
     - Set issue to which link will be created.

  fields:
    type: dict
    required: false
    description:
     - This is a free-form data structure that can contain arbitrary data. This is passed directly to the JIRA REST API
       (possibly after merging with other required data, as when passed to create). See examples for more information,
       and the JIRA REST API for the structure required for various fields.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  jql:
    required: false
    description:
     - Query JIRA in JQL Syntax, e.g. 'CMDB Hostname'='test.example.com'.
    type: str
    version_added: '0.2.0'

  maxresults:
    required: false
    description:
     - Limit the result of I(operation=search). If no value is specified, the default jira limit will be used.
     - Used when I(operation=search) only, ignored otherwise.
    type: int
    version_added: '0.2.0'

  timeout:
    type: float
    required: false
    description:
      - Set timeout, in seconds, on requests to JIRA API.
    default: 10

  validate_certs:
    required: false
    description:
      - Require valid SSL certificates (set to `false` if you'd like to use self-signed certificates)
    default: true
    type: bool

  attachment:
    type: dict
    version_added: 2.5.0
    description:
      - Information about the attachment being uploaded.
    suboptions:
      filename:
        required: true
        type: path
        description:
          - The path to the file to upload (from the remote node) or, if I(content) is specified,
            the filename to use for the attachment
      content:
        type: str
        description:
          - The Base64 encoded contents of the file to attach. If not specified, the contents of I(filename) will be
            used instead.
      mimetype:
        type: str
        description:
          - The MIME type to supply for the upload. If not specified, best-effort detection will be
            done.

notes:
  - "Currently this only works with basic-auth."
  - "To use with JIRA Cloud, pass the login e-mail as the I(username) and the API token as I(password)."

author:
- "Steve Smith (@tarka)"
- "Per Abildgaard Toft (@pertoft)"
- "Brandon McNama (@DWSR)"
"""

EXAMPLES = r"""
# Create a new issue and add a comment to it:
- name: Create an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: create
    summary: Example Issue
    description: Created using Ansible
    issuetype: Task
  args:
    fields:
        customfield_13225: "test"
        customfield_12931: {"value": "Test"}
  register: issue

- name: Comment on issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: comment
    comment: A comment added by Ansible

# Assign an existing issue using edit
- name: Assign an issue using free-form fields
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key}}'
    operation: edit
    assignee: ssmith

# Create an issue with an existing assignee
- name: Create an assigned issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: create
    summary: Assigned issue
    description: Created and assigned using Ansible
    issuetype: Task
    assignee: ssmith

# Edit an issue
- name: Set the labels on an issue using free-form fields
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: edit
  args:
    fields:
        labels:
          - autocreated
          - ansible

# Updating a field using operations: add, set & remove
- name: Change the value of a Select dropdown
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: update
  args:
    fields:
      customfield_12931: [ {'set': {'value': 'Virtual'}} ]
      customfield_13820: [ {'set': {'value':'Manually'}} ]
  register: cmdb_issue
  delegate_to: localhost


# Retrieve metadata for an issue and use it to create an account
- name: Get an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: fetch
    issue: ANS-63
  register: issue

# Search for an issue
# You can limit the search for specific fields by adding optional args. Note! It must be a dict, hence, lastViewed: null
- name: Search for an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: search
    maxresults: 10
    jql: project=cmdb AND cf[13225]="test"
  args:
    fields:
      lastViewed: null
  register: issue

- name: Create a unix account for the reporter
  become: true
  user:
    name: '{{ issue.meta.fields.creator.name }}'
    comment: '{{ issue.meta.fields.creator.displayName }}'

# You can get list of valid linktypes at /rest/api/2/issueLinkType
# url of your jira installation.
- name: Create link from HSP-1 to MKY-1
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    operation: link
    linktype: Relates
    inwardissue: HSP-1
    outwardissue: MKY-1

# Transition an issue
- name: Resolve the issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: transition
    status: Resolve Issue
    account_id: 112233445566778899aabbcc
    fields:
      resolution:
        name: Done
      description: I am done! This is the last description I will ever give you.

# Attach a file to an issue
- name: Attach a file
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: HSP-1
    operation: attach
    attachment:
      filename: topsecretreport.xlsx
"""

import base64
import binascii
import json
import mimetypes
import os
import random
import string
import sys
import traceback

from ansible.module_utils.six.moves.urllib.request import pathname2url

from ansible.module_utils._text import to_text, to_bytes, to_native

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def request(
    url,
    user,
    passwd,
    timeout,
    data=None,
    method=None,
    content_type='application/json',
    additional_headers=None
):
    if data and content_type == 'application/json':
        data = json.dumps(data)

    # NOTE: fetch_url uses a password manager, which follows the
    # standard request-then-challenge basic-auth semantics. However as
    # JIRA allows some unauthorised operations it doesn't necessarily
    # send the challenge, so the request occurs as the anonymous user,
    # resulting in unexpected results. To work around this we manually
    # inject the basic-auth header up-front to ensure that JIRA treats
    # the requests as authorized for this user.
    auth = to_text(base64.b64encode(to_bytes('{0}:{1}'.format(user, passwd), errors='surrogate_or_strict')))

    headers = {}
    if isinstance(additional_headers) == dict:
        headers = additional_headers.copy()
    headers.update({
        "Content-Type": content_type,
        "Authorization": "Basic %s" % auth,
    })

    response, info = fetch_url(
        module, url, data=data, method=method, timeout=timeout, headers=headers
    )

    if info['status'] not in (200, 201, 204):
        error = None
        try:
            error = json.loads(info['body'])
        except Exception:
            module.fail_json(msg=to_native(info['body']), exception=traceback.format_exc())
        if error:
            msg = []
            for key in ('errorMessages', 'errors'):
                if error.get(key):
                    msg.append(to_native(error[key]))
            if msg:
                module.fail_json(msg=', '.join(msg))
            module.fail_json(msg=to_native(error))
        # Fallback print body, if it cant be decoded
        module.fail_json(msg=to_native(info['body']))

    body = response.read()

    if body:
        return json.loads(to_text(body, errors='surrogate_or_strict'))
    return {}


def post(url, user, passwd, timeout, data, content_type='application/json', additional_headers=None):
    return request(url, user, passwd, timeout, data=data, method='POST', content_type=content_type, additional_headers=additional_headers)


def put(url, user, passwd, timeout, data):
    return request(url, user, passwd, timeout, data=data, method='PUT')


def get(url, user, passwd, timeout):
    return request(url, user, passwd, timeout)


def create(restbase, user, passwd, params):
    createfields = {
        'project': {'key': params['project']},
        'summary': params['summary'],
        'issuetype': {'name': params['issuetype']}}

    if params['description']:
        createfields['description'] = params['description']

    # Merge in any additional or overridden fields
    if params['fields']:
        createfields.update(params['fields'])

    data = {'fields': createfields}

    url = restbase + '/issue/'

    return True, post(url, user, passwd, params['timeout'], data)


def comment(restbase, user, passwd, params):
    data = {
        'body': params['comment']
    }
    url = restbase + '/issue/' + params['issue'] + '/comment'

    return True, post(url, user, passwd, params['timeout'], data)


def edit(restbase, user, passwd, params):
    data = {
        'fields': params['fields']
    }
    url = restbase + '/issue/' + params['issue']

    return True, put(url, user, passwd, params['timeout'], data)


def update(restbase, user, passwd, params):
    data = {
        "update": params['fields'],
    }
    url = restbase + '/issue/' + params['issue']

    return True, put(url, user, passwd, params['timeout'], data)


def fetch(restbase, user, passwd, params):
    url = restbase + '/issue/' + params['issue']
    return False, get(url, user, passwd, params['timeout'])


def search(restbase, user, passwd, params):
    url = restbase + '/search?jql=' + pathname2url(params['jql'])
    if params['fields']:
        fields = params['fields'].keys()
        url = url + '&fields=' + '&fields='.join([pathname2url(f) for f in fields])
    if params['maxresults']:
        url = url + '&maxResults=' + str(params['maxresults'])
    return False, get(url, user, passwd, params['timeout'])


def transition(restbase, user, passwd, params):
    # Find the transition id
    turl = restbase + '/issue/' + params['issue'] + "/transitions"
    tmeta = get(turl, user, passwd, params['timeout'])

    target = params['status']
    tid = None
    for t in tmeta['transitions']:
        if t['name'] == target:
            tid = t['id']
            break

    if not tid:
        raise ValueError("Failed find valid transition for '%s'" % target)

    fields = dict(params['fields'])
    if params['summary'] is not None:
        fields.update({'summary': params['summary']})
    if params['description'] is not None:
        fields.update({'description': params['description']})

    # Perform it
    url = restbase + '/issue/' + params['issue'] + "/transitions"
    data = {'transition': {"id": tid},
            'fields': fields}
    if params['comment'] is not None:
        data.update({"update": {
            "comment": [{
                "add": {"body": params['comment']}
            }],
        }})

    return True, post(url, user, passwd, params['timeout'], data)


def link(restbase, user, passwd, params):
    data = {
        'type': {'name': params['linktype']},
        'inwardIssue': {'key': params['inwardissue']},
        'outwardIssue': {'key': params['outwardissue']},
    }

    url = restbase + '/issueLink/'

    return True, post(url, user, passwd, params['timeout'], data)


def attach(restbase, user, passwd, params):
    filename = params['attachment'].get('filename')
    content = params['attachment'].get('content')

    if not any((filename, content)):
        raise ValueError('at least one of filename or content must be provided')
    mime = params['attachment'].get('mimetype')

    if not os.path.isfile(filename):
        raise ValueError('The provided filename does not exist: %s' % filename)

    content_type, data = _prepare_attachment(filename, content, mime)

    url = restbase + '/issue/' + params['issue'] + '/attachments'
    return True, post(
        url, user, passwd, params['timeout'], data, content_type=content_type,
        additional_headers={"X-Atlassian-Token": "no-check"}
    )


# Ideally we'd just use prepare_multipart from ansible.module_utils.urls, but
# unfortunately it does not support specifying the encoding and also defaults to
# base64. Jira doesn't support base64 encoded attachments (and is therefore not
# spec compliant. Go figure). I originally wrote this function as an almost
# exact copypasta of prepare_multipart, but ran into some encoding issues when
# using the noop encoder. Hand rolling the entire message body seemed to work
# out much better.
#
# https://community.atlassian.com/t5/Jira-questions/Jira-dosen-t-decode-base64-attachment-request-REST-API/qaq-p/916427
#
# content is expected to be a base64 encoded string since Ansible doesn't
# support passing raw bytes objects.
def _prepare_attachment(filename, content=None, mime_type=None):
    def escape_quotes(s):
        return s.replace('"', '\\"')

    boundary = "".join(random.choice(string.digits + string.ascii_letters) for i in range(30))
    name = to_native(os.path.basename(filename))

    if not mime_type:
        try:
            mime_type = mimetypes.guess_type(filename or '', strict=False)[0] or 'application/octet-stream'
        except Exception:
            mime_type = 'application/octet-stream'
    main_type, sep, sub_type = mime_type.partition('/')

    if not content and filename:
        with open(to_bytes(filename, errors='surrogate_or_strict'), 'rb') as f:
            content = f.read()
    else:
        try:
            content = base64.decode(content)
        except binascii.Error as e:
            raise Exception("Unable to base64 decode file content: %s" % e)

    lines = [
        "--{0}".format(boundary),
        'Content-Disposition: form-data; name="file"; filename={0}'.format(escape_quotes(name)),
        "Content-Type: {0}".format("{0}/{1}".format(main_type, sub_type)),
        '',
        to_text(content),
        "--{0}--".format(boundary),
        ""
    ]

    return (
        "multipart/form-data; boundary={0}".format(boundary),
        "\r\n".join(lines)
    )


def main():

    global module
    module = AnsibleModule(
        argument_spec=dict(
            attachment=dict(type='dict', options=dict(
                content=dict(type='str'),
                filename=dict(type='path', required=True),
                mimetype=dict(type='str')
            )),
            uri=dict(type='str', required=True),
            operation=dict(type='str', choices=['attach', 'create', 'comment', 'edit', 'update', 'fetch', 'transition', 'link', 'search'],
                           aliases=['command'], required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            project=dict(type='str', ),
            summary=dict(type='str', ),
            description=dict(type='str', ),
            issuetype=dict(type='str', ),
            issue=dict(type='str', aliases=['ticket']),
            comment=dict(type='str', ),
            status=dict(type='str', ),
            assignee=dict(type='str', ),
            fields=dict(default={}, type='dict'),
            linktype=dict(type='str', ),
            inwardissue=dict(type='str', ),
            outwardissue=dict(type='str', ),
            jql=dict(type='str', ),
            maxresults=dict(type='int'),
            timeout=dict(type='float', default=10),
            validate_certs=dict(default=True, type='bool'),
            account_id=dict(type='str'),
        ),
        required_if=(
            ('operation', 'attach', ['issue', 'attachment']),
            ('operation', 'create', ['project', 'issuetype', 'summary']),
            ('operation', 'comment', ['issue', 'comment']),
            ('operation', 'fetch', ['issue']),
            ('operation', 'transition', ['issue', 'status']),
            ('operation', 'link', ['linktype', 'inwardissue', 'outwardissue']),
            ('operation', 'search', ['jql']),
        ),
        mutually_exclusive=[('assignee', 'account_id')],
        supports_check_mode=False
    )

    op = module.params['operation']

    # Handle rest of parameters
    uri = module.params['uri']
    user = module.params['username']
    passwd = module.params['password']
    if module.params['assignee']:
        module.params['fields']['assignee'] = {'name': module.params['assignee']}
    if module.params['account_id']:
        module.params['fields']['assignee'] = {'accountId': module.params['account_id']}

    if not uri.endswith('/'):
        uri = uri + '/'
    restbase = uri + 'rest/api/2'

    # Dispatch
    try:

        # Lookup the corresponding method for this operation. This is
        # safe as the AnsibleModule should remove any unknown operations.
        thismod = sys.modules[__name__]
        method = getattr(thismod, op)

        changed, ret = method(restbase, user, passwd, module.params)

    except Exception as e:
        return module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, meta=ret)


if __name__ == '__main__':
    main()
