import json

from catmaid.models import Connector, TreenodeConnector
from catmaid.state import make_nocheck_state

from .common import CatmaidApiTestCase


class ConnectorsApiTests(CatmaidApiTestCase):
    def test_list_connector_types(self):
        self.fake_authentication()
        response = self.client.get('/%d/connectors/types/' % self.test_project_id)
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
            {
                'name': 'Presynaptic',
                'relation': 'presynaptic_to',
                'relation_id': 1023,
                'type': 'Synaptic'
            },
            {
                'name': 'Postsynaptic',
                'relation': 'postsynaptic_to',
                'relation_id': 1024,
                'type': 'Synaptic'
            },
            {
                'name': 'Abutting',
                'relation': 'abutting',
                'relation_id': 102461,
                'type': 'Abutting'
            },
            {
                'name': 'Gap junction',
                'relation': 'gapjunction_with',
                'relation_id': 1025,
                'type': 'Gap junction'
            }]


        self.assertListEqual(expected_result, parsed_response)


    def test_list_connector_empty(self):
        self.fake_authentication()
        response = self.client.get(
                '/%d/connectors/' % self.test_project_id, {
                    'relation_type': 'presynaptic_to',
                    'skeleton_ids': [0]})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = {
            'links': [],
            'tags': {}
        }
        self.assertEqual(expected_result, parsed_response)


    def test_list_connector_outgoing_with_sorting(self):
        self.fake_authentication()
        response = self.client.get(
                '/%d/connectors/' % self.test_project_id, {
                    'relation_type': 'presynaptic_to',
                    'skeleton_ids': [235]})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = {
          'links': [
            [235, 356, 6730.0, 2700.0, 0.0, 5, 3, 285, u'2011-12-20T10:46:01.360000+00:00'],
            [235, 421, 6260.0, 3990.0, 0.0, 5, 3, 415, u'2011-12-20T10:46:01.360000+00:00'],
            [235, 432, 2640.0, 3450.0, 0.0, 5, 3, 247, u'2011-12-20T10:46:01.360000+00:00']
           ],
           'tags': {
             '432': ['synapse with more targets', 'TODO']
            }
        }
        self.assertEqual(expected_result, parsed_response)


    def test_list_connector_incoming_with_connecting_skeletons(self):
        self.fake_authentication()
        response = self.client.get(
                '/%d/connectors/' % self.test_project_id, {
                    'relation_type': 'postsynaptic_to',
                    'skeleton_ids': [373]})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = {
                u'tags': {},
                u'links': [
                    [373, 356, 6730.00, 2700.00, 0.0, 5, 3, 377, u'2011-12-20T10:46:01.360000+00:00'],
                    [373, 421, 6260.00, 3990.00, 0.0, 5, 3, 409, u'2011-12-20T10:46:01.360000+00:00']]}
        self.assertEqual(expected_result, parsed_response)


    def test_one_to_many_skeletons_connector_list(self):
        self.fake_authentication()
        response = self.client.post(
                '/%d/connector/list/one_to_many' % self.test_project_id, {
                    'skid': 373,
                    'skids[0]': 235,
                    'relation': 'presynaptic_to'
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = []

        self.assertEqual(expected_result, parsed_response)

        response = self.client.post(
                '/%d/connector/list/one_to_many' % self.test_project_id, {
                    'skid': 373,
                    'skids[0]': 235,
                    'relation': 'postsynaptic_to'
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [[356, [6730.0, 2700.0, 0.0],
                            377, 373, 5, 3, [7620.0, 2890.0, 0.0],
                            285, 235, 5, 3, [6100.0, 2980.0, 0.0]],
                           [421, [6260.0, 3990.0, 0.0],
                            409, 373, 5, 3, [6630.0, 4330.0, 0.0],
                            415, 235, 5, 3, [5810.0, 3950.0, 0.0]]]
        self.assertEqual(expected_result, parsed_response)


    def test_many_to_many_skeletons_connector_list(self):
        self.fake_authentication()
        response = self.client.post(
                '/%d/connector/list/many_to_many' % self.test_project_id, {
                    'skids1[0]': 373,
                    'skids2[0]': 235,
                    'relation': 'presynaptic_to'
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = []

        self.assertEqual(expected_result, parsed_response)

        response = self.client.post(
                '/%d/connector/list/many_to_many' % self.test_project_id, {
                    'skids1[0]': 373,
                    'skids2[0]': 235,
                    'relation': 'postsynaptic_to'
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [[356, [6730.0, 2700.0, 0.0],
                            377, 373, 5, 3, [7620.0, 2890.0, 0.0],
                            285, 235, 5, 3, [6100.0, 2980.0, 0.0]],
                           [421, [6260.0, 3990.0, 0.0],
                            409, 373, 5, 3, [6630.0, 4330.0, 0.0],
                            415, 235, 5, 3, [5810.0, 3950.0, 0.0]]]
        self.assertEqual(expected_result, parsed_response)


    def test_connector_skeletons(self):
        self.fake_authentication()

        response = self.client.post(
                '/%d/connector/skeletons' % self.test_project_id, {
                    'connector_ids[0]': 356,
                    'connector_ids[1]': 2463
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
            [356, {
                'presynaptic_to': 235,
                'presynaptic_to_node': 285,
                'postsynaptic_to': [361, 373],
                'postsynaptic_to_node': [367, 377]
            }],
            [2463, {
                'presynaptic_to': 2462,
                'presynaptic_to_node': 2462,
                'postsynaptic_to': [2462],
                'postsynaptic_to_node': [2461]
            }],
        ]
        self.assertEqual(len(expected_result), len(parsed_response))
        self.assertItemsEqual(expected_result, parsed_response)


    def test_create_connector(self):
        self.fake_authentication()
        connector_count = Connector.objects.all().count()
        response = self.client.post(
                '/%d/connector/create' % self.test_project_id,
                {'x': 111, 'y': 222, 'z': 333, 'confidence': 3})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        self.assertTrue('connector_id' in parsed_response.keys())
        connector_id = parsed_response['connector_id']

        new_connector = Connector.objects.filter(id=connector_id).get()
        self.assertEqual(111, new_connector.location_x)
        self.assertEqual(222, new_connector.location_y)
        self.assertEqual(333, new_connector.location_z)
        self.assertEqual(3, new_connector.confidence)
        self.assertEqual(connector_count + 1, Connector.objects.all().count())


    def test_delete_connector(self):
        self.fake_authentication()
        connector_id = 356
        connector = Connector.objects.get(id=connector_id)
        connector_count = Connector.objects.all().count()
        treenode_connector_count = TreenodeConnector.objects.all().count()
        response = self.client.post(
                '/%d/connector/delete' % self.test_project_id,
                {'connector_id': connector_id, 'state': make_nocheck_state()})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = {
                'message': u'Removed connector and class_instances',
                'connector_id': 356,
                'x': 6730.0,
                'y': 2700.0,
                'z': 0.0,
                'confidence': 5,
                'partners': [{
                    'id': 285,
                    'link_id': 360,
                    'rel': 'presynaptic_to',
                    'rel_id': 1023,
                    'confidence': 5,
                    'edition_time': '2011-12-04T13:51:36.955Z',
                },{
                    'id': 367,
                    'link_id': 372,
                    'rel': 'postsynaptic_to',
                    'rel_id': 1024,
                    'confidence': 5,
                    'edition_time': '2011-12-05T13:51:36.955Z',
                }, {
                    'id': 377,
                    'link_id': 382,
                    'rel': 'postsynaptic_to',
                    'rel_id': 1024,
                    'confidence': 5,
                    'edition_time': '2011-12-05T13:51:36.955Z',
                }]
        }


        self.assertEqual(expected_result, parsed_response)

        self.assertEqual(connector_count - 1, Connector.objects.all().count())
        self.assertEqual(treenode_connector_count - 3, TreenodeConnector.objects.all().count())
        self.assertEqual(0, Connector.objects.filter(id=connector_id).count())
        self.assertEqual(0, TreenodeConnector.objects.filter(connector=connector).count())


    def test_connector_info(self):
        self.fake_authentication()
        response = self.client.post(
                '/%d/connector/info' % self.test_project_id,
                {'pre[0]': 235, 'post[0]': 373})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
                [356, [6730.0, 2700.0, 0.0],
                 285, 235, 5, 3, [6100.0, 2980.0, 0.0],
                 377, 373, 5, 3, [7620.0, 2890.0, 0.0]],
                [421, [6260.0, 3990.0, 0.0],
                 415, 235, 5, 3, [5810.0, 3950.0, 0.0],
                 409, 373, 5, 3, [6630.0, 4330.0, 0.0]]]
        self.assertEqual(expected_result, parsed_response)

        response = self.client.post(
                '/%d/connector/info' % self.test_project_id,
                {'pre[0]': 235, 'post[0]': 373, 'cids[0]': 421})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
                [421, [6260.0, 3990.0, 0.0],
                 415, 235, 5, 3, [5810.0, 3950.0, 0.0],
                 409, 373, 5, 3, [6630.0, 4330.0, 0.0]]]
        self.assertEqual(expected_result, parsed_response)

        response = self.client.post(
                '/%d/connector/info' % self.test_project_id,
                {'pre[0]': 2462, 'post[0]': 2468})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
                [2466, [6420.0, 5565.0, 0.0],
                 2462, 2462, 5, 3, [6685.0, 5395.0, 0.0],
                 2464, 2468, 5, 3, [6485.0, 5915.0, 0.0]]]

        self.assertEqual(expected_result, parsed_response)

        response = self.client.post(
                '/%d/connector/info' % self.test_project_id,
                {'pre[0]': 2462, 'post[0]': 2462})
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [
                [2463, [7135.0, 5065.0, 0.0],
                 2462, 2462, 5, 3, [6685.0, 5395.0, 0.0],
                 2461, 2462, 5, 3, [7680.0, 5345.0, 0.0]]]

        self.assertEqual(expected_result, parsed_response)


    def test_connector_detail(self):
        self.fake_authentication()
        response = self.client.get(
                '/%d/connectors/%d/' % (self.test_project_id, 421))
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = {
                'partners': [
                    {
                        'confidence': 5,
                        'skeleton_id': 235,
                        'link_id': 425,
                        'relation_name': 'presynaptic_to',
                        'relation_id': 1023,
                        'partner_id': 415},
                    {
                        'confidence': 5,
                        'skeleton_id': 373,
                        'link_id': 429,
                        'relation_name': 'postsynaptic_to',
                        'relation_id': 1024,
                        'partner_id': 409}
                ],
                'confidence': 5,
                'connector_id': 421,
                'y': 3990.0,
                'x': 6260.0,
                'z': 0.0}

        self.assertEqual(expected_result, parsed_response)


    def test_connector_user_info(self):
        self.fake_authentication()
        response = self.client.get(
                '/%d/connector/user-info' % (self.test_project_id,), {
                    'treenode_id': 415,
                    'connector_id': 421,
                    'relation_name': 'presynaptic_to'
                })
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        expected_result = [{
                'creation_time': '2011-10-07T07:02:22.656000+00:00',
                'user': 3,
                'edition_time': '2011-12-20T10:46:01.360000+00:00'}]

        self.assertEqual(expected_result, parsed_response)
