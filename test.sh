http http://localhost:8000/new_message author=alice data=hello
http http://localhost:8000/commit
http http://localhost:5000/add_peer 'peers:=["localhost:8000"]'
