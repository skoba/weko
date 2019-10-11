# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Module of weko-items-ui utils.."""

import csv
from datetime import datetime
from io import StringIO

from flask import current_app, session
from flask_babelex import gettext as _
from flask_login import current_user
from invenio_db import db
from invenio_records.api import RecordBase
from jsonschema import ValidationError
from sqlalchemy import MetaData, Table
from weko_records.api import ItemTypes
from weko_user_profiles import UserProfile
from weko_workflow.models import Action as _Action
from invenio_indexer.api import RecordIndexer


def get_list_username():
    """Get list username.

    Query database to get all available username
    return: list of username
    """
    current_user_id = current_user.get_id()
    user_index = 1
    result = list()
    while True:
        try:
            if not int(current_user_id) == user_index:
                user_info = UserProfile.get_by_userid(user_index)
                result.append(user_info.get_username)
            user_index = user_index + 1
        except Exception as e:
            current_app.logger.error(e)
            break

    return result


def get_list_email():
    """Get list email.

    Query database to get all available email
    return: list of email
    """
    current_user_id = current_user.get_id()
    result = list()
    try:
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if not int(current_user_id) == item[0]:
                result.append(item[1])
    except Exception as e:
        result = str(e)

    return result


def get_user_info_by_username(username):
    """Get user information by username.

    Query database to get user id by using username
    Get email from database using user id
    Pack response data: user id, user name, email

    parameter:
        username: The username
    return: response pack
    """
    result = dict()
    try:
        user = UserProfile.get_by_username(username)
        user_id = user.user_id

        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if item[0] == user_id:
                result['username'] = username
                result['user_id'] = user_id
                result['email'] = item[1]
                return result
        return None
    except Exception as e:
        result['error'] = str(e)


def validate_user(username, email):
    """Validate user information.

    Get user id from database using username
    Get user id from database using email
    Compare 2 user id to validate user information
    Pack responde data:
        results: user information (username, user id, email)
        validation: username is match with email or not
        error: null if no error occurs

    param:
        username: The username
        email: The email
    return: response data
    """
    result = {
        'results': '',
        'validation': False,
        'error': ''
    }
    try:
        user = UserProfile.get_by_username(username)
        user_id = 0

        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if item[1] == email:
                user_id = item[0]
                break

        if user.user_id == user_id:
            user_info = dict()
            user_info['username'] = username
            user_info['user_id'] = user_id
            user_info['email'] = email
            result['results'] = user_info
            result['validation'] = True
        return result
    except Exception as e:
        result['error'] = str(e)

    return result


def get_user_info_by_email(email):
    """
    Get user information by email.

    Query database to get user id by using email
    Get username from database using user id
    Pack response data: user id, user name, email

    parameter:
        email: The email
    return: response
    """
    result = dict()
    try:
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()
        for item in data:
            if item[1] == email:
                user = UserProfile.get_by_userid(item[0])
                if user is None:
                    result['username'] = ""
                else:
                    result['username'] = user.get_username
                result['user_id'] = item[0]
                result['email'] = email
                return result
        return None
    except Exception as e:
        result['error'] = str(e)


def get_user_information(user_id):
    """
    Get user information user_id.

    Query database to get email by using user_id
    Get username from database using user id
    Pack response data: user id, user name, email

    parameter:
        user_id: The user_id
    return: response
    """
    result = {
        'username': '',
        'email': ''
    }
    user_info = UserProfile.get_by_userid(user_id)
    if user_info is not None:
        result['username'] = user_info.get_username

    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    table_name = 'accounts_user'

    user_table = Table(table_name, metadata)
    record = db.session.query(user_table)

    data = record.all()

    for item in data:
        if item[0] == user_id:
            result['email'] = item[1]
            return result

    return result


def get_user_permission(user_id):
    """
    Get user permission user_id.

    Compare current id with id of current user
    parameter:
        user_id: The user_id
    return: true if current id is the same with id of current user.
    If not return false
    """
    current_id = current_user.get_id()
    if current_id is None:
        return False
    if str(user_id) == current_id:
        return True
    return False


