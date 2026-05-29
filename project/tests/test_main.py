from main import add, greet, slow_function

def test_add():
    assert add(2, 3) == 5

def test_greet_injection():
    assert greet("<script>alert('XSS')</script>") == "Hello, scriptalertXSSscript!"
