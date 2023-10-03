
def get_last_status_codes(checks):
    result = {}

    for item in checks:
        id = item['id']
        url_id = item['url_id']

        if url_id not in result or result.get(url_id, {}).get('id', -1) < id:
            result[url_id] = {
                'id': id,
                'status_code': item['status_code'],
                'created_at': item['created_at']
            }

    return result