def get_current_user():
    """
    Get user id of user currently login.

    parameter:
    return: current_id
    """
    current_id = current_user.get_id()
    return current_id


def get_actionid(endpoint):
    """
    Get action_id by action_endpoint.

    parameter:
    return: action_id
    """
    with db.session.no_autoflush:
        action = _Action.query.filter_by(
            action_endpoint=endpoint).one_or_none()
        if action:
            return action.id
        else:
            return None


def parse_ranking_results(results,
                          display_rank,
                          list_name='all',
                          title_key='title',
                          count_key=None,
                          pid_key=None,
                          search_key=None,
                          date_key=None):
    """Parse the raw stats results to be usable by the view."""
    ranking_list = []
    if pid_key:
        url = '../records/{0}'
        key = pid_key
    elif search_key:
        url = '../search?page=1&size=20&search_type=1&q={0}'
        key = search_key
    else:
        url = None

    if results and list_name in results:
        rank = 1
        count = 0
        date = ''
        for item in results[list_name]:
            t = {}
            if count_key:
                if not count == int(item[count_key]):
                    rank = len(ranking_list) + 1
                    count = int(item[count_key])
                t['rank'] = rank
                t['count'] = count
            elif date_key:
                new_date = \
                    datetime.utcfromtimestamp(
                        item[date_key]).strftime('%Y-%m-%d')
                if new_date == date:
                    t['date'] = ''
                else:
                    t['date'] = new_date
                    date = new_date
            title = item[title_key]
            if title_key == 'user_id':
                user_info = UserProfile.get_by_userid(title)
                if user_info:
                    title = user_info.username
                else:
                    title = 'None'
            t['title'] = title
            t['url'] = url.format(item[key]) if url and key in item else None
            ranking_list.append(t)
            if len(ranking_list) == display_rank:
                break
    return ranking_list


def validate_form_input_data(result: dict, item_id: str, data: dict):
    """Validate input data.

    :param result: result dictionary.
    :param item_id: item type identifier.
    :param data: form input data
    """
    item_type = ItemTypes.get_by_id(item_id)
    json_schema = item_type.schema.copy()

    data['$schema'] = json_schema.copy()
    validation_data = RecordBase(data)
    try:
        validation_data.validate()
    except ValidationError as error:
        result["is_valid"] = False
        if 'required' == error.validator:
            result['error'] = _('Please input all required item.')
        elif 'pattern' == error.validator:
            result['error'] = _('Please input the correct data.')
        else:
            result['error'] = _(error.message)


def update_json_schema_by_activity_id(json, activity_id):
    """Update json schema by activity id.

    :param json: The json schema
    :param activity_id: Activity ID
    :return: json schema
    """
    if not session.get('update_json_schema') or not session[
            'update_json_schema'].get(activity_id):
        return None
    error_list = session['update_json_schema'][activity_id]

    if error_list:
        for item in error_list['required']:
            sub_item = item.split('.')
            if len(sub_item) == 1:
                json['required'] = sub_item
            else:
                if json['properties'][sub_item[0]].get('items'):
                    if not json['properties'][sub_item[0]]['items'].get(
                            'required'):
                        json['properties'][sub_item[0]]['items']['required'] \
                            = []
                    json['properties'][sub_item[0]]['items'][
                        'required'].append(sub_item[1])
                else:
                    json['properties'][sub_item[0]]['required'].append(
                        sub_item[1])
        for item in error_list['pattern']:
            sub_item = item.split('.')
            if len(sub_item) == 2:
                creators = json['properties'][sub_item[0]].get('items')
                if not creators:
                    break
                for creator in creators.get('properties'):
                    if creators['properties'][creator].get('items'):
                        givename = creators['properties'][creator]['items']
                        if givename['properties'].get(sub_item[1]):
                            if not givename.get('required'):
                                givename['required'] = []
                            givename['required'].append(sub_item[1])
    return json


