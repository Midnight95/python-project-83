
def test_request_example(client):
    """
    Test if the client is running
    """
    response = client.get("/")
    string = "Анализатор страниц"
    bytes_data = string.encode('utf-8')
    assert bytes_data in response.data
