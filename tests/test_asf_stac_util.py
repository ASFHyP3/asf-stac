from datetime import datetime, timezone

import asf_stac_util


def test_jsonify_stac_item():
    assert asf_stac_util.jsonify_stac_item(
        {
            'str_field': 'foo',
            'int_field': 5,
            'float_field': 3.1,
            'bool_field': True,
            'null_field': None,
            'dict_field': {'str_field': 'bar'},
            'list_field': [[1, 2], [3, 4]],
            'tuple_field': ((1, 2), (3, 4)),
            'datetime_field': datetime(2022, 11, 30, 12, tzinfo=timezone.utc),
        }
    ) == (
        '{"str_field": "foo", "int_field": 5, "float_field": 3.1, "bool_field": true, "null_field": null, '
        '"dict_field": {"str_field": "bar"}, "list_field": [[1, 2], [3, 4]], "tuple_field": [[1, 2], [3, 4]], '
        '"datetime_field": "2022-11-30T12:00:00Z"}'
    )