def package_exports(item_type_data):
    """Export TSV Files.

        Arguments:
            pid_type     -- {string} 'doi' (default) or 'cnri'
            reg_value    -- {string} pid_value

        Returns:
            return       -- PID object if exist

    """
    """Package the .tsv files into one zip file."""
    tsv_output = StringIO()
    jsonschema_url = '=HYPERLINK("' + item_type_data.get('root_url') + \
                     item_type_data.get('jsonschema') + '")'

    tsv_writer = csv.writer(tsv_output, delimiter='\t')
    tsv_writer.writerow(['#ItemType',
                         item_type_data.get('name'),
                         jsonschema_url])

    keys = item_type_data['keys']
    labels = item_type_data['labels']
    tsv_metadata_writer = csv.DictWriter(tsv_output,
                                         fieldnames=keys,
                                         delimiter='\t')
    tsv_metadata_label_writer = csv.DictWriter(tsv_output,
                                               fieldnames=labels,
                                               delimiter='\t')
    tsv_metadata_writer.writeheader()
    tsv_metadata_label_writer.writeheader()
    # for recid in item_type_data.get('recids'):
    # record = WekoRecord.get_record_by_pid(recid)
    # tsv_metadata_writer.writerow({
    #     '#.id': str(recid),
    #     '.uri': item_type_data.get('root_url') + 'records/' + str(recid),
    #     '.path[0]': record.get('path')[0]
    # })

    return tsv_output

from weko_deposit.api import WekoRecord
import numpy

def make_stats_tsv(item_type_id, recids):
    """Prepare TSV data for each Item Types.

        Arguments:
            pid_type     -- {string} 'doi' (default) or 'cnri'
            reg_value    -- {string} pid_value

        Returns:
            return       -- PID object if exist

    """
    item_type = ItemTypes.get_by_id(item_type_id).render

    table_row_properties = item_type['table_row_map']['schema'].get(
        'properties')

    class Records:
        recids = []
        records = {}
        attr_data = {}
        attr_output = {}

        def __init__(self, recids):
            self.recids = recids
            for recid in recids:
                record = WekoRecord.get_record_by_pid(recid)
                self.records[recid] = record

        def get_max_ins(self, attr):
            max = 0
            self.attr_data[attr] = {'max_size': 0
            }
            for record in self.records:
                if isinstance(self.records[record].get(attr), dict) and self.records[record].get(attr).get('attribute_value_mlt'):
                    self.attr_data[attr][record] = self.records[record][attr]['attribute_value_mlt']
                else:
                    if self.records[record].get(attr):
                        self.attr_data[attr][record] = self.records[record].get(attr)
                    else:
                        self.attr_data[attr][record] = []
                rec_size = len(self.attr_data[attr][record])
                if rec_size > max:
                    max = rec_size
            self.attr_data[attr]['max_size'] = max

            return self.attr_data[attr]['max_size']

        def print_value(self, recid, attr):
            if not self.attr_output.get(recid):
                self.attr_output[recids] = []
            ret = self.attr_data[attr][recid]
            ret.extend(['' for i in range(len(self.attr_data[attr][recid]), self.attr_data[attr]['max_size'])])
            self.attr_output[recids].extend(ret)

        def get_sub_item(self, item_key, item_label, pos, properties, data=None):
            """Prepare TSV data for each Item Types.

                Arguments:
                    properties     -- {string} 'doi' (default) or 'cnri'

                Returns:
                    return       -- PID object if exist

            """
            ret = []
            ret_label = []
            ret_data = {}
            for recid in recids:
                ret_data[recid] = []
            for key in properties:
                if properties[key].get('type'):
                    if properties[key]['type'] == 'array':
                        current_app.logger.debug(key)
                        max_ins = 0
                        if max_ins > 1:
                            for i in range(0, max_ins):
                                sub, sublabel = self.get_sub_item(
                                    key,
                                    properties[key].get('title'),
                                    i,
                                    properties[key]['items']['properties'])
                                for idx in range(len(sub)):
                                    ret.append(item_key + '.' + sub[idx])
                                    ret_label.append(item_label + '.' + sublabel[idx])
                        else:
                            sub, sublabel = self.get_sub_item(
                                key,
                                properties[key].get('title'),
                                None,
                                properties[key]['items']['properties'])
                            for idx in range(len(sub)):
                                ret.append(item_key + '.' + sub[idx])
                                ret_label.append(item_label + '.' + sublabel[idx])
                    elif properties[key]['type'] == 'object':
                        sub, sublabel = self.get_sub_item(
                            key,
                            properties[key].get('title'),
                            None,
                            properties[key]['properties'])
                        for idx in range(len(sub)):
                            ret.append(item_key + '.' + sub[idx])
                            ret_label.append(item_label + '.' + sublabel[idx])
                    else:
                        if pos:
                            ret.append(item_key + '[{}]'.format(str(pos)) + '.' + key)
                            if pos < len(self.attr_data[item_key][recid]):
                                # current_app.logger.debug(self.attr_data[item_key][recid])
                                ret_label.append(self.attr_data[item_key][recid][pos][key])
                            else:
                                ret_label.append('')
                        else:
                            current_app.logger.debug(self.attr_data[item_key][recid])
                            ret.append(item_key + '.' + key)
                            ret_label.append(self.attr_data[item_key][recid][0][key])
                            # ret_label.append(item_label + '.'
                            #                 + properties[key].get('title'))

            return ret, ret_label

    records = Records(recids)

    ret = ['#.id', '.uri']
    ret_label = ['#ID', 'URI', 'インデックス', '公開日']

    # for idx in range(records.get_max_ins('path')):
    max_path = records.get_max_ins('path')
    ret.extend(['.path[{}]'.format(i) for i in range(max_path)])
    ret_label.extend(['.インデックス[{}]'.format(i) for i in range(max_path)])
    # for recid in recids:
    #     current_app.logger.debug(records.print_value(recid, 'path'))

    ret.append('.metadata.pubdate')
    ret_label.append('公開日')

    for item_key in item_type.get('table_row'):
        item = table_row_properties.get(item_key)
        max_path = records.get_max_ins(item_key)
        if item.get('type') == 'array':
            if max_path > 1:
                for i in range(0, max_path):
                    key, label = records.get_sub_item(item_key,
                                              item.get('title'),
                                              i,
                                              item['items']['properties'])
                    ret.extend(key)
                    ret_label.extend(label)
            else:
                key, label = records.get_sub_item('.metadata.' + item_key,
                                          item.get('title'),
                                          None,
                                          item['items']['properties'])
                ret.extend(key)
                ret_label.extend(label)
        elif item.get('type') == 'object':
            key, label = records.get_sub_item(item_key,
                                      item.get('title'),
                                      None,
                                      item['properties'])
            ret.extend(key)
            ret_label.extend(label)

        current_app.logger.debug(ret_label)

    return ret, ret_label


def get_sub_item(item_key, item_label, pos, properties, data=None):
    """Prepare TSV data for each Item Types.

        Arguments:
            properties     -- {string} 'doi' (default) or 'cnri'

        Returns:
            return       -- PID object if exist

    """
    ret = []
    ret_label = []
    for key in properties:
        if properties[key].get('type'):
            if properties[key]['type'] == 'array':
                max_ins = 0
                if max_ins > 1:
                    for i in range(0, max_ins):
                        sub, sublabel = get_sub_item(
                            key,
                            properties[key].get('title'),
                            i,
                            properties[key]['items']['properties'])
                        for idx in range(len(sub)):
                            ret.append(item_key + '.' + sub[idx])
                            ret_label.append(item_label + '.' + sublabel[idx])
                else:
                    sub, sublabel = get_sub_item(
                        key,
                        properties[key].get('title'),
                        None,
                        properties[key]['items']['properties'])
                    for idx in range(len(sub)):
                        ret.append(item_key + '.' + sub[idx])
                        ret_label.append(item_label + '.' + sublabel[idx])
            elif properties[key]['type'] == 'object':
                sub, sublabel = get_sub_item(
                    key,
                    properties[key].get('title'),
                    None,
                    properties[key]['properties'])
                for idx in range(len(sub)):
                    ret.append(item_key + '.' + sub[idx])
                    ret_label.append(item_label + '.' + sublabel[idx])
            else:
                if data:
                    current_app.logger.debug('----------------------------')
                    current_app.logger.debug(item_key + '.' + key)
                    # current_app.logger.debug(key)
                    current_app.logger.debug(data)
                
                if pos:
                    item_key = item_key + '[{}]'.format(str(pos))
                    item_label = item_label + '#{}'.format(str(pos))
                ret.append(item_key + '.' + key)
                ret_label.append(item_label + '.'
                                 + properties[key].get('title'))

    return ret, ret_label


def get_max_ins(attribute_id):
    """Fill Item Metadata to TSV Row.

        Arguments:
            pid_type     -- {string} 'doi' (default) or 'cnri'
            reg_value    -- {string} pid_value

        Returns:
            return       -- PID object if exist

    """
    import random

    return random.randrange(0, 3)


def write_report_tsv_rows():
    """Fill Item Metadata to TSV Row.

        Arguments:
            pid_type     -- {string} 'doi' (default) or 'cnri'
            reg_value    -- {string} pid_value

        Returns:
            return       -- PID object if exist

    """
    pass


def get_author_id_by_name(names=[]):
    """Get Author_id by list name.

        Arguments:
            names     -- {string} list names

        Returns:
            weko_id       -- author id of author has search result

    """
    query_should = [
        {
            "match": {
                "authorNameInfo.fullName": name
            }
        } for name in names]

    body = {
        "query": {
            "bool": {
                "should": query_should
            }
        },
        "size": 1
    }
    indexer = RecordIndexer()
    result = indexer.client.search(
        index=current_app.config['WEKO_AUTHORS_ES_INDEX_NAME'],
        body=body
    )
    weko_id = None

    if isinstance(result, dict) and isinstance(result.get('hits'), dict) and \
            isinstance(result['hits'].get('hits'), list) and \
            len(result['hits']['hits']) > 0 and \
            isinstance(result['hits']['hits'][0], dict) and \
            isinstance(result['hits']['hits'][0].get('_source'), dict) and \
            result['hits']['hits'][0]['_source']['pk_id']:
        weko_id = result['hits']['hits'][0]['_source']['pk_id']
    return weko_id


def get_list_file_by_record_id(recid):
    """Get Author_id by list name.

        Arguments:
            recid     -- {number} record id

        Returns:
            list_file  -- list file name of record

    """

    body = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "_id": recid
                    }
                }
            }
        },
        "_source": ["file"],
        "size": 1
    }
    indexer = RecordIndexer()
    result = indexer.client.search(
        index=current_app.config['INDEXER_DEFAULT_INDEX'],
        body=body
    )
    list_file_name = []

    if isinstance(result, dict) and isinstance(result.get('hits'), dict) and \
            isinstance(result['hits'].get('hits'), list) and \
            len(result['hits']['hits']) > 0 and \
            isinstance(result['hits']['hits'][0], dict) and \
            isinstance(result['hits']['hits'][0].get('_source'), dict) and \
            isinstance(result['hits']['hits'][0]['_source'].get('file'), dict) \
            and result['hits']['hits'][0]['_source']['file'].get('URI'):
        list_file = result['hits']['hits'][0]['_source']['file'].get('URI')

        list_file_name = [
            recid + '/' + item.get('value') for item in list_file]
    return list_file_name


def get_metadata_by_list_id(list_id=[]):
    """Get Author_id by list name.

        Arguments:
            list_id     -- {string} list Id record

        Returns:
            result       -- list_metadata of record has id in list_id

    """
    query_should = [
        {
            "match": {
                "control_number": rec_id
            }
        } for rec_id in list_id]

    body = {
        "query": {
            "bool": {
                "should": query_should
            }
        },
        "_source": ["_item_metadata"]
    }
    indexer = RecordIndexer()
    result = indexer.client.search(
        index=current_app.config['INDEXER_DEFAULT_INDEX'],
        body=body
    )
    list_metadata = []

    if isinstance(result, dict) and isinstance(result.get('hits'), dict) and \
            isinstance(result['hits'].get('hits'), list):
        list_source = result['hits'].get('hits')

        list_metadata = [
            item.get('_source').get("_item_metadata")
            for item in list_source
            if (isinstance(item.get('_source'), dict) and isinstance(item.get(
                '_source').get("_item_metadata"), dict))
        ]
    return list_metadata
